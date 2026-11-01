"""YarnSection window: packing density from the outline of yarn cross-sections.

Runs on its own (program YarnSection) or as a window of YarnHair; in YarnHair
the mean packing density of a label can be passed to the boundary settings
(link.use_section_phi). The method is described in yarnhair/section.py.
"""
import datetime
import os
import sys

from PySide6.QtCore import Qt, QSettings, QLocale
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QScrollArea, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDoubleSpinBox, QTabWidget, QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QTextBrowser)

from .. import __version__
from ..i18n import detect_lang
from ..packing import DEFAULT_PACKING, theoretical_diameter_um
from ..section import (ASPECT_LIMIT, empty_project, evaluate, load_outlines, save_outlines, section_table,
                       section_values, suggest_outline, summary_table)
from .blend import YarnDialog, blend_text
from .calibration import CalibrationDialog
from .outline_view import OutlineView
from .texts import tr, fmt

IMG_EXT = (".bmp", ".png", ".tif", ".tiff", ".jpg", ".jpeg")
RED = "#c62828"
ORANGE = "#c2410c"


def _num(value, nd, lang):
    ok = value is not None and value == value and not isinstance(value, str)
    it = QTableWidgetItem(fmt(value, nd, lang) if ok else "—")
    if ok:
        it.setData(Qt.UserRole, float(value))
    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    it.setFlags(it.flags() & ~Qt.ItemIsEditable)
    return it


def _text(s):
    it = QTableWidgetItem(s)
    it.setFlags(it.flags() & ~Qt.ItemIsEditable)
    return it


def _isnum(x):
    return isinstance(x, (int, float)) and x == x


