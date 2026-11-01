"""YarnSection: the cross-section window as a program of its own (``yarnsection``).

``yarnsection --selftest`` suggests and measures the outline of a synthetic
section, opens the window off-screen (where the suggestion appears on its own
and is accepted) and returns exit code 0 if this works.
"""
import math
import os
import sys
import tempfile


def selftest():
    from PIL import Image
    from .. import __version__
    from ..section import polygon_props, section_values, suggest_outline, synthetic_section
    img = synthetic_section()
    pts = suggest_outline(img, expected_diameter_px=250)
    ok = pts is not None
    if ok:
        area = polygon_props(pts)["area"]
        v = section_values(pts, 1.0, 42.18, 1.50)
        ok = abs(area / (math.pi * 120 ** 2) - 1) < 0.12 and 0 < v["phi"] < 1
        print(f"suggested outline: {len(pts)} points, area {area:.0f} px² "
              f"(fibres placed within a circle of {math.pi * 120 ** 2:.0f} px²), phi {v['phi']:.3f}")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from .section_window import SectionWindow
    app = QApplication.instance() or QApplication(sys.argv[:1])
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "section.png")
        Image.fromarray(img.astype("uint8")).save(path)
        w = SectionWindow(lang="en")
        w.add_files([["test", path]])
        auto = w.project["sections"][0].get("status") == "suggested"
        w.accept_suggestion()
        app.processEvents()
        ok = ok and auto and w.project["sections"][0]["status"] == "accepted" and w.rows and w.rows[0][1] is not None
        print("window: suggestion shown on opening and accepted" if ok else "window: suggestion FAILED")
        w.dirty = False
        w.close()
    print(f"YarnSection {__version__}")
    print("self-test", "passed" if ok else "FAILED")
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv[1:]:
        return selftest()
    from PySide6.QtWidgets import QApplication
    from .section_window import SectionWindow
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("YarnSection")
    w = SectionWindow()
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
