"""Work done in the background processes (no Qt imports here)."""
import os
import time
import traceback


def process_frame(path, label, diameter_um, pixel_um, overlay_path):
    """Measure one frame and write its checking image.

    Returns a dict with the results, or with the key "error"."""
    t0 = time.time()
    try:
        from ..measure import measure_frame
        from ..overlay import render
        res, acc, q, D = measure_frame(path, diameter_um=diameter_um, pixel_um=pixel_um)
        if overlay_path:
            os.makedirs(os.path.dirname(overlay_path), exist_ok=True)
            render(D, acc, q, overlay_path, scale=0.5)
        out = {k: (float(v) if not isinstance(v, (int, str)) else v) for k, v in res.items()}
        out.update(path=path, label=label, overlay=overlay_path, diameter_um=diameter_um,
                   pixel_um=pixel_um, seconds=time.time() - t0)
        return out
    except Exception as e:  # unreadable or unsuitable image
        return dict(path=path, label=label, error=f"{type(e).__name__}: {e}",
                    trace=traceback.format_exc(limit=3), seconds=time.time() - t0)
