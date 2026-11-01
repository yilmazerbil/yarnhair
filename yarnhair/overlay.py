"""Display image with detected hairs drawn on top (for checking results).
Measurements are always made on the raw image; the enhancement below is for
display only and is the same fixed transform for every frame."""
import colorsys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.draw import line as draw_line

from .measure import prep


def enhance(X):
    """Fixed display transform: background subtraction (151 px box, 40th
    percentile clip), fixed scale /170, gamma 0.5, unsharp mask (sigma 2, 0.6)."""
    E = np.clip(prep(X) / 170.0, 0, 1) ** 0.5
    E = np.clip(E + 0.6 * (E - ndi.gaussian_filter(E, 2)), 0, 1)
    return E


def _colours(n):
    return [tuple(int(255 * c) for c in colorsys.hsv_to_rgb(0.1 + 0.8 * ((i * 0.618034) % 1), 0.85, 1.0))
            for i in range(n)]


def hair_pixels(hair, D):
    """All pixels of one hair: detected skeleton plus its connection to the boundary."""
    H3, conn = D["H3"], D["conn"]
    pts = [np.argwhere(np.isin(H3, hair["members"]))]
    for h in hair["members"]:
        if h in conn:
            kind, v = conn[h]
            if kind == "path":
                pts.append(np.asarray(v))
            else:  # straight drop from the innermost pixel to the boundary
                y0, x0 = v
                m, b, Rb = D["m"], D["b"], D["Rb"]
                yax = m * x0 + b
                s = np.sign(y0 - yax) or 1
                y1 = int(round(yax + s * Rb * np.sqrt(1 + m * m)))
                rr, cc = draw_line(int(y0), int(x0), y1, int(x0))
                pts.append(np.stack([rr, cc], 1))
    return np.concatenate(pts) if pts else np.zeros((0, 2), int)


def render(D, accepted, unresolved, out_path, scale=0.5, width=3):
    """Save a PNG: enhanced frame, dashed body boundary, each accepted hair
    in its own colour (red is never used for them), unresolved fragments in red."""
    X = D["X"]
    H, W = X.shape
    E = (enhance(X) * 255).astype(np.uint8)
    rgb = np.stack([E, E, E], 2)

    def paint(pts, col):
        if len(pts) == 0:
            return
        pts = pts[(pts[:, 0] >= 0) & (pts[:, 0] < H) & (pts[:, 1] >= 0) & (pts[:, 1] < W)]
        mk = np.zeros((H, W), bool)
        mk[pts[:, 0], pts[:, 1]] = True
        mk = ndi.binary_dilation(mk, iterations=width)
        rgb[mk] = col

    for hair, col in zip(accepted, _colours(len(accepted))):
        paint(hair_pixels(hair, D), col)
    for hair in unresolved:
        paint(np.argwhere(np.isin(D["H3"], hair["members"])), (255, 0, 0))
    # dashed body boundary (white)
    m, b, Rb = D["m"], D["b"], D["Rb"]
    off = Rb * np.sqrt(1 + m * m)
    for x in range(W):
        if (x // 20) % 2:
            continue
        for s in (-1, 1):
            y = int(round(m * x + b + s * off))
            if 0 <= y < H:
                rgb[max(0, y - 1):y + 2, x] = 255
    img = Image.fromarray(rgb)
    if scale != 1:
        img = img.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    img.save(out_path)
    return out_path
