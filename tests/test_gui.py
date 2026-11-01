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


def test_section_window_and_link(tmp_path):
    """Cross-section window: outline -> phi -> summary -> outline file -> phi in YarnHair."""
    pytest.importorskip("PySide6")
    import math
    import numpy as np
    from PIL import Image
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from yarnhair.gui.app import MainWindow
    from yarnhair.gui.section_window import SectionWindow
    from yarnhair.packing import theoretical_diameter_um
    from yarnhair.section import load_outlines, synthetic_section
    app = QApplication.instance() or QApplication([])
    main = MainWindow()
    main.count.setValue(14)                       # Ne 14, 100 % cotton
    yarn = main.current_yarn()
    assert yarn and abs(yarn["tex"] - 590.5 / 14) < 1e-9
    files = []
    for k in range(3):
        p = tmp_path / f"s{k}.png"
        Image.fromarray(synthetic_section(seed=k).astype(np.uint8)).save(p)
        files.append(["B0", str(p)])
    w = SectionWindow(lang="tr", link=main, default_yarn=yarn)
    w.pixel.setValue(1.0)
    w.add_files(files)
    phis = []
    for k, phi in enumerate((0.30, 0.32, 0.34)):
        w.select(k)
        r = theoretical_diameter_um(yarn["tex"], yarn["rho"], phi) / 2
        w.view.set_points([(300 + r * math.cos(a / 36 * math.pi), 300 + r * math.sin(a / 36 * math.pi))
                           for a in range(72)])
        phis.append(w.rows[k][1]["phi"])
    app.processEvents()
    s = w.summary["B0"]
    assert s["n"] == 3 and abs(s["phi_mean"] - sum(phis) / 3) < 1e-12 and abs(s["phi_mean"] - 0.32) < 0.002
    # leave one section out
    w.select(2)
    w.use_box.setChecked(False)
    assert w.summary["B0"]["n"] == 2
    w.use_box.setChecked(True)
    # outline file is written and, from then on, kept up to date
    f = tmp_path / "outlines.json"
    from yarnhair.section import save_outlines
    save_outlines(str(f), w.project)
    w.outline_file = str(f)
    w.view.set_points(w.project["sections"][2]["outline"][:-1])      # one point fewer -> autosave
    assert len(load_outlines(str(f))["sections"][2]["outline"]) == 71
    # results file
    w.write_results(str(tmp_path / "r.xlsx"))
    w.write_results(str(tmp_path / "r.tsv"))
    assert (tmp_path / "r.tsv").read_text(encoding="utf-8").count("\n") == 4
    # language switch keeps the work
    w.set_language("en")
    assert len(w.project["sections"]) == 3 and w.summary["B0"]["n"] == 3
    # the mean phi goes to YarnHair
    w.sum_table.setCurrentCell(0, 0)
    w.use_in_yarnhair()
    assert main.mode_theory.isChecked() and abs(main.phi.value() - round(w.summary["B0"]["phi_mean"], 3)) < 1e-9
    assert main.phi_source and "B0" in main.phi_source
    settings = dict(main.run_settings(main.boundary(), 3.85, ["B0"]))
    assert "B0" in settings[main.t("set_phi_src")]
    main.phi.setValue(0.33)                       # typed by hand: source is cleared
    assert main.phi_source is None
    w.dirty = False
    w.close()
    main.close()


def test_yarnsection_selftest(capsys):
    pytest.importorskip("PySide6")
    from yarnhair.gui.section_app import selftest
    assert selftest() == 0
    assert "self-test passed" in capsys.readouterr().out