class SectionWindow(QMainWindow):
    def __init__(self, lang=None, link=None, default_yarn=None):
        super().__init__()
        self.settings = QSettings("YarnHair", "YarnSection")
        self.link = link                       # YarnHair main window, or None
        lang = lang or self.settings.value("lang", detect_lang(sys.argv[1:]))
        self.lang = lang if lang in ("en", "tr") else "en"
        self.default_yarn = default_yarn
        self.project = empty_project()
        self.project["pixel_um"] = float(self.settings.value("pixel_um", 1.0))
        self.project["pixel_how"] = ""
        self.current = -1
        self.outline_file = None
        self.dirty = False
        self.rows, self.summary = [], {}
        self._gray = (None, None)              # (path, array) for the outline suggestion
        self.resize(1450, 920)
        self.build_ui()

    def t(self, key, **kw):
        return tr(key, self.lang, **kw)

    # ------------------------------------------------------------------ UI
    def build_ui(self):
        self._building = True
        loc = (QLocale(QLocale.Turkish, QLocale.Turkey) if self.lang == "tr"
               else QLocale(QLocale.English, QLocale.UnitedStates))
        loc.setNumberOptions(QLocale.OmitGroupSeparator)
        self.setLocale(loc)
        self.setWindowTitle(self.t("s_title", v=__version__))
        self.build_menus()
        split = QSplitter(Qt.Horizontal)
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.addWidget(self.build_images())
        lv.addWidget(self.build_pixel())
        lv.addWidget(self.build_yarns())
        lv.addStretch(1)
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setWidget(left)
        sa.setMinimumWidth(600)
        split.addWidget(sa)
        right = QSplitter(Qt.Vertical)
        right.addWidget(self.build_viewer())
        right.addWidget(self.build_tabs())
        right.setStretchFactor(0, 3)
        right.setStretchFactor(1, 2)
        split.addWidget(right)
        split.setStretchFactor(1, 1)
        split.setSizes([620, 830])
        self.setCentralWidget(split)
        self._building = False
        self.refresh_all()
        if self.project["sections"]:
            self.select(min(max(self.current, 0), len(self.project["sections"]) - 1))

    def build_menus(self):
        mb = self.menuBar()
        mb.clear()
        m = mb.addMenu(self.t("menu_file"))
        for key, fn in (("act_add_images", self.add_images), ("act_add_folder", self.add_folder), (None, None),
                        ("s_act_open", self.open_outlines), ("s_act_save_outlines", self.save_outlines_as),
                        ("act_save", self.save_results), ("s_act_save_checks", self.save_checks), (None, None),
                        ("s_act_close", self.close)):
            if key is None:
                m.addSeparator()
                continue
            a = QAction(self.t(key), self)
            a.triggered.connect(fn)
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
        mh = mb.addMenu(self.t("menu_help"))
        for key, fn in (("s_act_method", self.show_method), ("s_act_about", self.show_about)):
            a = QAction(self.t(key), self)
            a.triggered.connect(fn)
            mh.addAction(a)

    def build_images(self):
        g = QGroupBox(self.t("s_grp_images"))
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
        self.img_table = QTableWidget(0, 4)
        self.img_table.setHorizontalHeaderLabels([self.t("col_label"), self.t("col_file"), self.t("s_col_phi"),
                                                  self.t("s_col_use")])
        hh = self.img_table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        self.img_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.img_table.setMinimumHeight(180)
        self.img_table.itemChanged.connect(self.image_item_changed)
        self.img_table.currentCellChanged.connect(self._cell_changed)
        v.addWidget(self.img_table)
        return g

    def build_pixel(self):
        g = QGroupBox(self.t("grp_pixel"))
        v = QVBoxLayout(g)
        row = QHBoxLayout()
        row.addWidget(QLabel(self.t("pixel_size")))
        self.pixel = QDoubleSpinBox()
        self.pixel.setRange(0.0001, 1000)
        self.pixel.setDecimals(4)
        self.pixel.setValue(self.project["pixel_um"] or 1.0)
        self.pixel.setSuffix(" " + self.t("um_per_px"))
        self.pixel.valueChanged.connect(self.pixel_edited)
        row.addWidget(self.pixel)
        b = QPushButton(self.t("btn_calibrate"))
        b.clicked.connect(self.calibrate)
        row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)
        self.pixel_info = QLabel(self.project.get("pixel_how") or self.t("pixel_manual"))
        self.pixel_info.setWordWrap(True)
        v.addWidget(self.pixel_info)
        return g

    def build_yarns(self):
        g = QGroupBox(self.t("s_grp_yarns"))
        v = QVBoxLayout(g)
        self.yarn_table = QTableWidget(0, 5)
        self.yarn_table.setHorizontalHeaderLabels([self.t("col_label"), self.t("s_col_count"), self.t("s_col_blend"),
                                                   self.t("s_col_rho"), self.t("s_col_af")])
        hh = self.yarn_table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        self.yarn_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.yarn_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.yarn_table.setMinimumHeight(140)
        self.yarn_table.cellDoubleClicked.connect(lambda r, _c: self.edit_yarn(r))
        v.addWidget(self.yarn_table)
        b = QPushButton(self.t("s_btn_edit_yarn"))
        b.clicked.connect(lambda: self.edit_yarn(self.yarn_table.currentRow()))
        row = QHBoxLayout()
        row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)
        return g

    def build_viewer(self):
        w = QWidget()
        v = QVBoxLayout(w)
        hint = QLabel(self.t("s_hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet("color: gray")
        v.addWidget(hint)
        row = QHBoxLayout()
        for key, fn in (("s_btn_prev", lambda: self.select(self.current - 1)),
                        ("s_btn_next", lambda: self.select(self.current + 1)),
                        ("s_btn_suggest", self.suggest), ("s_btn_undo", lambda: self.view.undo()),
                        ("s_btn_clear_outline", self.clear_outline), ("btn_fit", lambda: self.view.fit())):
            b = QPushButton(self.t(key))
            b.clicked.connect(fn)
            row.addWidget(b)
        self.use_box = QCheckBox(self.t("s_use"))
        self.use_box.setChecked(True)
        self.use_box.toggled.connect(self.use_toggled)
        row.addWidget(self.use_box)
        row.addStretch(1)
        v.addLayout(row)
        self.view = OutlineView()
        self.view.outlineChanged.connect(self.outline_changed)
        v.addWidget(self.view, 1)
        self.live = QLabel("")
        self.live.setWordWrap(True)
        self.live.setTextInteractionFlags(Qt.TextSelectableByMouse)
        v.addWidget(self.live)
        self.message = QLabel("")
        self.message.setWordWrap(True)
        v.addWidget(self.message)
        return w

    def build_tabs(self):
        tabs = QTabWidget()
        self.sec_table = QTableWidget(0, 12)
        self.sec_table.setHorizontalHeaderLabels([self.t(k) for k in (
            "h_label", "h_image", "h_pts", "h_area", "h_deq", "h_major", "h_minor", "h_aspect", "s_col_phi", "h_phim",
            "h_use", "h_note")])
        self.sec_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sec_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sec_table.cellDoubleClicked.connect(lambda r, _c: self.select(r))
        tabs.addTab(self.sec_table, self.t("s_tab_sections"))
        w = QWidget()
        v = QVBoxLayout(w)
        note = QLabel(self.t("s_sum_note"))
        note.setWordWrap(True)
        note.setStyleSheet("color: gray")
        v.addWidget(note)
        self.sum_table = QTableWidget(0, 9)
        self.sum_table.setHorizontalHeaderLabels([self.t(k) for k in (
            "h_label", "h_nsec", "h_phi_mean", "h_ci", "h_cv", "h_deq_mean", "h_aspect", "h_flagged", "h_dth")])
        self.sum_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sum_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sum_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        v.addWidget(self.sum_table, 1)
        if self.link is not None:
            row = QHBoxLayout()
            b = QPushButton(self.t("s_btn_use_phi"))
            b.setStyleSheet("font-weight: bold")
            b.clicked.connect(self.use_in_yarnhair)
            row.addWidget(b)
            row.addStretch(1)
            v.addLayout(row)
        tabs.addTab(w, self.t("s_tab_summary"))
        self.tabs = tabs
        return tabs

    def set_language(self, code):
        if code == self.lang:
            return
        self.lang = code
        self.settings.setValue("lang", code)
        self.build_ui()

    # -------------------------------------------------------------- images
    def start_dir(self):
        return self.settings.value("last_dir", os.path.expanduser("~"))

    def add_images(self):
        fs, _ = QFileDialog.getOpenFileNames(self, self.t("act_add_images"), self.start_dir(), self.t("img_filter"))
        if fs:
            self.settings.setValue("last_dir", os.path.dirname(fs[0]))
            self.add_files([[self.label_edit.text().strip(), f] for f in sorted(fs)])

    def add_folder(self):
        d = QFileDialog.getExistingDirectory(self, self.t("act_add_folder"), self.start_dir())
        if not d:
            return
        self.settings.setValue("last_dir", d)
        self.settings.setValue("sub_label", "true" if self.sub_label.isChecked() else "false")
        out = []
        for root, dirs, files in os.walk(d):
            dirs.sort()
            imgs = sorted(f for f in files if f.lower().endswith(IMG_EXT) and not f.startswith("."))
            lab = self.label_edit.text().strip()
            if self.sub_label.isChecked() and os.path.abspath(root) != os.path.abspath(d):
                lab = os.path.relpath(root, d).replace(os.sep, "/")
            out.extend([lab, os.path.join(root, f)] for f in imgs)
        self.add_files(out)

    def add_files(self, items):
        """items: [label, path]; adds sections without outline and selects the first new one."""
        if not items:
            return
        first = len(self.project["sections"])
        for lab, f in items:
            self.project["sections"].append(dict(label=lab, image=f, outline=[], use=True))
        self.ensure_yarns()
        self.mark_changed()
        self.refresh_all()
        self.select(first)

    def remove_selected(self):
        rows = sorted({i.row() for i in self.img_table.selectedIndexes()}, reverse=True)
        for r in rows:
            del self.project["sections"][r]
        if rows:
            self.current = min(self.current, len(self.project["sections"]) - 1)
            self.mark_changed()
            self.refresh_all()
            self.select(self.current)

    def clear_files(self):
        if not self.project["sections"]:
            return
        self.project["sections"] = []
        self.current = -1
        self.view.clear()
        self.mark_changed()
        self.refresh_all()

    def ensure_yarns(self):
        for s in self.project["sections"]:
            lab = s["label"]
            if lab not in self.project["yarns"] and self.default_yarn:
                self.project["yarns"][lab] = dict(self.default_yarn)

    def image_item_changed(self, item):
        r, c = item.row(), item.column()
        if self._building or r >= len(self.project["sections"]):
            return
        s = self.project["sections"][r]
        if c == 0:
            s["label"] = item.text().strip()
            self.ensure_yarns()
        elif c == 3:
            s["use"] = item.checkState() == Qt.Checked
            if r == self.current:
                self.use_box.blockSignals(True)
                self.use_box.setChecked(s["use"])
                self.use_box.blockSignals(False)
        else:
            return
        self.mark_changed()
        self.refresh_yarns()
        self.refresh_values()

    def _cell_changed(self, r, *_):
        if not self._building and r != self.current and r >= 0:
            self.select(r)

    def select(self, i):
        secs = self.project["sections"]
        if not secs:
            self.current = -1
            self.view.clear()
            self.update_live()
            return
        i = min(max(i, 0), len(secs) - 1)
        self.current = i
        s = secs[i]
        self.message.setText("")
        if os.path.exists(s["image"]):
            self.view.set_image(s["image"], s.get("outline", []))
        else:
            self.view.clear()
            self.message.setText(self.t("s_missing_image", p=s["image"]))
        self.use_box.blockSignals(True)
        self.use_box.setChecked(s.get("use", True))
        self.use_box.blockSignals(False)
        t = self.img_table
        if t.currentRow() != i:
            t.blockSignals(True)
            t.setCurrentCell(i, 1)
            t.blockSignals(False)
        self.update_live()

    # ------------------------------------------------------------- outline
    def outline_changed(self, pts):
        if self.current < 0:
            return
        self.project["sections"][self.current]["outline"] = [(float(x), float(y)) for x, y in pts]
        self.mark_changed()
        self.refresh_values()
        self.update_live()

    def clear_outline(self):
        if self.current >= 0:
            self.view.set_points([])

    def use_toggled(self, on):
        if self.current < 0:
            return
        self.project["sections"][self.current]["use"] = bool(on)
        it = self.img_table.item(self.current, 3)
        if it is not None:
            self._building = True
            it.setCheckState(Qt.Checked if on else Qt.Unchecked)
            self._building = False
        self.mark_changed()
        self.refresh_values()

    def expected_diameter_px(self, label):
        y = self.project["yarns"].get(label)
        px = self.project.get("pixel_um")
        if not y or not px:
            return None
        return theoretical_diameter_um(y["tex"], y["rho"], DEFAULT_PACKING) / px

    def suggest(self):
        if self.current < 0:
            return
        s = self.project["sections"][self.current]
        if not os.path.exists(s["image"]):
            return
        import numpy as np
        from PIL import Image
        if self._gray[0] != s["image"]:
            self._gray = (s["image"], np.asarray(Image.open(s["image"]).convert("L"), dtype=float))
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            pts = suggest_outline(self._gray[1], self.expected_diameter_px(s["label"]))
        finally:
            QApplication.restoreOverrideCursor()
        if pts is None:
            self.message.setText(self.t("s_suggest_none"))
        else:
            self.view.set_points(pts)
            self.message.setText(self.t("s_suggest_done"))

    def update_live(self):
        lang = self.lang
        self.live.setStyleSheet("font-weight: bold")
        if self.current < 0:
            self.live.setText(self.t("s_no_image"))
            return
        s = self.project["sections"][self.current]
        pts = s.get("outline", [])
        if len(pts) < 3:
            self.live.setText(self.t("s_need_points", n=len(pts)))
            return
        y = self.project["yarns"].get(s["label"]) or {}
        try:
            v = section_values(pts, self.project["pixel_um"], y.get("tex"), y.get("rho"))
        except ValueError:
            self.live.setText(self.t("s_err_cross"))
            self.live.setStyleSheet(f"color: {RED}; font-weight: bold")
            return
        txt = self.t("s_live", a=fmt(v["area_um2"], 0, lang), d=fmt(v["d_eq_um"], 1, lang),
                     asp=fmt(v["aspect"], 2, lang))
        if "phi" in v:
            txt += self.t("s_live_phi", phi=fmt(v["phi"], 3, lang))
            if v["phi"] >= 1:
                txt += "\n" + self.t("s_phi_impossible")
                self.live.setStyleSheet(f"color: {RED}; font-weight: bold")
        else:
            txt += " · " + self.t("s_yarn_missing")
        if v["flag"]:
            txt += "\n" + self.t("s_flag_aspect", lim=fmt(ASPECT_LIMIT, 1, lang),
                                 phim=fmt(v.get("phi_minor", float("nan")), 3, lang) if "phi_minor" in v else "—")
            if v.get("phi", 0) < 1:
                self.live.setStyleSheet(f"color: {ORANGE}; font-weight: bold")
        self.live.setText(txt)

    # ---------------------------------------------------------- pixel size
    def pixel_edited(self, value):
        self.project["pixel_um"] = float(value)
        self.project["pixel_how"] = self.t("pixel_manual")
        self.pixel_info.setText(self.project["pixel_how"])
        self.settings.setValue("pixel_um", float(value))
        self.mark_changed()
        self.refresh_values()
        self.update_live()

    def calibrate(self):
        dlg = CalibrationDialog(self.lang, self.start_dir(), self)
        if dlg.exec() == QDialog.Accepted and dlg.result:
            s, L, p, f = dlg.result
            self.pixel.blockSignals(True)
            self.pixel.setValue(s)
            self.pixel.blockSignals(False)
            self.project["pixel_um"] = float(s)
            self.project["pixel_how"] = self.t("pixel_calc", L=fmt(L, 1, self.lang), p=fmt(p, 1, self.lang),
                                               s=fmt(s, 4, self.lang), f=os.path.basename(f))
            self.pixel_info.setText(self.project["pixel_how"])
            self.settings.setValue("pixel_um", float(s))
            self.mark_changed()
            self.refresh_values()
            self.update_live()

    # --------------------------------------------------------------- yarns
    def labels(self):
        out = []
        for s in self.project["sections"]:
            if s["label"] not in out:
                out.append(s["label"])
        return out

    def edit_yarn(self, row):
        labels = self.labels()
        if not labels:
            return
        lab = labels[row] if 0 <= row < len(labels) else labels[0]
        dlg = YarnDialog(self.lang, lab or "—", self.project["yarns"].get(lab) or self.default_yarn, self)
        if dlg.exec() == QDialog.Accepted and dlg.yarn():
            self.project["yarns"][lab] = dlg.yarn()
            self.mark_changed()
            self.refresh_yarns()
            self.refresh_values()
            self.update_live()

    # ------------------------------------------------------------- refresh
    def refresh_all(self):
        self.refresh_images()
        self.refresh_yarns()
        self.refresh_values()

    def refresh_images(self):
        t = self.img_table
        self._building = True
        t.setRowCount(len(self.project["sections"]))
        for i, s in enumerate(self.project["sections"]):
            t.setItem(i, 0, QTableWidgetItem(s["label"]))
            it = _text(os.path.basename(s["image"]))
            it.setToolTip(s["image"])
            t.setItem(i, 1, it)
            t.setItem(i, 2, _num(None, 3, self.lang))
            u = QTableWidgetItem("")
            u.setFlags((u.flags() | Qt.ItemIsUserCheckable) & ~Qt.ItemIsEditable)
            u.setCheckState(Qt.Checked if s.get("use", True) else Qt.Unchecked)
            t.setItem(i, 3, u)
        self._building = False

    def refresh_yarns(self):
        lang = self.lang
        t = self.yarn_table
        labels = self.labels()
        t.setRowCount(len(labels))
        for i, lab in enumerate(labels):
            y = self.project["yarns"].get(lab)
            t.setItem(i, 0, _text(lab))
            if y:
                t.setItem(i, 1, _text(f"{fmt(y['count'], 2, lang)} {y['unit']}"))
                t.setItem(i, 2, _text(blend_text(y["blend"], lang)))
                t.setItem(i, 3, _num(y["rho"], 3, lang))
                t.setItem(i, 4, _num(1000 * y["tex"] / y["rho"], 0, lang))
            else:
                it = _text(self.t("s_yarn_missing"))
                it.setForeground(Qt.red)
                t.setItem(i, 1, it)
                for c in (2, 3, 4):
                    t.setItem(i, c, _text(""))

    def refresh_values(self):
        lang = self.lang
        if not self.project.get("pixel_um"):
            return
        self.rows, self.summary = evaluate(self.project)
        st = self.sec_table
        st.setRowCount(len(self.rows))
        it_t = self.img_table
        self._building = True
        n_out = 0
        for i, (s, v, err) in enumerate(self.rows):
            v = v or {}
            n_out += bool(v)
            st.setItem(i, 0, _text(s["label"]))
            st.setItem(i, 1, _text(os.path.basename(s["image"])))
            st.setItem(i, 2, _num(len(s.get("outline", [])), 0, lang))
            for j, (k, nd) in enumerate((("area_um2", 0), ("d_eq_um", 1), ("major_um", 1), ("minor_um", 1),
                                          ("aspect", 2), ("phi", 3), ("phi_minor", 3))):
                st.setItem(i, 3 + j, _num(v.get(k), nd, lang))
            st.setItem(i, 10, _text("✓" if s.get("use", True) else "–"))
            note = self.t("s_err_cross") if err else (
                self.t("note_aspect", lim=fmt(ASPECT_LIMIT, 1, lang)) if v.get("flag") else "")
            st.setItem(i, 11, _text(note))
            if i < it_t.rowCount():
                it_t.setItem(i, 2, _num(v.get("phi"), 3, lang))
        self._building = False
        sm = self.sum_table
        sm.setRowCount(len(self.summary))
        for i, (lab, d) in enumerate(self.summary.items()):
            sm.setItem(i, 0, _text(lab))
            sm.setItem(i, 1, _num(d["n"], 0, lang))
            m, sd, ci = d["phi_mean"], d["phi_sd"], d["phi_ci95"]
            txt = "—" if not _isnum(m) else fmt(m, 3, lang) + ("" if not _isnum(sd) else " ± " + fmt(sd, 3, lang))
            sm.setItem(i, 2, _text(txt))
            sm.setItem(i, 3, _text("—" if not _isnum(ci) else f"{fmt(m - ci, 3, lang)} – {fmt(m + ci, 3, lang)}"))
            sm.setItem(i, 4, _num(d["phi_cv"], 1, lang))
            dm, dsd = d["d_eq_mean"], d["d_eq_sd"]
            sm.setItem(i, 5, _text("—" if not _isnum(dm) else fmt(dm, 1, lang)
                                   + ("" if not _isnum(dsd) else " ± " + fmt(dsd, 1, lang))))
            sm.setItem(i, 6, _num(d["aspect_mean"], 2, lang))
            sm.setItem(i, 7, _num(d["n_flagged"], 0, lang))
            sm.setItem(i, 8, _num(d["d_theoretical"], 1, lang))
        self.statusBar().showMessage(self.t("s_status", n=len(self.project["sections"]), m=n_out))

    # -------------------------------------------------------------- saving
    def mark_changed(self):
        self.dirty = True
        if self.outline_file:
            try:
                save_outlines(self.outline_file, self.project, program=f"YarnHair {__version__} (YarnSection)")
                self.dirty = False
            except OSError as e:
                self.message.setText(self.t("s_open_failed", e=e))

    def save_outlines_as(self):
        f, _ = QFileDialog.getSaveFileName(self, self.t("s_act_save_outlines"),
                                           self.outline_file or os.path.join(self.start_dir(), "outlines.json"),
                                           self.t("s_outline_filter"))
        if not f:
            return False
        if not f.lower().endswith(".json"):
            f += ".json"
        save_outlines(f, self.project, program=f"YarnHair {__version__} (YarnSection)")
        self.outline_file, self.dirty = f, False
        self.message.setText(self.t("s_saved_outlines", p=f))
        return True

    def open_outlines(self):
        if self.dirty and self.project["sections"] and not self.ask_save():
            return
        f, _ = QFileDialog.getOpenFileName(self, self.t("s_act_open"), self.start_dir(), self.t("s_outline_filter"))
        if f:
            self.load_file(f)

    def load_file(self, f):
        try:
            pr = load_outlines(f)
        except (OSError, ValueError, KeyError, TypeError) as e:
            QMessageBox.critical(self, "YarnSection", self.t("s_open_failed", e=e))
            return False
        self.project = pr
        self.project.setdefault("pixel_how", "")
        self.outline_file, self.dirty = f, False
        self.current = 0
        self.build_ui()
        return True

    def save_results(self):
        if not any(v for _, v, _ in self.rows):
            QMessageBox.information(self, "YarnSection", self.t("s_no_sections"))
            return
        f, flt = QFileDialog.getSaveFileName(self, self.t("act_save"),
                                             os.path.join(self.start_dir(), "yarnsection_results.xlsx"),
                                             self.t("save_filter"))
        if not f:
            return
        if not f.lower().endswith((".xlsx", ".tsv")):
            f += ".tsv" if "tsv" in flt else ".xlsx"
        try:
            self.write_results(f)
        except Exception as e:      # file open in Excel, openpyxl missing ...
            QMessageBox.critical(self, "YarnSection", f"{type(e).__name__}: {e}")
            return
        self.message.setText(self.t("saved", p=f))

    def write_results(self, f):
        import csv
        secs = section_table(self.rows)
        if f.lower().endswith(".tsv"):
            with open(f, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh, delimiter="\t")
                for row in secs:
                    w.writerow([f"{x:.4f}" if isinstance(x, float) else x for x in row])
            return
        from openpyxl import Workbook
        from openpyxl.styles import Font
        wb = Workbook()
        sheets = [(self.t("sheet_sections"), secs), (self.t("sheet_summary"), summary_table(self.summary))]
        yarns = [["label", "count", "unit", "tex", "blend", "rho_g_cm3", "fibre_area_um2"]]
        for lab in self.labels():
            y = self.project["yarns"].get(lab)
            if y:
                yarns.append([lab, y["count"], y["unit"], y["tex"], blend_text(y["blend"], "en"), y["rho"],
                              1000 * y["tex"] / y["rho"]])
        sheets.append((self.t("sheet_yarns"), yarns))
        settings = [[self.t("set_version"), f"YarnHair {__version__} (YarnSection)"],
                    [self.t("set_date"), datetime.datetime.now().strftime("%Y-%m-%d %H:%M")],
                    [self.t("set_pixel"), self.project["pixel_um"]],
                    [self.t("set_pixel_how"), self.project.get("pixel_how") or self.t("pixel_manual")],
                    [self.t("set_method"), self.t("set_method_text")],
                    [self.t("set_aspect_limit"), ASPECT_LIMIT],
                    ["outlines", self.outline_file or ""]]
        sheets.append((self.t("sheet_settings"), settings))
        ws = wb.active
        for k, (title, rows) in enumerate(sheets):
            if k:
                ws = wb.create_sheet()
            ws.title = title[:31]
            for row in rows:
                ws.append([None if (isinstance(x, float) and x != x) else x for x in row])
            if k < 3:
                for c in ws[1]:
                    c.font = Font(bold=True)
                ws.freeze_panes = "A2"
        ws.column_dimensions["A"].width = 34          # settings sheet
        wb.save(f)

    def save_checks(self):
        todo = [(s, v) for s, v, _ in self.rows if v and os.path.exists(s["image"])]
        if not todo:
            QMessageBox.information(self, "YarnSection", self.t("s_no_sections"))
            return
        d = QFileDialog.getExistingDirectory(self, self.t("s_act_save_checks"), self.start_dir())
        if not d:
            return
        from PIL import Image, ImageDraw, ImageFont
        n = 0
        for s, v in todo:
            im = Image.open(s["image"]).convert("RGB")
            dr = ImageDraw.Draw(im)
            w = max(2, int(round(min(im.size) / 400)))
            pts = [tuple(p) for p in s["outline"]]
            dr.line(pts + [pts[0]], fill=(255, 220, 0), width=w)
            size = max(14, int(min(im.size) / 30))
            try:
                font = ImageFont.load_default(size=size)
            except TypeError:           # Pillow < 10.1
                font = ImageFont.load_default()
            txt = f"{s['label']}  d = {v['d_eq_um']:.1f} um  aspect {v['aspect']:.2f}"
            if "phi" in v:
                txt += f"  phi = {v['phi']:.3f}"
            if not s.get("use", True):
                txt += "  (not used)"
            dr.text((10, 10), txt, fill=(255, 220, 0), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
            base = os.path.splitext(os.path.basename(s["image"]))[0]
            name = f"{s['label']}_{base}".replace("/", "_") if s["label"] else base
            im.save(os.path.join(d, name + "_outline.png"))
            n += 1
        self.message.setText(self.t("s_checks_done", n=n, p=d))

    def ask_save(self):
        """Returns False if the user cancels."""
        r = QMessageBox.question(self, "YarnSection", self.t("s_ask_save"),
                                 QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
        if r == QMessageBox.Cancel:
            return False
        if r == QMessageBox.Save:
            return self.save_outlines_as()
        return True

    def closeEvent(self, e):
        has_outlines = any(len(s.get("outline", [])) >= 3 for s in self.project["sections"])
        if self.dirty and has_outlines and not self.outline_file and not self.ask_save():
            e.ignore()
            return
        e.accept()

    # ------------------------------------------------------------- YarnHair
    def use_in_yarnhair(self):
        if self.link is None:
            return
        r = self.sum_table.currentRow()
        labels = list(self.summary)
        if not labels:
            QMessageBox.information(self, "YarnSection", self.t("s_no_sections"))
            return
        lab = labels[r] if 0 <= r < len(labels) else labels[0]
        d = self.summary[lab]
        if d["n"] < 3 or not _isnum(d["phi_mean"]):
            QMessageBox.information(self, "YarnSection", self.t("s_need_three"))
            return
        self.link.use_section_phi(d["phi_mean"], lab, d["n"], d["phi_sd"])
        self.message.setText(self.t("s_used_phi", phi=fmt(d["phi_mean"], 3, self.lang), label=lab, n=d["n"]))

    # -------------------------------------------------------------- dialogs
    def show_method(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(self.t("s_act_method"))
        dlg.resize(760, 620)
        v = QVBoxLayout(dlg)
        tb = QTextBrowser()
        tb.setHtml(self.t("s_method_html"))
        v.addWidget(tb)
        bb = QDialogButtonBox(QDialogButtonBox.Close)
        bb.rejected.connect(dlg.reject)
        v.addWidget(bb)
        dlg.exec()

    def show_about(self):
        QMessageBox.about(self, self.t("s_act_about"), self.t("s_about_text", v=__version__))
