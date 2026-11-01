"""Blend editor (fibre from the list, mass share, density with source) and the
dialog that defines the yarn of one label in the cross-section window."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QTableWidget,
                               QHeaderView, QComboBox, QDoubleSpinBox, QDialog, QDialogButtonBox)

from ..fibres import FIBRES, OTHER, SOURCES as FIBRE_SOURCES, SOURCE_SHORT, SOURCE_PENDING, fibre_name, blend_density
from ..packing import COUNT_UNITS, DEFAULT_PACKING, to_tex, substance_area_um2, theoretical_diameter_um
from .texts import tr, fmt


class BlendTable(QWidget):
    changed = Signal()

    def __init__(self, lang, rows=None, parent=None):
        super().__init__(parent)
        self.lang = lang
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([tr(k, lang) for k in ("col_fibre", "col_share", "col_density",
                                                                     "col_source")])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setMinimumHeight(130)
        v.addWidget(self.table)
        row = QHBoxLayout()
        b = QPushButton(tr("btn_add_fibre", lang))
        b.clicked.connect(lambda: self.add_row("cotton", 0.0))
        row.addWidget(b)
        b = QPushButton(tr("btn_del_fibre", lang))
        b.clicked.connect(self.remove_row)
        row.addWidget(b)
        self.info = QLabel("")
        row.addWidget(self.info, 1)
        v.addLayout(row)
        for key, share, dens in (rows or [("cotton", 100.0, None)]):
            self.add_row(key, share, dens)
        self._update()

    def add_row(self, key="cotton", share=0.0, density=None):
        t = self.table
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
        idx = cb.findData(key)
        cb.setCurrentIndex(idx if idx >= 0 else cb.findData(OTHER))
        self._fibre_changed(cb)
        if (key == OTHER or idx < 0) and density:
            ds.setValue(density)
        cb.currentIndexChanged.connect(lambda _=0, c=cb: self._fibre_changed(c))
        sp.valueChanged.connect(self._update)
        ds.valueChanged.connect(self._update)
        self._update()

    def _fibre_changed(self, cb):
        t = self.table
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
                        txt += " – " + tr("pending", self.lang)
                    src.setText(txt)
                    src.setToolTip(FIBRE_SOURCES[skey])
        self._update()

    def remove_row(self):
        t = self.table
        r = t.currentRow()
        if r < 0:
            r = t.rowCount() - 1
        if r >= 0 and t.rowCount() > 1:
            t.removeRow(r)
            self._update()

    def rows(self):
        t = self.table
        return [(t.cellWidget(r, 0).currentData(), t.cellWidget(r, 1).value(), t.cellWidget(r, 2).value())
                for r in range(t.rowCount())]

    def total(self):
        return sum(s for _, s, _ in self.rows())

    def density(self):
        """Blend density, or None if the shares do not add up to 100 %."""
        if abs(self.total() - 100) >= 0.01:
            return None
        return blend_density([(s, d) for _, s, d in self.rows()])

    def _update(self, *_):
        lang = self.lang
        txt = tr("blend_total", lang, s=fmt(self.total(), 2, lang))
        rho = self.density()
        if rho is not None:
            txt += "   " + tr("blend_rho", lang, r=fmt(rho, 3, lang))
            self.info.setStyleSheet("")
        else:
            txt += "   " + tr("blend_bad", lang)
            self.info.setStyleSheet("color: #c62828")
        self.info.setText(txt)
        self.changed.emit()


def blend_text(rows, lang):
    return "; ".join(f"{fibre_name(k, lang)} {fmt(s, 2, lang)} %" for k, s, _ in rows)


class YarnDialog(QDialog):
    """Count and blend of the yarn of one label; shows the fibre area of a section."""

    def __init__(self, lang, label, yarn=None, parent=None):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(tr("s_yarn_title", lang, label=label))
        self.resize(760, 460)
        v = QVBoxLayout(self)
        g = QGridLayout()
        g.addWidget(QLabel(tr("count", lang)), 0, 0)
        self.count = QDoubleSpinBox()
        self.count.setRange(0, 100000)
        self.count.setDecimals(2)
        self.count.setSpecialValueText("—")
        self.unit = QComboBox()
        self.unit.addItems(list(COUNT_UNITS))
        self.unit.setCurrentText("Ne")
        h = QHBoxLayout()
        h.addWidget(self.count)
        h.addWidget(self.unit)
        h.addStretch(1)
        g.addLayout(h, 0, 1)
        v.addLayout(g)
        v.addWidget(QLabel(tr("blend", lang)))
        rows = None
        if yarn:
            self.count.setValue(yarn.get("count") or 0)
            self.unit.setCurrentText(yarn.get("unit", "Ne"))
            rows = [tuple(r) for r in yarn.get("blend", [])] or None
        self.blend = BlendTable(lang, rows)
        v.addWidget(self.blend, 1)
        self.calc = QLabel("")
        self.calc.setWordWrap(True)
        v.addWidget(self.calc)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        self.ok = bb.button(QDialogButtonBox.Ok)
        v.addWidget(bb)
        self.count.valueChanged.connect(self._update)
        self.unit.currentIndexChanged.connect(self._update)
        self.blend.changed.connect(self._update)
        self._update()

    def yarn(self):
        """dict(count, unit, tex, blend, rho) or None if incomplete."""
        if self.count.value() <= 0:
            return None
        rho = self.blend.density()
        if rho is None:
            return None
        tex = to_tex(self.count.value(), self.unit.currentText())
        return dict(count=self.count.value(), unit=self.unit.currentText(), tex=tex,
                    blend=[list(r) for r in self.blend.rows()], rho=rho)

    def _update(self, *_):
        lang = self.lang
        y = self.yarn()
        self.ok.setEnabled(y is not None)
        if y is None:
            self.calc.setText(tr("need_count", lang) if self.count.value() <= 0 else tr("blend_bad", lang))
            return
        af = substance_area_um2(y["tex"], y["rho"])
        d = theoretical_diameter_um(y["tex"], y["rho"], DEFAULT_PACKING)
        self.calc.setText(tr("s_fibre_area", lang, T=fmt(y["tex"], 2, lang), rho=fmt(y["rho"], 3, lang),
                             a=fmt(af, 0, lang), d=fmt(d, 0, lang)))
