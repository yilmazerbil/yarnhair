"""Pixel size from two clicks on a stage-micrometer image."""
import os

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDoubleSpinBox,
                               QDialogButtonBox, QFileDialog)

from .texts import tr, fmt
from .viewer import ImageView


class CalibrationDialog(QDialog):
    def __init__(self, lang, start_dir="", parent=None):
        super().__init__(parent)
        self.lang = lang
        self.start_dir = start_dir
        self.result = None          # (um_per_px, length_um, pixels, file)
        self.setWindowTitle(tr("cal_title", lang))
        self.resize(1000, 760)
        lay = QVBoxLayout(self)
        hint = QLabel(tr("cal_hint", lang))
        hint.setWordWrap(True)
        lay.addWidget(hint)
        top = QHBoxLayout()
        self.btn_open = QPushButton(tr("cal_open", lang))
        self.btn_open.clicked.connect(self.open_image)
        self.file_label = QLabel("")
        top.addWidget(self.btn_open)
        top.addWidget(self.file_label, 1)
        lay.addLayout(top)
        self.view = ImageView(pick_points=True)
        self.view.pointsChanged.connect(self.update_result)
        lay.addWidget(self.view, 1)
        row = QHBoxLayout()
        row.addWidget(QLabel(tr("cal_length", lang)))
        self.length = QDoubleSpinBox()
        self.length.setRange(0.1, 100000)
        self.length.setDecimals(1)
        self.length.setValue(1000.0)
        self.length.setSuffix(" µm")
        self.length.valueChanged.connect(self.update_result)
        row.addWidget(self.length)
        row.addStretch(1)
        lay.addLayout(row)
        self.px_label = QLabel(tr("cal_need", lang))
        self.res_label = QLabel("")
        lay.addWidget(self.px_label)
        lay.addWidget(self.res_label)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        self.ok = bb.button(QDialogButtonBox.Ok)
        self.ok.setEnabled(False)
        lay.addWidget(bb)
        self.file = ""

    def open_image(self):
        f, _ = QFileDialog.getOpenFileName(self, tr("cal_open", self.lang), self.start_dir, tr("img_filter", self.lang))
        if f:
            self.load(f)

    def load(self, f):
        self.file = f
        self.file_label.setText(os.path.basename(f))
        self.view.set_image(f)

    def update_result(self, *_):
        d = self.view.distance()
        lang = self.lang
        if not d:
            self.px_label.setText(tr("cal_need", lang))
            self.res_label.setText("")
            self.ok.setEnabled(False)
            self.result = None
            return
        L = self.length.value()
        s = L / d
        self.px_label.setText(tr("cal_pixels", lang, p=fmt(d, 1, lang)))
        self.res_label.setText("<b>" + tr("cal_result", lang, L=fmt(L, 1, lang), p=fmt(d, 1, lang),
                                          s=fmt(s, 4, lang)) + "</b>")
        self.result = (s, L, d, self.file)
        self.ok.setEnabled(True)
