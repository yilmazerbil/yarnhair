"""Skeleton graph utilities: split the hair skeleton into segments, join
segments that continue each other across junctions, and bridge short gaps
between hair fragments that point at each other."""
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.morphology import skeletonize

K8 = np.ones((3, 3), int)


def nbcount(S):
    """Number of 8-neighbours of every skeleton pixel."""
    return ndi.convolve(S.astype(np.uint8), K8, mode="constant") - S


def segments(S):
    """Split a skeleton into segments between junction clusters."""
    nb = nbcount(S)
    J = S & (nb >= 3)
    Jl, nj = ndi.label(J, structure=np.ones((3, 3)))
    Seg = S & ~J
    Sl, ns = ndi.label(Seg, structure=np.ones((3, 3)))
    return J, Jl, nj, Sl, ns


def seglen(mask):
    """Length of a one-pixel-wide path in pixels (orthogonal steps 1,
    diagonal steps sqrt(2))."""
    o = mask[:, :-1] & mask[:, 1:]
    v = mask[:-1, :] & mask[1:, :]
    d1 = mask[:-1, :-1] & mask[1:, 1:]
    d2 = mask[:-1, 1:] & mask[1:, :-1]
    return o.sum() + v.sum() + np.sqrt(2) * (d1.sum() + d2.sum())


def order_pixels(coords):
    """Order the pixels of a simple path starting from one end."""
    S = set(map(tuple, coords))

    def nbs(p):
        return [(p[0] + a, p[1] + b) for a in (-1, 0, 1) for b in (-1, 0, 1)
                if (a or b) and (p[0] + a, p[1] + b) in S]

    ends = [p for p in S if len(nbs(p)) <= 1] or [next(iter(S))]
    path = [ends[0]]
    seen = {ends[0]}
    while True:
        n = [q for q in nbs(path[-1]) if q not in seen]
        if not n:
            break
        path.append(n[0])
        seen.add(n[0])
    return np.array(path)


