"""Graphical program: texts in both languages and an off-screen start (skipped without PySide6)."""
import os

import pytest


def test_gui_texts_have_both_languages():
    from yarnhair.gui.texts import T
    for key, val in T.items():
        assert isinstance(val, tuple) and len(val) == 2 and all(isinstance(x, str) and x for x in val), key


def test_window_opens_offscreen():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from yarnhair.gui.app import MainWindow
    app = QApplication.instance() or QApplication([])
    w = MainWindow()
    w.show()
    app.processEvents()
    w.close()
