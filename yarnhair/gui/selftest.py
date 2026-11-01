"""Self-test of an installed or frozen program: ``yarnhair-gui --selftest``.

Measures a synthetic frame with six straight hairs in a separate process (as the
program does), opens the main window and the cross-section window off-screen
and reports the result. Exit code 0 means the measurement libraries, the worker
processes and Qt work.
"""
import multiprocessing
import os
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor


def synthetic_frame(seed=0):
    """Bright horizontal yarn on a dark background with six straight hairs (8-bit RGB)."""
    import numpy as np
    from skimage.draw import line_aa
    rng = np.random.default_rng(seed)
    H, W = 900, 1200
    X = 20 + rng.normal(0, 1.5, (H, W))
    yc, r = H // 2, 30
    yy = np.arange(H)[:, None]
    X += 200 * np.exp(-((yy - yc) / r) ** 8)
    for i, x in enumerate(np.linspace(100, W - 100, 6).astype(int)):
        s = -1 if i % 2 else 1
        rr, cc, v = line_aa(yc + s * (r - 2), x, yc + s * (r + 150), x + 40)
        X[rr, cc] += 120 * v
    X = np.clip(X, 0, 255).astype(np.uint8)
    return np.dstack([X] * 3)


def run():
    from PIL import Image
    from .. import __version__
    from .tasks import process_frame
    ok = True
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "selftest.bmp")
        Image.fromarray(synthetic_frame()).save(path)
        ctx = multiprocessing.get_context("spawn")
        with ProcessPoolExecutor(max_workers=2, mp_context=ctx) as ex:
            res = ex.submit(process_frame, path, "selftest", 0.0, 3.85, os.path.join(d, "overlay.png")).result(timeout=600)
        if "error" in res:
            print("measurement failed:", res["error"], res.get("trace", ""))
            ok = False
        else:
            hairs = res["N"] * 1200 * 3.85e-3 / 10       # back to hairs per frame
            ok = round(hairs) == 6 and res["L"] > 0 and os.path.exists(res["overlay"])
            print(f"hairs per frame {hairs:.2f} (expected 6), L {res['L']:.3f} mm per 10 mm, "
                  f"{res['seconds']:.1f} s")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from .app import MainWindow
    app = QApplication.instance() or QApplication(sys.argv[:1])
    w = MainWindow()
    w.show()
    w.open_sections()                 # the cross-section window is part of the program
    app.processEvents()
    ok = ok and w.section_win is not None and w.section_win.isVisible()
    w.section_win.dirty = False
    w.close()
    import numpy, scipy, skimage
    print(f"YarnHair {__version__}; numpy {numpy.__version__}, scipy {scipy.__version__}, "
          f"scikit-image {skimage.__version__}")
    print("self-test", "passed" if ok else "FAILED")
    return 0 if ok else 1
