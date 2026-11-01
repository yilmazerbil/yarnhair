"""YarnHair graphical interface (PySide6)."""
import datetime
import gc
import json
import multiprocessing
import os
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed

from PySide6.QtCore import Qt, QObject, QTimer, Signal, QSettings, QLocale
from PySide6.QtGui import QAction, QActionGroup, QColor, QBrush
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QScrollArea, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QDoubleSpinBox, QSpinBox, QComboBox, QRadioButton, QButtonGroup, QTabWidget,
    QProgressBar, QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QTextBrowser)

from .. import __version__
from ..i18n import detect_lang
from ..measure import DEFAULT_CONFIG
from ..fibres import (FIBRES, OTHER, SOURCES as FIBRE_SOURCES, SOURCE_SHORT, SOURCE_PENDING, fibre_name,
                      blend_density)
from ..packing import (DEFAULT_PACKING, COUNT_UNITS, SYSTEMS, SYSTEM_NAMES, DIAMETER_TYPES, REFERENCES,
                       REF_SOURCES, to_tex, theoretical_diameter_um, packing_from_diameter, check_packing)
from .texts import tr, fmt, fmt_dur
from .viewer import ImageView
from .calibration import CalibrationDialog
from .export import write_tsv, write_xlsx, summarise
from .tasks import process_frame

IMG_EXT = (".bmp", ".png", ".tif", ".tiff", ".jpg", ".jpeg")
COLORS = {"ok": "#1b7f3b", "notice": "#b36b00", "warning": "#c2410c", "error": "#c62828"}
REF_SHORT = {"erbil2022": "Erbil et al. 2022", "kilic2014": "Kilic et al. 2014", "demir2023": "Demir 2023",
             "eldessouki2016": "Eldessouki & Ibrahim 2016", "hearle1969": "Hearle et al. 1969"}


def num_item(value, nd, lang):
    it = QTableWidgetItem(fmt(value, nd, lang))
    it.setData(Qt.UserRole, float(value))
    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    return it


