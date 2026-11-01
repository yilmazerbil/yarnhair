"""Hair detection and measurement for one microscope frame.

Pipeline (see docs/method.md):
1. yarn axis and apparent diameter from the brightness profile;
2. body boundary = larger of apparent and theoretical radius;
3. background subtraction and Sato ridge filter (bright ridges, sigma 1-3 px);
4. ridge response normalised to the far background (median, 1.4826*MAD);
5. hysteresis thresholding, stricter in a band next to the boundary (halo);
6. skeleton, spur pruning, junction decomposition, gap bridging;
7. every hair is connected back to the boundary (direct drop, or the
   cheapest path along the ridge map); hairs that cannot be connected are
   reported as unresolved and are not counted;
8. hair length = length outside the boundary, including the connection.
"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.filters import sato, apply_hysteresis_threshold
from skimage.graph import MCP_Geometric
from skimage.morphology import skeletonize, remove_small_objects

from .skeleton import merge_segments, bridge, prune_spurs

# Parameters used in the published analysis (tuned on four hand-traced frames).
DEFAULT_CONFIG = dict(
    lo=3,            # hysteresis low threshold (robust z units)
    hi=20,           # hysteresis high threshold
    zone_px=40,      # width of the stricter band next to the body boundary (px)
    zone_k=3,        # threshold multiplier inside that band
    minlen=0.1,      # minimum total hair length (mm)
    spur=25,         # spur pruning length (px)
    win=320,         # search window for path connection (px)
    gap_ok=40,       # gaps up to this distance (px) are closed by a straight drop
    ridge_min=2.0,   # ridge level counted as "on a fibre" along a connecting path
    onr_min=0.5,     # minimum share of a connecting path lying on a fibre
    lenk=1.6,        # path length limit: lenk * gap + 30 px
    cont_px=50,      # meeting another hair within this distance of its outer end = same hair
    minvis=40,       # minimum visible (detected) length of a hair (px)
)


def _remove_small(M, n):
    """Remove connected objects smaller than n pixels (works with old and new scikit-image)."""
    import inspect
    if "max_size" in inspect.signature(remove_small_objects).parameters:
        return remove_small_objects(M, max_size=n - 1)
    return remove_small_objects(M, min_size=n)


def load_gray(path):
    """Read an image and return the mean of the RGB channels as float."""
    return np.asarray(Image.open(path).convert("RGB")).astype(float).mean(2)


def body(X):
    """Yarn axis y = m*x + b and apparent half-diameter hd (px), from the
    half-maximum width of the brightness profile in every 8th column."""
    H, W = X.shape
    bgv = np.median(X)
    diam, cent = [], []
    for c in range(0, W, 8):
        col = np.convolve(X[:, c], np.ones(9) / 9, "same")
        p = col.argmax()
        t = bgv + 0.5 * (col[p] - bgv)
        l = p
        while l > 0 and col[l] > t:
            l -= 1
        r = p
        while r < H - 1 and col[r] > t:
            r += 1
        diam.append(r - l)
        cent.append((l + r) / 2)
    m, b = np.polyfit(np.arange(0, W, 8), cent, 1)
    yc = int(np.median(cent))
    hd = int(np.median(diam) / 2)
    return m, b, yc, hd


def prep(X):
    """Subtract a smooth background (151 px box of the image clipped at its
    40th percentile)."""
    bg = ndi.uniform_filter(np.minimum(X, np.percentile(X, 40)), 151)
    return np.clip(X - bg, 0, None)


def trace_hairs(R, m, b, yc, hd, Rb, px_mm, lo=10, hi=30, zone_px=40, zone_k=2, minlen=0.1,
                spur=25, win=320, gap_ok=40, ridge_min=2.0, onr_min=0.5, lenk=1.6,
                cont_px=25, minvis=26):
    """Detect hairs on the ridge map R and connect each one to the body
    boundary (radius Rb px around the axis). Returns (N, total length mm,
    accepted hairs, unresolved hairs, details)."""
    H, W = R.shape
    hd = int(hd)
    far = np.concatenate([R[:max(1, yc - hd - 400)].ravel(), R[min(H - 1, yc + hd + 400):].ravel()])
    med = np.median(far)
    sd = 1.4826 * np.median(np.abs(far - med))
    yy, xx = np.mgrid[0:H, 0:W]
    dB = np.abs(yy - (m * xx + b)) / np.sqrt(1 + m * m) - Rb   # signed distance to boundary (px)
    Rn = (R - med) / sd
    kmul = np.where((dB > 0) & (dB < zone_px), zone_k, 1.0)
    M = apply_hysteresis_threshold(Rn / kmul, lo, hi) & (dB > 0)
    M = _remove_small(M, 12)
    S = prune_spurs(skeletonize(M), spur)
    DT = ndi.distance_transform_edt(M)
    H2, n2, info, sp = merge_segments(S, DT)
    H3, n3, Bm = bridge(H2, info, sp, dB <= 0)
    cost = 1.0 / (0.3 + np.clip(Rn, 0, 20) / 5.0)
    ys, xs = np.nonzero(H3)
    L = H3[ys, xs]
    d = dB[ys, xs]
    parent = list(range(n3 + 1))

    def f(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    dmin = np.full(n3 + 1, 1e9)
    np.minimum.at(dmin, L, d)
    order = np.argsort(dmin[1:]) + 1
    conn, status = {}, {}
    attached = set(h for h in range(1, n3 + 1) if dmin[h] <= 3)
    inner = {}
    for h in range(1, n3 + 1):
        k = np.nonzero(L == h)[0]
        i = k[np.argmin(d[k])]
        inner[h] = (ys[i], xs[i])
    for h in order:
        if h in attached:
            status[h] = "attached"
            continue
        y0, x0 = inner[h]
        if dmin[h] <= gap_ok:
            status[h] = "extended"          # short straight drop to the boundary
            conn[h] = ("line", (y0, x0))
            continue
        side = np.sign(y0 - (m * x0 + b)) or 1
        ya, yb = ((int(max(0, y0 - win)), int(min(H, y0 + 40))) if side > 0
                  else (int(max(0, y0 - 40)), int(min(H, y0 + win))))
        xa, xb = int(max(0, x0 - win)), int(min(W, x0 + win))
        cw = cost[ya:yb, xa:xb]
        goal = (dB[ya:yb, xa:xb] <= 0.5) & (dB[ya:yb, xa:xb] >= -2)
        if not goal.any():
            status[h] = "unresolved"
            continue
        mcp = MCP_Geometric(cw)
        cum, _ = mcp.find_costs([(y0 - ya, x0 - xa)])
        gi = np.argwhere(goal)
        cg = cum[goal]
        j = np.argmin(cg)
        path = np.array(mcp.traceback(tuple(gi[j])))
        plen = len(path)
        pg = path + [ya, xa]
        rr = Rn[pg[:, 0], pg[:, 1]]
        onr = (rr >= ridge_min).mean()
        if plen <= lenk * dmin[h] + 30 and onr >= onr_min:
            hv = H3[pg[:, 0], pg[:, 1]]
            idx = np.nonzero((hv > 0) & (hv != h))[0]
            if len(idx):
                o = hv[idx[0]]
                py, px = pg[idx[0]]
                ko = np.nonzero(L == o)[0]
                oy, ox = ys[ko][np.argmax(d[ko])], xs[ko][np.argmax(d[ko])]
                if np.hypot(py - oy, px - ox) <= cont_px:
                    # the path meets another hair near its outer end: same fibre
                    parent[f(h)] = f(o)
                    status[h] = "traced"
                    conn[h] = ("path", pg[:idx[0]])
                    continue
                pg = pg[:idx[0]]
            status[h] = "traced"
            conn[h] = ("path", pg)
        else:
            status[h] = "unresolved"
    groups = {}
    for h in range(1, n3 + 1):
        groups.setdefault(f(h), []).append(h)
    hairs = []
    for g, members in groups.items():
        st = [status.get(h) for h in members]
        ok = any(s in ("attached", "extended", "traced") for s in st)
        npx = sum((L == h).sum() for h in members)
        extra = 0
        for h in members:
            if h in conn:
                kind, v = conn[h]
                extra += max(dmin[h], 0) if kind == "line" else len(v)
        Lh = (npx + extra) * px_mm
        md = max(dB[ys[L == h], xs[L == h]].max() for h in members) * px_mm
        hairs.append(dict(members=members, ok=ok, L=Lh, md=md, vis=npx))
    acc = [x for x in hairs if x["ok"] and x["L"] >= minlen and x["vis"] >= minvis]
    q = [x for x in hairs if not x["ok"] and x["vis"] >= minvis]
    N = len(acc)
    Ls = sum(x["L"] for x in acc)
    return N, Ls, acc, q, dict(H3=H3, conn=conn, dB=dB)


def measure_frame(path_or_array, diameter_um=0.0, pixel_um=3.85, config=None):
    """Measure one frame.

    diameter_um : theoretical yarn diameter in micrometres (0 = use the
                  apparent diameter only). The boundary radius is the larger
                  of the theoretical and apparent radius.
    pixel_um    : pixel size at the yarn plane in micrometres.

    Returns (results, accepted_hairs, unresolved_hairs, details). Counts and
    lengths are normalised to 10 mm of yarn.
    """
    cfg = dict(DEFAULT_CONFIG)
    if config:
        cfg.update(config)
    X = load_gray(path_or_array) if not isinstance(path_or_array, np.ndarray) else path_or_array.astype(float)
    px_mm = pixel_um / 1000.0
    m, b, yc, hd = body(X)
    R = sato(prep(X), sigmas=(1, 2, 3), black_ridges=False)
    Rb = max(diameter_um / 2 / pixel_um, hd)
    N, L, acc, q, D = trace_hairs(R, m, b, int(yc), hd, Rb, px_mm, **cfg)
    md = np.array([x["md"] for x in acc]) if acc else np.zeros(0)
    W = X.shape[1]
    f = 10 / (W * np.sqrt(1 + m * m) * px_mm)          # per 10 mm of yarn
    res = dict(apparent_diameter_px=int(hd * 2), boundary_radius_px=float(Rb),
               N=N * f, L=L * f,
               N05=(md >= 0.5).sum() * f, N1=(md >= 1).sum() * f,
               N2=(md >= 2).sum() * f, N3=(md >= 3).sum() * f,
               unresolved=len(q), mean_length=(L / N if N else 0.0))
    D.update(m=m, b=b, Rb=Rb, X=X)
    return res, acc, q, D


# Kept here for backward compatibility; see packing.py.
from .packing import theoretical_diameter_um, ne_to_tex  # noqa: E402,F401