def decompose(S, DT=None, spur=3, turn_max=60, tail=8, spur_k=1.5):
    """Label the hairs of a skeleton. Segments are joined across a junction
    only where the fibre continues nearly straight (turn <= turn_max degrees),
    so crossing or touching hairs stay separate."""
    J, Jl, nj, Sl, ns = segments(S)
    info = {}
    for s in range(1, ns + 1):
        c = np.argwhere(Sl == s)
        P = order_pixels(c) if len(c) > 1 else c
        ends = []
        for e, inner in ((P[0], P[min(tail, len(P) - 1)]),
                         (P[-1], P[max(-tail - 1, -len(P))])):
            y, x = e
            ys = slice(max(0, y - 1), y + 2)
            xs = slice(max(0, x - 1), x + 2)
            jl = np.unique(Jl[ys, xs])
            jl = jl[jl > 0]
            d = (e - inner).astype(float)
            d /= (np.linalg.norm(d) + 1e-9)  # outward direction
            ends.append((int(jl[0]) if len(jl) else 0, d))
        info[s] = dict(n=len(P), ends=ends, P=P)

    # tiny free spurs (shorter than the local fibre radius) are medial-axis artefacts
    def jhalf(v):
        js = [e[0] for e in v["ends"] if e[0] > 0]
        if DT is None or not js:
            return spur
        return max(spur, spur_k * max(DT[Jl == j].max() for j in js))

    spurs = {s for s, v in info.items()
             if ((v["ends"][0][0] == 0) != (v["ends"][1][0] == 0)) and v["n"] <= jhalf(v)}
    parent = {s: s for s in info}

    def f(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for j in range(1, nj + 1):
        arms = [(s, k, v["ends"][k][1]) for s, v in info.items() if s not in spurs
                for k in (0, 1) if v["ends"][k][0] == j]
        used = set()
        pairs = []
        for a in range(len(arms)):
            for b in range(a + 1, len(arms)):
                cosang = -float(np.dot(arms[a][2], arms[b][2]))
                pairs.append((cosang, a, b))
        for cosang, a, b in sorted(pairs, reverse=True):
            if a in used or b in used:
                continue
            if cosang < np.cos(np.radians(turn_max)):
                break
            used |= {a, b}
            parent[f(arms[a][0])] = f(arms[b][0])
    H = np.zeros(S.shape, int)
    roots = {}
    for s, v in info.items():
        if s in spurs:
            continue
        r = f(s)
        roots.setdefault(r, len(roots) + 1)
        H[Sl == s] = roots[r]
    # junction pixels go to a touching hair so that no length is lost
    Jlab = ndi.grey_dilation(H, footprint=np.ones((3, 3)))
    H[J] = Jlab[J]
    return H, len(roots), spurs, info


def _dir(P, k, tail=15):
    n = len(P)
    if k == 0:
        e, i = P[0], P[min(tail, n - 1)]
    else:
        e, i = P[-1], P[max(-tail - 1, -n)]
    d = (e - i).astype(float)
    return d / (np.linalg.norm(d) + 1e-9)


def merge_segments(S, DT):
    """decompose() plus: a junction with only two arms joins them, and a loop
    that leaves and returns to the same junction belongs to the hair it closes
    on (curled tips and loops are part of the same hair)."""
    J, Jl, nj, Sl, ns = segments(S)
    Hl, nh, spurs, info = decompose(S, DT)
    seg2hair = {s: int(Hl[tuple(v["P"][len(v["P"]) // 2])])
                for s, v in info.items() if s not in spurs}
    parent = list(range(nh + 1))

    def f(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for j in range(1, nj + 1):
        arms = [(s, k) for s, v in info.items() if s not in spurs
                for k in (0, 1) if v["ends"][k][0] == j]
        segs = [a[0] for a in arms]
        loops = {s for s in segs if segs.count(s) == 2}
        if len(arms) == 2 or loops:
            hs = [seg2hair[s] for s in set(segs)] if len(arms) == 2 else None
            if len(arms) == 2:
                parent[f(hs[0])] = f(hs[-1])
            for s in loops:
                others = [o for o in set(segs) if o != s]
                if others:
                    o = max(others, key=lambda o: info[o]["n"])
                    parent[f(seg2hair[s])] = f(seg2hair[o])
    lut = np.array([f(a) for a in range(nh + 1)])
    H2 = lut[Hl]
    H2[Hl == 0] = 0
    u, inv = np.unique(H2, return_inverse=True)
    H2 = inv.reshape(H2.shape)
    return H2, len(u) - 1, info, spurs


def bezier(p0, d0, p1, d1):
    """Cubic Bezier between two free ends following their directions.
    The curve length is stored in bezier.last."""
    d = np.linalg.norm(p1 - p0)
    c0 = p0 + d0 * d / 3
    c1 = p1 + d1 * d / 3
    t = np.linspace(0, 1, max(4, int(3 * d)))[:, None]
    B = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * c0 + 3 * (1 - t) * t ** 2 * c1 + t ** 3 * p1
    bezier.last = float(np.linalg.norm(np.diff(B, axis=0), axis=1).sum())
    return np.unique(np.round(B).astype(int), axis=0)


def bridge(Hl, info, spurs, BM, gmax=120, ang_near=45, ang_far=30, near=20):
    """Join free ends of different hairs that continue each other's
    direction and draw the hidden part. Bridges never cross the yarn body (BM).
    Returns the relabelled image, the number of hairs and the bridge mask;
    bridge lengths (px) are stored in bridge.blen."""
    H, W = Hl.shape
    E = []
    for s, v in info.items():
        if s in spurs:
            continue
        P = v["P"]
        for k in (0, 1):
            if v["ends"][k][0] == 0:
                p = P[0] if k == 0 else P[-1]
                E.append((int(Hl[p[0], p[1]]), np.array(p, float), _dir(P, k)))
    bridge.blen = []
    if len(E) < 2:
        return Hl, Hl.max(), np.zeros_like(Hl, bool)
    T = cKDTree(np.array([e[1] for e in E]))
    cand = []
    for i, j in T.query_pairs(gmax):
        li, pi, di = E[i]
        lj, pj, dj = E[j]
        if li == lj or 0 in (li, lj):
            continue
        v = pj - pi
        d = np.linalg.norm(v)
        if d < 1:
            continue
        v = v / d
        a1 = np.degrees(np.arccos(np.clip(di @ v, -1, 1)))
        a2 = np.degrees(np.arccos(np.clip(dj @ -v, -1, 1)))
        lim = ang_near if d <= near else ang_far
        if a1 > lim or a2 > lim:
            continue
        off = abs(di[0] * (pj - pi)[1] - di[1] * (pj - pi)[0])  # lateral offset
        if d > near and off > 0.3 * d:
            continue
        cand.append((d * (1 + (a1 + a2) / 90), i, j, li, lj))
    parent = list(range(Hl.max() + 1))

    def f(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    used = set()
    blen = []
    Bm = np.zeros_like(Hl, bool)
    Hn = Hl.copy()
    for _, i, j, li, lj in sorted(cand):
        if i in used or j in used or f(li) == f(lj):
            continue
        pts = bezier(E[i][1], E[i][2], E[j][1], E[j][2])
        pts = pts[(pts[:, 0] >= 0) & (pts[:, 0] < H) & (pts[:, 1] >= 0) & (pts[:, 1] < W)]
        if BM[pts[:, 0], pts[:, 1]].any():
            continue
        used |= {i, j}
        parent[f(li)] = f(lj)
        blen.append(bezier.last)
        free = Hn[pts[:, 0], pts[:, 1]] == 0
        Bm[pts[free, 0], pts[free, 1]] = True
        Hn[pts[free, 0], pts[free, 1]] = li
    lut = np.array([f(a) for a in range(len(parent))])
    H2 = lut[Hn]
    H2[Hn == 0] = 0
    u, inv = np.unique(H2, return_inverse=True)
    H2 = inv.reshape(H2.shape)
    bridge.blen = blen
    return H2, len(u) - 1, Bm


def prune_spurs(S, maxlen=15, it=3):
    """Remove short side branches (< maxlen px) that end free on one side
    and touch a junction on the other."""
    S = S.copy()
    for _ in range(it):
        J, Jl, nj, Sl, ns = segments(S)
        if ns == 0:
            break
        nb = nbcount(S)
        ends = S & (nb == 1)
        Jd = ndi.binary_dilation(J, structure=np.ones((3, 3)))
        sizes = ndi.sum(np.ones_like(Sl), Sl, index=np.arange(1, ns + 1))
        hasend = ndi.maximum(ends, Sl, index=np.arange(1, ns + 1))
        hasj = ndi.maximum(Jd, Sl, index=np.arange(1, ns + 1))
        kill = [i + 1 for i in range(ns) if sizes[i] < maxlen and hasend[i] and hasj[i]]
        if not kill:
            break
        S[np.isin(Sl, kill)] = False
        S = skeletonize(S)
    return S