class Runner(QObject):
    """Runs the frames in worker processes; polled from the GUI thread.

    Python's automatic garbage collection is paused during a run: if it ran in
    the executor's helper thread it could delete Qt objects of the GUI thread.
    """
    frameDone = Signal(dict)
    allDone = Signal(int, int, bool)

    def __init__(self, jobs, workers, parent=None):
        super().__init__(parent)
        self.jobs, self.workers, self._stop = jobs, workers, False
        self.ok = self.fail = 0
        self.ex = None
        self.futs = {}
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.poll)

    def start(self):
        gc.collect()
        gc.disable()
        ctx = multiprocessing.get_context("spawn")
        self.ex = ProcessPoolExecutor(max_workers=self.workers, mp_context=ctx)
        self.futs = {self.ex.submit(process_frame, *j): j for j in self.jobs}
        self.timer.start()

    def stop(self):
        self._stop = True
        for f in list(self.futs):
            f.cancel()

    def poll(self):
        for f in [f for f in self.futs if f.done()]:
            j = self.futs.pop(f)
            if f.cancelled():
                continue
            try:
                r = f.result()
            except Exception as e:      # a worker process died (e.g. out of memory)
                r = dict(path=j[0], label=j[1], error=f"{type(e).__name__}: {e}")
            if "error" in r:
                self.fail += 1
            else:
                self.ok += 1
            self.frameDone.emit(r)
        if not self.futs:
            self.finish()

    def finish(self, wait=False):
        self.timer.stop()
        if self.ex is not None:
            self.ex.shutdown(wait=wait, cancel_futures=True)
            self.ex = None
        gc.enable()
        self.allDone.emit(self.ok, self.fail, self._stop)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("YarnHair", "YarnHair")
        self.lang = self.settings.value("lang", detect_lang(sys.argv[1:]))
        if self.lang not in ("en", "tr"):
            self.lang = "en"
        self.files = []          # [label, path]
        self.results = []        # dicts from process_frame
        self.runs = []           # settings of each run
        self.calib = None        # (um_per_px, length_um, pixels, file)
        self.tmpdir = tempfile.mkdtemp(prefix="yarnhair_")
        self.runner = None
        self.section_win = None      # cross-section window (YarnSection)
        self.phi_source = None       # text: where the packing density came from
        self._phi_from_sections = False
        self.resize(1400, 900)
        self.build_ui()

    # ------------------------------------------------------------------ UI
    def t(self, key, **kw):
        return tr(key, self.lang, **kw)

    def build_ui(self, state=None):
        self._building = True
        loc = (QLocale(QLocale.Turkish, QLocale.Turkey) if self.lang == "tr"
               else QLocale(QLocale.English, QLocale.UnitedStates))
        loc.setNumberOptions(QLocale.OmitGroupSeparator)
        QLocale.setDefault(loc)
        self.setLocale(loc)
        self.setWindowTitle(self.t("app_title", v=__version__))
        self.build_menus()
        split = QSplitter(Qt.Horizontal)
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.addWidget(self.build_images())
        lv.addWidget(self.build_pixel())
        lv.addWidget(self.build_yarn())
        lv.addWidget(self.build_run())
        lv.addStretch(1)
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setWidget(left)
        sa.setMinimumWidth(560)
        split.addWidget(sa)
        split.addWidget(self.build_tabs())
        split.setStretchFactor(1, 1)
        self.setCentralWidget(split)
        if state:
            self.restore_state(state)
        else:
            self.add_fibre_row("cotton", 100.0)
        self._building = False
        self.refresh_files()
        self.update_boundary()
        self.refresh_results()

    def build_menus(self):
        mb = self.menuBar()
        mb.clear()
        m = mb.addMenu(self.t("menu_file"))
        for key, fn in (("act_add_images", self.add_images), ("act_add_folder", self.add_folder),
                        ("act_save", self.save_results)):
            a = QAction(self.t(key), self)
            a.triggered.connect(fn)
            m.addAction(a)
        m.addSeparator()
        a = QAction(self.t("act_quit"), self)
        a.triggered.connect(self.close)
        m.addAction(a)
        ml = mb.addMenu(self.t("menu_lang"))
        grp = QActionGroup(self)
        for code, name in (("en", "English"), ("tr", "Türkçe")):
            a = QAction(name, self)
            a.setCheckable(True)
            a.setChecked(code == self.lang)
            a.triggered.connect(lambda _=False, c=code: self.set_language(c))
            grp.addAction(a)
            ml.addAction(a)
        mt = mb.addMenu(self.t("menu_tools"))
        a = QAction(self.t("act_sections"), self)
        a.triggered.connect(self.open_sections)
        mt.addAction(a)
        mh = mb.addMenu(self.t("menu_help"))
        for key, fn in (("act_refs", self.show_refs), ("act_fibres", self.show_fibres), ("act_about", self.show_about)):
            a = QAction(self.t(key), self)
            a.triggered.connect(fn)
            mh.addAction(a)

    def build_images(self):
        g = QGroupBox(self.t("grp_images"))
        v = QVBoxLayout(g)
        row = QHBoxLayout()
        row.addWidget(QLabel(self.t("label")))
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText(self.t("label_hint"))
        row.addWidget(self.label_edit, 1)
        v.addLayout(row)
        self.sub_label = QCheckBox(self.t("sub_as_label"))
        self.sub_label.setChecked(self.settings.value("sub_label", "true") == "true")
        v.addWidget(self.sub_label)
        row = QHBoxLayout()
        for key, fn in (("btn_add_images", self.add_images), ("btn_add_folder", self.add_folder),
                        ("btn_remove", self.remove_selected), ("btn_clear", self.clear_files)):
            b = QPushButton(self.t(key))
            b.clicked.connect(fn)
            row.addWidget(b)
        v.addLayout(row)
        self.file_table = QTableWidget(0, 2)
        self.file_table.setHorizontalHeaderLabels([self.t("col_label"), self.t("col_file")])
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_table.setMinimumHeight(150)
        self.file_table.itemChanged.connect(self.file_label_edited)
        v.addWidget(self.file_table)
        self.n_files = QLabel("")
        v.addWidget(self.n_files)
        return g

    def build_pixel(self):
        g = QGroupBox(self.t("grp_pixel"))
        v = QVBoxLayout(g)
        row = QHBoxLayout()
        row.addWidget(QLabel(self.t("pixel_size")))
        self.pixel = QDoubleSpinBox()
        self.pixel.setRange(0.001, 1000)
        self.pixel.setDecimals(4)
        self.pixel.setValue(float(self.settings.value("pixel_um", 3.85)))
        self.pixel.setSuffix(" " + self.t("um_per_px"))
        self.pixel.valueChanged.connect(self.pixel_edited)
        row.addWidget(self.pixel)
        b = QPushButton(self.t("btn_calibrate"))
        b.clicked.connect(self.calibrate)
        row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)
        self.pixel_info = QLabel(self.t("pixel_manual"))
        self.pixel_info.setWordWrap(True)
        v.addWidget(self.pixel_info)
        return g

    def build_yarn(self):
        g = QGroupBox(self.t("grp_yarn"))
        v = QVBoxLayout(g)
        grid = QGridLayout()
        grid.addWidget(QLabel(self.t("count")), 0, 0)
        self.count = QDoubleSpinBox()
        self.count.setRange(0, 100000)
        self.count.setDecimals(2)
        self.count.setSpecialValueText("—")
        self.count.valueChanged.connect(self.update_boundary)
        self.unit = QComboBox()
        self.unit.addItems(list(COUNT_UNITS))
        self.unit.setCurrentText("Ne")
        self.unit.currentIndexChanged.connect(self.update_boundary)
        h = QHBoxLayout()
        h.addWidget(self.count)
        h.addWidget(self.unit)
        h.addStretch(1)
        grid.addLayout(h, 0, 1)
        grid.addWidget(QLabel(self.t("system")), 1, 0)
        self.system = QComboBox()
        for s in SYSTEMS:
            self.system.addItem(SYSTEM_NAMES[s][1 if self.lang == "tr" else 0], s)
        self.system.setCurrentIndex(SYSTEMS.index("ring"))
        self.system.currentIndexChanged.connect(self.update_boundary)
        grid.addWidget(self.system, 1, 1)
        v.addLayout(grid)

        v.addWidget(QLabel(self.t("blend")))
        self.blend = QTableWidget(0, 4)
        self.blend.setHorizontalHeaderLabels([self.t("col_fibre"), self.t("col_share"), self.t("col_density"),
                                              self.t("col_source")])
        hh = self.blend.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.Stretch)
        self.blend.setMinimumHeight(130)
        v.addWidget(self.blend)
        row = QHBoxLayout()
        b = QPushButton(self.t("btn_add_fibre"))
        b.clicked.connect(lambda: self.add_fibre_row("cotton", 0.0))
        row.addWidget(b)
        b = QPushButton(self.t("btn_del_fibre"))
        b.clicked.connect(self.remove_fibre_row)
        row.addWidget(b)
        self.blend_info = QLabel("")
        row.addWidget(self.blend_info, 1)
        v.addLayout(row)
        hint = QLabel(self.t("blend_hint"))
        hint.setStyleSheet("color: gray")
        hint.setWordWrap(True)
        v.addWidget(hint)

        self.mode_group = QButtonGroup(self)
        self.mode_theory = QRadioButton(self.t("mode_theory"))
        self.mode_measured = QRadioButton(self.t("mode_measured"))
        self.mode_group.addButton(self.mode_theory)
        self.mode_group.addButton(self.mode_measured)
        self.mode_theory.setChecked(True)
        self.mode_theory.toggled.connect(self.update_boundary)
        v.addWidget(self.mode_theory)
        grid = QGridLayout()
        grid.setContentsMargins(24, 0, 0, 0)
        grid.addWidget(QLabel(self.t("packing")), 0, 0)
        self.phi = QDoubleSpinBox()
        self.phi.setRange(0.05, 1.0)
        self.phi.setDecimals(3)
        self.phi.setSingleStep(0.01)
        self.phi.setValue(DEFAULT_PACKING)
        self.phi.valueChanged.connect(self.update_boundary)
        self.phi.valueChanged.connect(self.phi_edited)
        h = QHBoxLayout()
        h.addWidget(self.phi)
        b = QPushButton(self.t("btn_refs"))
        b.clicked.connect(self.show_refs)
        h.addWidget(b)
        b = QPushButton(self.t("btn_from_sections"))
        b.clicked.connect(self.open_sections)
        h.addWidget(b)
        h.addStretch(1)
        grid.addLayout(h, 0, 1)
        src = QLabel(self.t("packing_src"))
        src.setWordWrap(True)
        grid.addWidget(src, 1, 0, 1, 2)
        self.phi_src_label = QLabel(self.phi_source or "")
        self.phi_src_label.setWordWrap(True)
        self.phi_src_label.setStyleSheet("color: #1b7f3b; font-weight: bold")
        grid.addWidget(self.phi_src_label, 2, 0, 1, 2)
        self.theory_calc = QLabel("")
        self.theory_calc.setWordWrap(True)
        self.theory_calc.setTextInteractionFlags(Qt.TextSelectableByMouse)
        grid.addWidget(self.theory_calc, 3, 0, 1, 2)
        v.addLayout(grid)

        v.addWidget(self.mode_measured)
        grid = QGridLayout()
        grid.setContentsMargins(24, 0, 0, 0)
        grid.addWidget(QLabel(self.t("diameter")), 0, 0)
        self.dmeas = QDoubleSpinBox()
        self.dmeas.setRange(0, 100000)
        self.dmeas.setDecimals(1)
        self.dmeas.setSuffix(" µm")
        self.dmeas.setSpecialValueText("—")
        self.dmeas.valueChanged.connect(self.update_boundary)
        grid.addWidget(self.dmeas, 0, 1)
        grid.addWidget(QLabel(self.t("dtype")), 1, 0)
        self.dtype = QComboBox()
        for d in DIAMETER_TYPES:
            self.dtype.addItem(self.t("dtype_" + d), d)
        self.dtype.currentIndexChanged.connect(self.update_boundary)
        grid.addWidget(self.dtype, 1, 1)
        self.measured_calc = QLabel("")
        self.measured_calc.setWordWrap(True)
        grid.addWidget(self.measured_calc, 2, 0, 1, 2)
        v.addLayout(grid)

        self.check_label = QLabel("")
        self.check_label.setWordWrap(True)
        v.addWidget(self.check_label)
        note = QLabel(self.t("boundary_note"))
        note.setWordWrap(True)
        note.setStyleSheet("color: gray")
        v.addWidget(note)
        return g

    def build_run(self):
        g = QGroupBox(self.t("grp_run"))
        v = QVBoxLayout(g)
        row = QHBoxLayout()
        row.addWidget(QLabel(self.t("workers")))
        self.workers = QSpinBox()
        n = os.cpu_count() or 1
        self.workers.setRange(1, n)
        self.workers.setValue(min(int(self.settings.value("workers", min(2, n))), n))
        row.addWidget(self.workers)
        hint = QLabel(self.t("workers_hint"))
        hint.setStyleSheet("color: gray")
        row.addWidget(hint, 1)
        v.addLayout(row)
        row = QHBoxLayout()
        self.save_ov = QCheckBox(self.t("save_overlays"))
        self.save_ov.setChecked(self.settings.value("save_ov", "false") == "true")
        row.addWidget(self.save_ov)
        self.ov_dir = QLineEdit(self.settings.value("ov_dir", ""))
        row.addWidget(self.ov_dir, 1)
        b = QPushButton(self.t("btn_choose"))
        b.clicked.connect(self.choose_ov_dir)
        row.addWidget(b)
        v.addLayout(row)
        row = QHBoxLayout()
        self.btn_start = QPushButton(self.t("btn_start"))
        self.btn_start.setStyleSheet("font-weight: bold")
        self.btn_start.clicked.connect(self.start)
        self.btn_stop = QPushButton(self.t("btn_stop"))
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop)
        row.addWidget(self.btn_start)
        row.addWidget(self.btn_stop)
        v.addLayout(row)
        self.progress = QProgressBar()
        v.addWidget(self.progress)
        self.status = QLabel(self.t("status_ready"))
        self.status.setWordWrap(True)
        v.addWidget(self.status)
        return g

    def build_tabs(self):
        tabs = QTabWidget()
        w = QWidget()
        v = QVBoxLayout(w)
        note = QLabel(self.t("res_note"))
        note.setStyleSheet("color: gray")
        v.addWidget(note)
        self.res_table = QTableWidget(0, 12)
        self.res_table.setHorizontalHeaderLabels([self.t(k) for k in (
            "h_label", "h_frame", "h_N", "h_L", "h_N05", "h_N1", "h_N2", "h_N3", "h_mlen", "h_unres", "h_app", "h_bnd")])
        self.res_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.res_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.res_table.setSortingEnabled(True)
        self.res_table.cellDoubleClicked.connect(self.show_overlay_row)
        v.addWidget(self.res_table)
        row = QHBoxLayout()
        b = QPushButton(self.t("act_save"))
        b.clicked.connect(self.save_results)
        row.addWidget(b)
        b = QPushButton(self.t("btn_clear"))
        b.clicked.connect(self.clear_results)
        row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)
        tabs.addTab(w, self.t("tab_results"))

        self.sum_table = QTableWidget(0, 7)
        self.sum_table.setHorizontalHeaderLabels([self.t(k) for k in (
            "h_label", "h_n", "h_N", "h_L", "h_N1", "h_mlen", "h_app")])
        self.sum_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sum_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabs.addTab(self.sum_table, self.t("tab_summary"))

        w = QWidget()
        v = QVBoxLayout(w)
        row = QHBoxLayout()
        self.ov_combo = QComboBox()
        self.ov_combo.currentIndexChanged.connect(self.show_overlay_index)
        row.addWidget(self.ov_combo, 1)
        b = QPushButton(self.t("btn_fit"))
        row.addWidget(b)
        v.addLayout(row)
        self.ov_view = ImageView()
        b.clicked.connect(self.ov_view.fit)
        v.addWidget(self.ov_view, 1)
        leg = QLabel(self.t("ov_legend"))
        leg.setWordWrap(True)
        leg.setStyleSheet("color: gray")
        v.addWidget(leg)
        tabs.addTab(w, self.t("tab_overlay"))
        self.tabs = tabs
        return tabs

    # ------------------------------------------------------------ language
    def capture_state(self):
        return dict(
            files=[list(f) for f in self.files], label=self.label_edit.text(), pixel=self.pixel.value(),
            calib=self.calib, count=self.count.value(), unit=self.unit.currentText(),
            system=self.system.currentData(), blend=self.blend_rows(), theory=self.mode_theory.isChecked(),
            phi=self.phi.value(), dmeas=self.dmeas.value(), dtype=self.dtype.currentData(),
            workers=self.workers.value(), save_ov=self.save_ov.isChecked(), ov_dir=self.ov_dir.text(),
            status=self.status.text(), progress=(self.progress.value(), self.progress.maximum()))

    def restore_state(self, s):
        self.files = s["files"]
        self.label_edit.setText(s["label"])
        self.pixel.blockSignals(True)
        self.pixel.setValue(s["pixel"])
        self.pixel.blockSignals(False)
        self.calib = s["calib"]
        self.show_pixel_info()
        self.count.setValue(s["count"])
        self.unit.setCurrentText(s["unit"])
        self.system.setCurrentIndex(SYSTEMS.index(s["system"]))
        for key, share, dens in s["blend"]:
            self.add_fibre_row(key, share, dens)
        (self.mode_theory if s["theory"] else self.mode_measured).setChecked(True)
        self.phi.setValue(s["phi"])
        self.dmeas.setValue(s["dmeas"])
        self.dtype.setCurrentIndex(DIAMETER_TYPES.index(s["dtype"]))
        self.workers.setValue(s["workers"])
        self.save_ov.setChecked(s["save_ov"])
        self.ov_dir.setText(s["ov_dir"])
        self.progress.setMaximum(max(1, s["progress"][1]))
        self.progress.setValue(s["progress"][0])

    def set_language(self, code):
        if code == self.lang:
            return
        if self.runner is not None:
            return
        state = self.capture_state()
        self.lang = code
        self.settings.setValue("lang", code)
        self.build_ui(state)
        gc.collect()        # remove the old widgets now, in the GUI thread

    # --------------------------------------------------------------- files
    def start_dir(self):
        return self.settings.value("last_dir", os.path.expanduser("~"))

    def add_images(self):
        fs, _ = QFileDialog.getOpenFileNames(self, self.t("act_add_images"), self.start_dir(), self.t("img_filter"))
        if fs:
            self.settings.setValue("last_dir", os.path.dirname(fs[0]))
            lab = self.label_edit.text().strip()
            for f in sorted(fs):
                self.files.append([lab, f])
            self.refresh_files()

    def add_folder(self):
        d = QFileDialog.getExistingDirectory(self, self.t("act_add_folder"), self.start_dir())
        if not d:
            return
        self.settings.setValue("last_dir", d)
        self.settings.setValue("sub_label", "true" if self.sub_label.isChecked() else "false")
        self.files.extend(self.scan_folder(d, self.label_edit.text().strip(), self.sub_label.isChecked()))
        self.refresh_files()

    @staticmethod
    def scan_folder(d, label, sub_as_label):
        out = []
        for root, dirs, files in os.walk(d):
            dirs.sort()
            imgs = sorted(f for f in files if f.lower().endswith(IMG_EXT) and not f.startswith("."))
            if not imgs:
                continue
            lab = label
            if sub_as_label and os.path.abspath(root) != os.path.abspath(d):
                lab = os.path.relpath(root, d).replace(os.sep, "/")
            out.extend([lab, os.path.join(root, f)] for f in imgs)
        return out

    def remove_selected(self):
        rows = sorted({i.row() for i in self.file_table.selectedIndexes()}, reverse=True)
        for r in rows:
            del self.files[r]
        self.refresh_files()

    def clear_files(self):
        self.files = []
        self.refresh_files()

    def refresh_files(self):
        t = self.file_table
        t.blockSignals(True)
        t.setRowCount(len(self.files))
        for i, (lab, f) in enumerate(self.files):
            t.setItem(i, 0, QTableWidgetItem(lab))
            it = QTableWidgetItem(os.path.basename(f))
            it.setToolTip(f)
            it.setFlags(it.flags() & ~Qt.ItemIsEditable)
            t.setItem(i, 1, it)
        t.blockSignals(False)
        self.n_files.setText(self.t("n_images", n=len(self.files)))

    def file_label_edited(self, item):
        if item.column() == 0 and item.row() < len(self.files):
            self.files[item.row()][0] = item.text().strip()

    # ---------------------------------------------------------- pixel size
    def calibrate(self):
        dlg = CalibrationDialog(self.lang, self.start_dir(), self)
        if dlg.exec() == QDialog.Accepted and dlg.result:
            self.calib = dlg.result
            self.pixel.blockSignals(True)
            self.pixel.setValue(dlg.result[0])
            self.pixel.blockSignals(False)
            self.show_pixel_info()

    def pixel_edited(self, *_):
        self.calib = None
        self.show_pixel_info()

    def show_pixel_info(self):
        if self.calib:
            s, L, p, f = self.calib
            self.pixel_info.setText(self.t("pixel_calc", L=fmt(L, 1, self.lang), p=fmt(p, 1, self.lang),
                                           s=fmt(s, 4, self.lang), f=os.path.basename(f)))
        else:
            self.pixel_info.setText(self.t("pixel_manual"))

    # ---------------------------------------------------------------- blend
    def add_fibre_row(self, key="cotton", share=0.0, density=None):
        t = self.blend
        r = t.rowCount()
        t.insertRow(r)
        cb = QComboBox()
        for k in FIBRES:
            cb.addItem(fibre_name(k, self.lang), k)
        cb.addItem(fibre_name(OTHER, self.lang), OTHER)
        sp = QDoubleSpinBox()
        sp.setRange(0, 100)
        sp.setDecimals(2)
        sp.setSuffix(" %")
        sp.setValue(share)
        ds = QDoubleSpinBox()
        ds.setRange(0.5, 3.0)
        ds.setDecimals(3)
        ds.setSingleStep(0.01)
        src = QLabel("")
        t.setCellWidget(r, 0, cb)
        t.setCellWidget(r, 1, sp)
        t.setCellWidget(r, 2, ds)
        t.setCellWidget(r, 3, src)
        cb.currentIndexChanged.connect(lambda _=0, row_cb=cb: self.fibre_changed(row_cb))
        sp.valueChanged.connect(self.update_boundary)
        ds.valueChanged.connect(self.update_boundary)
        cb.setCurrentIndex(cb.findData(key))
        self.fibre_changed(cb)
        if key == OTHER and density:
            ds.setValue(density)
        self.update_boundary()

    def fibre_changed(self, cb):
        t = self.blend
        for r in range(t.rowCount()):
            if t.cellWidget(r, 0) is cb:
                key = cb.currentData()
                ds, src = t.cellWidget(r, 2), t.cellWidget(r, 3)
                if key == OTHER:
                    ds.setEnabled(True)
                    src.setText("—")
                    src.setToolTip("")
                else:
                    name_en, name_tr, dens, skey, note = FIBRES[key]
                    ds.blockSignals(True)
                    ds.setValue(dens)
                    ds.blockSignals(False)
                    ds.setEnabled(False)
                    txt = SOURCE_SHORT[skey] + (f" ({note})" if note else "")
                    if skey in SOURCE_PENDING:
                        txt += " – " + self.t("pending")
                    src.setText(txt)
                    src.setToolTip(FIBRE_SOURCES[skey])
        self.update_boundary()

    def remove_fibre_row(self):
        t = self.blend
        r = t.currentRow()
        if r < 0:
            r = t.rowCount() - 1
        if r >= 0 and t.rowCount() > 1:
            t.removeRow(r)
            self.update_boundary()

    def blend_rows(self):
        t = self.blend
        out = []
        for r in range(t.rowCount()):
            out.append((t.cellWidget(r, 0).currentData(), t.cellWidget(r, 1).value(), t.cellWidget(r, 2).value()))
        return out

    # ------------------------------------------------------------- boundary
    def boundary(self):
        """Current boundary settings and checks."""
        lang = self.lang
        b = dict(theory=self.mode_theory.isChecked(), tex=None, rho=None, phi_in=self.phi.value(),
                 dmeas=self.dmeas.value(), dtype=self.dtype.currentData(), system=self.system.currentData(),
                 d=None, phi=None, check=None, errors=[])
        if self.count.value() > 0:
            b["tex"] = to_tex(self.count.value(), self.unit.currentText())
        rows = self.blend_rows()
        total = sum(s for _, s, _ in rows)
        b["blend_total"] = total
        if abs(total - 100) < 0.01:
            b["rho"] = blend_density([(s, d) for _, s, d in rows])
        if b["theory"]:
            if b["tex"] is None:
                b["errors"].append(self.t("need_count"))
            if b["rho"] is None:
                b["errors"].append(self.t("blend_bad"))
            if not b["errors"]:
                b["d"] = theoretical_diameter_um(b["tex"], b["rho"], b["phi_in"])
                b["phi"] = b["phi_in"]
                b["check"] = check_packing(b["phi"], "cross_section", b["system"])
        else:
            if b["dmeas"] > 0:
                b["d"] = b["dmeas"]
                if b["tex"] is not None and b["rho"] is not None:
                    b["phi"] = packing_from_diameter(b["tex"], b["rho"], b["dmeas"])
                    b["check"] = check_packing(b["phi"], b["dtype"], b["system"])
            else:
                b["errors"].append(self.t("need_diameter"))
        return b

    def check_text(self, c):
        lang = self.lang
        phi = fmt(c["phi"], 3, lang)
        lvl = c["level"]
        if lvl == "ok":
            if c["low"] is None:
                return self.t("chk_ok_noref", phi=phi)
            return self.t("chk_ok", phi=phi, low=fmt(c["low"], 2, lang), high=fmt(c["high"], 2, lang))
        if lvl == "notice":
            return self.t("chk_notice", phi=phi, low=fmt(c["low"], 2, lang), high=fmt(c["high"], 2, lang))
        return self.t("chk_" + lvl, phi=phi)

    def update_boundary(self, *_):
        if getattr(self, "_building", True):
            return
        lang = self.lang
        b = self.boundary()
        rows = self.blend_rows() if hasattr(self, "blend") else []
        txt = self.t("blend_total", s=fmt(b["blend_total"], 2, lang))
        if b["rho"] is not None:
            txt += "   " + self.t("blend_rho", r=fmt(b["rho"], 3, lang))
            self.blend_info.setStyleSheet("")
        else:
            txt += "   " + self.t("blend_bad")
            self.blend_info.setStyleSheet(f"color: {COLORS['error']}")
        self.blend_info.setText(txt)
        theory = b["theory"]
        for w in (self.phi,):
            w.setEnabled(theory)
        self.dmeas.setEnabled(not theory)
        self.dtype.setEnabled(not theory)
        if b["tex"] is not None and b["rho"] is not None:
            dth = theoretical_diameter_um(b["tex"], b["rho"], self.phi.value())
            self.theory_calc.setText(self.t("theory_calc", T=fmt(b["tex"], 2, lang), phi=fmt(self.phi.value(), 3, lang),
                                            rho=fmt(b["rho"], 3, lang), d=fmt(dth, 1, lang)))
        else:
            self.theory_calc.setText(self.t("need_count") if b["tex"] is None else self.t("blend_bad"))
        if not theory and b["dmeas"] > 0 and b["phi"] is not None:
            self.measured_calc.setText(self.t("measured_calc", T=fmt(b["tex"], 2, lang),
                                              d=fmt(b["dmeas"] / 1000, 4, lang), rho=fmt(b["rho"], 3, lang),
                                              phi=fmt(b["phi"], 3, lang)))
        elif not theory:
            self.measured_calc.setText(self.t("measured_nocalc"))
        else:
            self.measured_calc.setText("")
        c = b["check"]
        if c:
            self.check_label.setText(self.check_text(c))
            self.check_label.setStyleSheet(f"color: {COLORS[c['level']]}; font-weight: bold")
        elif b["errors"]:
            self.check_label.setText(" ".join(b["errors"]))
            self.check_label.setStyleSheet(f"color: {COLORS['error']}")
        else:
            self.check_label.setText("")

    # ------------------------------------------------------------------ run
    def choose_ov_dir(self):
        d = QFileDialog.getExistingDirectory(self, self.t("save_overlays"), self.ov_dir.text() or self.start_dir())
        if d:
            self.ov_dir.setText(d)
            self.save_ov.setChecked(True)

    def confirm_boundary(self, b):
        """Ask about unusual packing densities. Returns True to go on."""
        c = b["check"]
        if c is None or c["level"] == "ok":
            return True
        box = QMessageBox(self)
        box.setWindowTitle(self.t("dlg_check_title"))
        box.setIcon(QMessageBox.Critical if c["level"] == "error" else QMessageBox.Warning)
        box.setText(self.check_text(c))
        fix = box.addButton(self.t("btn_fix"), QMessageBox.RejectRole)
        if b["theory"]:
            go = None if c["level"] == "error" else box.addButton(self.t("btn_continue"), QMessageBox.AcceptRole)
            use_theory = None
        else:
            go = None if c["level"] == "error" else box.addButton(self.t("btn_use_measured"), QMessageBox.AcceptRole)
            use_theory = box.addButton(self.t("btn_use_theory", phi=fmt(self.phi.value(), 3, self.lang)),
                                       QMessageBox.ActionRole)
        box.setDefaultButton(fix)
        box.exec()
        clicked = box.clickedButton()
        if clicked is go and go is not None:
            return True
        if use_theory is not None and clicked is use_theory:
            self.mode_theory.setChecked(True)
            nb = self.boundary()
            return not nb["errors"] and self.confirm_boundary(nb)
        return False

    def start(self):
        if self.runner is not None:
            return
        if not self.files:
            QMessageBox.information(self, "YarnHair", self.t("no_images"))
            return
        b = self.boundary()
        if b["errors"] or b["d"] is None:
            QMessageBox.warning(self, "YarnHair", " ".join(b["errors"]) or self.t("need_count"))
            return
        if not self.confirm_boundary(b):
            return
        b = self.boundary()
        px = self.pixel.value()
        self.settings.setValue("pixel_um", px)
        self.settings.setValue("workers", self.workers.value())
        self.settings.setValue("save_ov", "true" if self.save_ov.isChecked() else "false")
        self.settings.setValue("ov_dir", self.ov_dir.text())
        out_dir = self.ov_dir.text() if (self.save_ov.isChecked() and self.ov_dir.text()) else self.tmpdir
        jobs = []
        for lab, f in self.files:
            base = os.path.splitext(os.path.basename(f))[0]
            name = f"{lab}_{base}".replace("/", "_") if lab else base
            jobs.append((f, lab, b["d"], px, os.path.join(out_dir, name + ".png")))
        self.runs.append(self.run_settings(b, px, [lab for lab, _ in self.files]))
        self.pending = list(self.files)
        self.done_paths = set()
        self.run_total = len(jobs)
        self.run_ok = 0
        self.run_seconds = []
        self.progress.setMaximum(len(jobs))
        self.progress.setValue(0)
        self.status.setText(self.t("status_running", done=0, total=len(jobs), eta="…"))
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.runner = Runner(jobs, self.workers.value(), self)
        self.runner.frameDone.connect(self.frame_done)
        self.runner.allDone.connect(self.run_done)
        self.runner.start()

    def stop(self):
        if self.runner is not None:
            self.runner.stop()
            self.btn_stop.setEnabled(False)

    def run_settings(self, b, px, labels):
        lang = self.lang
        blend = "; ".join(f"{fibre_name(k, lang)} {fmt(s, 2, lang)} % ({fmt(d, 3, lang)})"
                          for k, s, d in self.blend_rows())
        if self.calib:
            s, L, p, f = self.calib
            how = self.t("pixel_calc", L=fmt(L, 1, lang), p=fmt(p, 1, lang), s=fmt(s, 4, lang), f=os.path.basename(f))
        else:
            how = self.t("pixel_manual")
        return [
            (self.t("col_label"), ", ".join(sorted(set(labels)))),
            (self.t("set_pixel"), px), (self.t("set_pixel_how"), how),
            (self.t("set_count"), f"{fmt(self.count.value(), 2, lang)} {self.unit.currentText()}"),
            (self.t("set_tex"), b["tex"]), (self.t("set_system"), self.system.currentText()),
            (self.t("set_blend"), blend), (self.t("set_rho"), b["rho"]),
            (self.t("set_mode"), self.t("mode_theory") if b["theory"] else self.t("mode_measured")),
            (self.t("set_phi"), b["phi"]),
            (self.t("set_phi_src"), (self.phi_source or self.t("phi_src_hand")) if b["theory"] else ""),
            (self.t("set_dtype"), "" if b["theory"] else self.dtype.currentText()),
            (self.t("set_d"), b["d"]),
            (self.t("set_config"), json.dumps(DEFAULT_CONFIG)),
        ]

    def frame_done(self, r):
        self.done_paths.add(r["path"])
        self.progress.setValue(len(self.done_paths))
        if "error" in r:
            self.status.setText(self.t("frame_failed", f=os.path.basename(r["path"]), e=r["error"]))
        else:
            self.results.append(r)
            k = len(self.results) - 1
            self.run_ok += 1
            self.run_seconds.append(r["seconds"])
            self.add_result_row(r, k)
            self.refresh_summary()
            self.ov_combo.addItem(f"{r['label']} – {os.path.basename(r['path'])}", k)
            if self.ov_combo.count() == 1:
                self.show_overlay_index(0)
            left = self.run_total - len(self.done_paths)
            avg = sum(self.run_seconds) / len(self.run_seconds)
            eta = fmt_dur(left * avg / max(1, self.workers.value()), self.lang)
            self.status.setText(self.t("status_running", done=len(self.done_paths), total=self.run_total, eta=eta))

    def run_done(self, ok, fail, stopped):
        self.runner.deleteLater()
        self.runner = None
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        # processed images leave the list; the rest stay for the next run
        self.files = [f for f in self.files if f[1] not in self.done_paths]
        self.refresh_files()
        msg = self.t("status_done", ok=ok, fail=fail)
        if stopped:
            msg = self.t("status_stopped") + " " + msg
        self.status.setText(msg)

    # -------------------------------------------------------------- results
    def add_result_row(self, r, k):
        lang = self.lang
        t = self.res_table
        t.setSortingEnabled(False)
        i = t.rowCount()
        t.insertRow(i)
        it = QTableWidgetItem(r["label"])
        it.setData(Qt.UserRole + 1, k)
        t.setItem(i, 0, it)
        t.setItem(i, 1, QTableWidgetItem(os.path.basename(r["path"])))
        vals = [(r["N"], 1), (r["L"], 1), (r["N05"], 1), (r["N1"], 1), (r["N2"], 1), (r["N3"], 1),
                (r["mean_length"], 3), (r["unresolved"], 0),
                (r["apparent_diameter_px"] * r["pixel_um"], 0), (2 * r["boundary_radius_px"] * r["pixel_um"], 0)]
        for j, (v, nd) in enumerate(vals):
            t.setItem(i, 2 + j, num_item(v, nd, lang))
        t.setSortingEnabled(True)

    def refresh_results(self):
        self.res_table.setRowCount(0)
        self.ov_combo.blockSignals(True)
        self.ov_combo.clear()
        for k, r in enumerate(self.results):
            self.add_result_row(r, k)
            self.ov_combo.addItem(f"{r['label']} – {os.path.basename(r['path'])}", k)
        self.ov_combo.blockSignals(False)
        self.refresh_summary()
        if self.results:
            self.show_overlay_index(0)

    def refresh_summary(self):
        lang = self.lang
        s = summarise(self.results) if self.results else {}
        t = self.sum_table
        t.setRowCount(len(s))
        for i, (lab, d) in enumerate(s.items()):
            t.setItem(i, 0, QTableWidgetItem(lab))
            t.setItem(i, 1, num_item(d["n"], 0, lang))
            for j, (k, nd) in enumerate((("N", 1), ("L", 1), ("N1", 1), ("mean_length", 3), ("apparent_diameter_um", 0))):
                m, sd = d[k]
                txt = fmt(m, nd, lang) + ("" if sd != sd else " ± " + fmt(sd, nd, lang))
                it = QTableWidgetItem(txt)
                it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                t.setItem(i, 2 + j, it)

    def clear_results(self):
        if self.runner is not None:
            return
        self.results = []
        self.runs = []
        self.refresh_results()
        self.ov_view.clear()

    def show_overlay_row(self, row, _col):
        it = self.res_table.item(row, 0)
        k = it.data(Qt.UserRole + 1)
        idx = self.ov_combo.findData(k)
        if idx >= 0:
            self.ov_combo.setCurrentIndex(idx)
            self.show_overlay_index(idx)
        self.tabs.setCurrentIndex(2)

    def show_overlay_index(self, idx):
        if idx < 0 or idx >= self.ov_combo.count():
            return
        k = self.ov_combo.itemData(idx)
        p = self.results[k].get("overlay")
        if p and os.path.exists(p):
            self.ov_view.set_image(p)

    def save_results(self):
        if not self.results:
            QMessageBox.information(self, "YarnHair", self.t("no_results"))
            return
        f, flt = QFileDialog.getSaveFileName(self, self.t("act_save"),
                                             os.path.join(self.start_dir(), "yarnhair_results.xlsx"),
                                             self.t("save_filter"))
        if not f:
            return
        if not f.lower().endswith((".xlsx", ".tsv")):
            f += ".tsv" if "tsv" in flt else ".xlsx"
        try:
            self._write(f)
        except Exception as e:  # e.g. file open in Excel, openpyxl missing
            QMessageBox.critical(self, "YarnHair", f"{type(e).__name__}: {e}")
            return
        self.status.setText(self.t("saved", p=f))

    def _write(self, f):
        if f.lower().endswith(".tsv"):
            write_tsv(f, self.results)
        else:
            settings = [(self.t("set_version"), __version__),
                        (self.t("set_date"), datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))]
            for i, run in enumerate(self.runs, 1):
                settings.append((f"— {i} —", ""))
                settings.extend(run)
            write_xlsx(f, self.results, settings, dict(frames=self.t("sheet_frames"),
                                                       summary=self.t("sheet_summary"),
                                                       settings=self.t("sheet_settings")))

    # -------------------------------------------------------------- dialogs
    def show_refs(self):
        lang = self.lang
        b = self.boundary()
        used = set(map(id, b["check"]["refs"])) if b["check"] else set()
        dlg = QDialog(self)
        dlg.setWindowTitle(self.t("refs_title"))
        dlg.resize(980, 640)
        v = QVBoxLayout(dlg)
        lab = QLabel(self.t("refs_intro"))
        lab.setWordWrap(True)
        v.addWidget(lab)
        t = QTableWidget(len(REFERENCES), 6)
        t.setHorizontalHeaderLabels([self.t(k) for k in ("h_kind", "h_system", "h_fibre", "h_tex", "h_phi", "h_src")])
        t.setEditTriggers(QAbstractItemView.NoEditTriggers)
        for i, ref in enumerate(REFERENCES):
            kind, system, fibre, tex, val, src, note = ref
            approx = "≈" if "approx" in note else ""
            cells = [self.t("kind_" + kind), SYSTEM_NAMES[system][1 if lang == "tr" else 0], fibre,
                     "" if tex is None else fmt(tex, 1, lang), approx + fmt(val, 3, lang),
                     REF_SHORT[src] + (f" ({note})" if note and "approx" not in note else "")]
            for j, c in enumerate(cells):
                it = QTableWidgetItem(c)
                if id(ref) in used:
                    it.setBackground(QBrush(QColor(255, 236, 179)))
                t.setItem(i, j, it)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        v.addWidget(t, 1)
        tb = QTextBrowser()
        tb.setHtml("<br>".join(REF_SOURCES[k] for k in REF_SHORT))
        tb.setMaximumHeight(130)
        v.addWidget(tb)
        bb = QDialogButtonBox(QDialogButtonBox.Close)
        bb.rejected.connect(dlg.reject)
        v.addWidget(bb)
        dlg.exec()

    def show_fibres(self):
        lang = self.lang
        dlg = QDialog(self)
        dlg.setWindowTitle(self.t("fibres_title"))
        dlg.resize(820, 560)
        v = QVBoxLayout(dlg)
        lab = QLabel(self.t("fibres_intro"))
        lab.setWordWrap(True)
        v.addWidget(lab)
        t = QTableWidget(len(FIBRES), 3)
        t.setHorizontalHeaderLabels([self.t("col_fibre"), self.t("col_density"), self.t("col_source")])
        t.setEditTriggers(QAbstractItemView.NoEditTriggers)
        for i, (k, (en, trn, dens, src, note)) in enumerate(FIBRES.items()):
            t.setItem(i, 0, QTableWidgetItem(trn if lang == "tr" else en))
            t.setItem(i, 1, num_item(dens, 2, lang))
            txt = SOURCE_SHORT[src] + (f" ({note})" if note else "")
            if src in SOURCE_PENDING:
                txt += " – " + self.t("pending")
            t.setItem(i, 2, QTableWidgetItem(txt))
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        v.addWidget(t, 1)
        tb = QTextBrowser()
        tb.setHtml("<br>".join(FIBRE_SOURCES.values()))
        tb.setMaximumHeight(130)
        v.addWidget(tb)
        bb = QDialogButtonBox(QDialogButtonBox.Close)
        bb.rejected.connect(dlg.reject)
        v.addWidget(bb)
        dlg.exec()

    def show_about(self):
        QMessageBox.about(self, self.t("act_about"), self.t("about_text", v=__version__))

    # ------------------------------------------------- cross-sections (YarnSection)
    def current_yarn(self):
        """Count and blend of step 3 for new labels of the cross-section window, or None."""
        b = self.boundary()
        if b["tex"] is None or b["rho"] is None:
            return None
        return dict(count=self.count.value(), unit=self.unit.currentText(), tex=b["tex"],
                    blend=[list(r) for r in self.blend_rows()], rho=b["rho"])

    def open_sections(self):
        from .section_window import SectionWindow
        if self.section_win is None:
            self.section_win = SectionWindow(lang=self.lang, link=self, default_yarn=self.current_yarn())
        else:
            self.section_win.default_yarn = self.current_yarn()
        self.section_win.show()
        self.section_win.raise_()
        self.section_win.activateWindow()

    def use_section_phi(self, phi, label, n, sd):
        """Called by the cross-section window: mean packing density of one label."""
        lang = self.lang
        self.mode_theory.setChecked(True)
        self._phi_from_sections = True
        self.phi.setValue(round(float(phi), 3))
        self._phi_from_sections = False
        self.phi_source = self.t("phi_src_sections", label=label, n=n, phi=fmt(phi, 3, lang),
                                 sd=fmt(sd, 3, lang) if sd == sd else "—")
        self.phi_src_label.setText(self.phi_source)
        self.update_boundary()

    def phi_edited(self, *_):
        if getattr(self, "_building", True) or self._phi_from_sections:
            return
        self.phi_source = None
        self.phi_src_label.setText("")

    def closeEvent(self, e):
        if self.section_win is not None and not self.section_win.close():
            e.ignore()
            return
        if self.runner is not None:
            self.runner.stop()
            self.runner.finish(wait=True)
        e.accept()


def main():
    multiprocessing.freeze_support()
    if "--selftest" in sys.argv[1:]:
        from .selftest import run
        return run()
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("YarnHair")
    w = MainWindow()
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
