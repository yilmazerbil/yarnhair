"""Packing density from yarn cross-sections (outline method).

On an image of a yarn cross-section the user draws the outline of the yarn
body: around the outermost fibres that still belong to the compact body;
protruding and displaced fibres stay outside. The fibre area in a section
perpendicular to the yarn axis follows from the yarn count and the blend
density alone,

    A_f = 1000 T / rho      (um2; T in tex, rho in g/cm3),

because the mass per unit length of yarn equals the density times the fibre
area in a transverse section. Fibre fineness, fibre number and twist do not
enter (the number of fibres in a section does depend on twist, their total
area does not). The packing density of one section is

    phi = A_f / A,

with A the area inside the outline. No fibre has to be recognised in the
image, so the method also works on sections whose fibres cannot be separated.

Checks of a section
- aspect: major / minor axis of the ellipse with the same second moments as
  the outline. An oblique cut stretches the outline in one direction by
  1/cos(angle) and leaves the short axis unchanged; flattening by the knife
  also raises it. Sections above ASPECT_LIMIT are flagged.
- phi_minor = A_f / (pi minor^2 / 4): the value if the yarn is round and the
  long axis comes only from an oblique cut. Reported, not used by default.
- An outline that crosses itself has no defined area and is rejected.
"""
import json
import math
import os

from .packing import substance_area_um2, theoretical_diameter_um

ASPECT_LIMIT = 1.3
FORMAT = "yarnsection-outlines"


# ----------------------------------------------------------------- geometry
def _segments_cross(p1, p2, p3, p4):
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2 = orient(p3, p4, p1), orient(p3, p4, p2)
    d3, d4 = orient(p1, p2, p3), orient(p1, p2, p4)
    return (d1 * d2 < 0) and (d3 * d4 < 0)


def self_intersects(points):
    """True if two non-adjacent edges of the closed polygon cross."""
    n = len(points)
    if n < 4:
        return False
    edges = [(points[i], points[(i + 1) % n]) for i in range(n)]
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:      # first and last edge share a vertex
                continue
            if _segments_cross(*edges[i], *edges[j]):
                return True
    return False


def polygon_props(points):
    """Area, centroid, perimeter and equivalent ellipse of a closed polygon.

    points: sequence of (x, y) in pixels; the polygon is closed implicitly.
    Returns dict(area, cx, cy, perimeter, major, minor, angle) in pixels and
    degrees; major/minor are the full axes of the ellipse with the same area
    moments of second order (for a circle both equal the diameter)."""
    pts = [(float(x), float(y)) for x, y in points]
    n = len(pts)
    if n < 3:
        raise ValueError("an outline needs at least 3 points")
    a2 = cx = cy = sxx = syy = sxy = per = 0.0
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        c = x0 * y1 - x1 * y0
        a2 += c
        cx += (x0 + x1) * c
        cy += (y0 + y1) * c
        sxx += (x0 * x0 + x0 * x1 + x1 * x1) * c
        syy += (y0 * y0 + y0 * y1 + y1 * y1) * c
        sxy += (x0 * y1 + 2 * x0 * y0 + 2 * x1 * y1 + x1 * y0) * c
        per += math.hypot(x1 - x0, y1 - y0)
    area = a2 / 2
    if abs(area) < 1e-9:
        raise ValueError("the outline has no area")
    cx /= 6 * area
    cy /= 6 * area
    mxx = sxx / 12 / area - cx * cx          # central moments per unit area; the sign of
    myy = syy / 12 / area - cy * cy          # the area (drawing direction) cancels
    mxy = sxy / 24 / area - cx * cy
    half = (mxx + myy) / 2
    disc = math.sqrt(max(half * half - (mxx * myy - mxy * mxy), 0.0))
    l1, l2 = half + disc, max(half - disc, 0.0)
    angle = 0.5 * math.degrees(math.atan2(2 * mxy, mxx - myy))
    return dict(area=abs(area), cx=cx, cy=cy, perimeter=per,
                major=4 * math.sqrt(l1), minor=4 * math.sqrt(l2), angle=angle)


def section_values(points, pixel_um, tex=None, density=None):
    """Values of one section from its outline (pixels).

    Returns dict with area_um2, d_eq_um (diameter of the circle of equal area),
    major_um, minor_um, aspect, perimeter_um, n_points, flag ("" or
    "aspect"), and, if tex and density are given, fibre_area_um2, phi and
    phi_minor. Raises ValueError for fewer than 3 points or a crossing outline."""
    if pixel_um <= 0:
        raise ValueError("pixel size must be positive")
    if self_intersects(points):
        raise ValueError("the outline crosses itself")
    p = polygon_props(points)
    s = float(pixel_um)
    area = p["area"] * s * s
    out = dict(area_um2=area, d_eq_um=2 * math.sqrt(area / math.pi), major_um=p["major"] * s,
               minor_um=p["minor"] * s, perimeter_um=p["perimeter"] * s, n_points=len(points),
               angle_deg=p["angle"], cx_px=p["cx"], cy_px=p["cy"])
    out["aspect"] = p["major"] / p["minor"] if p["minor"] > 0 else float("inf")
    out["flag"] = "aspect" if out["aspect"] > ASPECT_LIMIT else ""
    if tex and density:
        af = substance_area_um2(tex, density)
        out["fibre_area_um2"] = af
        out["phi"] = af / area
        out["phi_minor"] = af / (math.pi * out["minor_um"] ** 2 / 4) if out["minor_um"] > 0 else float("nan")
    return out


# ------------------------------------------------------------------ summary
def _t975(df):
    from scipy.stats import t
    return float(t.ppf(0.975, df))


def summarise(values, tex=None, density=None):
    """Summary of the sections of one yarn (only those with use=True).

    values: dicts from section_values (with an optional key "use").
    Returns dict(n, n_flagged, phi_mean, phi_sd, phi_cv, phi_ci95, d_eq_mean,
    d_eq_sd, aspect_mean, area_mean, phi_of_mean_area, d_theoretical) with
    NaN where a value cannot be computed. phi_ci95 is the half-width of the
    95 % confidence interval of the mean (t distribution). d_theoretical is the
    diameter YarnHair calculates from count, density and phi_mean."""
    nan = float("nan")
    used = [v for v in values if v.get("use", True)]
    n = len(used)
    out = dict(n=n, n_flagged=sum(1 for v in used if v.get("flag")), phi_mean=nan, phi_sd=nan, phi_cv=nan,
               phi_ci95=nan, d_eq_mean=nan, d_eq_sd=nan, aspect_mean=nan, area_mean=nan,
               phi_of_mean_area=nan, d_theoretical=nan)
    if n == 0:
        return out

    def mean_sd(xs):
        m = sum(xs) / len(xs)
        sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) if len(xs) > 1 else nan
        return m, sd

    out["d_eq_mean"], out["d_eq_sd"] = mean_sd([v["d_eq_um"] for v in used])
    out["aspect_mean"] = sum(v["aspect"] for v in used) / n
    out["area_mean"] = sum(v["area_um2"] for v in used) / n
    phis = [v["phi"] for v in used if "phi" in v]
    if len(phis) == n:
        m, sd = mean_sd(phis)
        out["phi_mean"], out["phi_sd"] = m, sd
        if n > 1:
            out["phi_cv"] = 100 * sd / m
            out["phi_ci95"] = _t975(n - 1) * sd / math.sqrt(n)
        af = used[0]["fibre_area_um2"]
        out["phi_of_mean_area"] = af / out["area_mean"]
        if tex and density and 0 < m < 1:
            out["d_theoretical"] = theoretical_diameter_um(tex, density, m)
    return out


# ------------------------------------------------------- outline suggestion
def _dilate(m, r):
    from scipy import ndimage as ndi
    return ndi.distance_transform_edt(~m) <= r


def _erode(m, r):
    from scipy import ndimage as ndi
    return ndi.distance_transform_edt(m) > r


def suggest_outline(gray, expected_diameter_px=None, n_points=48, max_side=1600):
    """Suggest an outline of the yarn body on a cross-section image.

    Smooths the image, splits it at the Otsu threshold, closes the gaps between
    fibres (disk of 6 % of the expected diameter), fills holes and takes the
    compact region that does not touch the image border and whose area is
    closest to the expected area (else the largest). Both polarities are tried
    (fibres brighter or darker than the embedding medium). Large images are
    reduced to at most max_side pixels for this step. The contour is resampled
    to n_points vertices equally spaced along it, starting at the top (few
    points to edit; a circle comes out 0.3 % small with 48). Returns a list of
    (x, y) vertices in pixels of the original image, or None. The result is only
    a suggestion: the measurement is the outline the user accepts."""
    import numpy as np
    from scipy import ndimage as ndi
    from skimage.filters import gaussian, threshold_otsu
    from skimage.measure import find_contours, regionprops

    g = np.asarray(gray, dtype=float)
    if g.ndim == 3:
        g = g[..., :3].mean(2)
    f = max(1, int(math.ceil(max(g.shape) / max_side)))
    if f > 1:                                     # block mean
        h, w = (g.shape[0] // f) * f, (g.shape[1] // f) * f
        g = g[:h, :w].reshape(h // f, f, w // f, f).mean(axis=(1, 3))
    if g.max() - g.min() < 1e-9:
        return None
    g = gaussian(g, sigma=1.5, preserve_range=True)
    t = threshold_otsu(g)
    h, w = g.shape
    if expected_diameter_px:
        dexp = expected_diameter_px / f
        r = max(2.0, 0.06 * dexp)
        a_exp = math.pi * dexp ** 2 / 4
    else:
        r = max(2.0, 0.01 * min(h, w))
        a_exp = None
    pad = int(math.ceil(r)) + 2
    best, best_score = None, -math.inf
    for fg in (g > t, g < t):
        m = np.pad(fg, pad)
        m = _erode(_dilate(m, r), r)                       # closing
        m = ndi.binary_fill_holes(m)
        m = _dilate(_erode(m, r / 2), r / 2)               # opening
        m = m[pad:-pad, pad:-pad]
        lab, n = ndi.label(m)
        for rp in regionprops(lab):
            r0, c0, r1, c1 = rp.bbox
            if r0 == 0 or c0 == 0 or r1 == h or c1 == w:
                continue
            if rp.solidity < 0.7:
                continue
            if a_exp is not None:
                if not 0.2 * a_exp < rp.area < 5 * a_exp:
                    continue
                score = -abs(math.log(rp.area / a_exp))
            else:
                score = rp.area
            if score > best_score:
                best, best_score = (lab == rp.label), score
    if best is None:
        return None
    cs = find_contours(np.pad(best, 1).astype(float), 0.5)
    if not cs:
        return None
    c = np.asarray(max(cs, key=len), dtype=float)
    if np.allclose(c[0], c[-1]):
        c = c[:-1]
    c = np.roll(c, -int(np.argmin(c[:, 0])), axis=0)          # start at the top
    c = np.vstack([c, c[:1]])
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(c, axis=0).T))])
    u = np.linspace(0.0, s[-1], int(n_points), endpoint=False)
    c = np.column_stack([np.interp(u, s, c[:, 0]), np.interp(u, s, c[:, 1])])
    off = (f - 1) / 2                             # centre of a block in original pixels
    pts = [((float(col) - 1) * f + off, (float(row) - 1) * f + off) for row, col in c]
    return pts if len(pts) >= 3 else None


def synthetic_section(seed=1, radius=120, fibre_radius=6, size=600, bright=True):
    """Test image: bright fibre discs packed at random inside a circle of the given
    radius (pixels) on a dark background, or the reverse (bright=False)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[:size, :size]
    img = 40 + rng.normal(0, 3, (size, size))
    c = size / 2
    centres = []
    for _ in range(20000):
        rr = (radius - fibre_radius) * math.sqrt(rng.random())
        a = 2 * math.pi * rng.random()
        x, y = c + rr * math.cos(a), c + rr * math.sin(a)
        if all((x - u) ** 2 + (y - v) ** 2 >= (2 * fibre_radius + 1) ** 2 for u, v in centres):
            centres.append((x, y))
    for x, y in centres:
        img[(xx - x) ** 2 + (yy - y) ** 2 <= fibre_radius ** 2] = 200
    img = np.clip(img, 0, 255)
    return img if bright else 255 - img


# ------------------------------------------------------------- outline files
def empty_project():
    return dict(format=FORMAT, version=1, pixel_um=None, pixel_how="", yarns={}, sections=[])


def save_outlines(path, project, program=""):
    """Write a project (yarns, pixel size and outlines) as JSON. Image paths
    are stored relative to the file when possible, so the folder can be moved."""
    base = os.path.dirname(os.path.abspath(path))
    data = dict(project)
    data["format"], data["version"] = FORMAT, 1
    if program:
        data["program"] = program
    secs = []
    for s in project["sections"]:
        s = dict(s)
        img = os.path.abspath(s["image"])
        try:
            s["image"] = os.path.relpath(img, base).replace(os.sep, "/")
        except ValueError:          # other drive on Windows
            s["image"] = img
        s["outline"] = [[round(float(x), 2), round(float(y), 2)] for x, y in s.get("outline", [])]
        secs.append(s)
    data["sections"] = secs
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)


def load_outlines(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if data.get("format") != FORMAT:
        raise ValueError("not a YarnSection outline file")
    base = os.path.dirname(os.path.abspath(path))
    for s in data["sections"]:
        if not os.path.isabs(s["image"]):
            s["image"] = os.path.normpath(os.path.join(base, s["image"]))
        s["outline"] = [tuple(p) for p in s.get("outline", [])]
        s.setdefault("use", True)
    data.setdefault("yarns", {})
    return data


SECTION_COLUMNS = ["label", "image", "use", "area_um2", "d_eq_um", "major_um", "minor_um", "aspect",
                   "phi", "phi_minor", "flag", "error"]
SUMMARY_COLUMNS = ["label", "n", "phi_mean", "phi_sd", "phi_ci95", "phi_cv", "phi_of_mean_area", "d_eq_mean",
                   "d_eq_sd", "aspect_mean", "n_flagged", "d_theoretical"]


def section_table(rows):
    """Rows of evaluate() as a table (header first); empty cells for sections
    without an outline."""
    out = [list(SECTION_COLUMNS)]
    for s, v, err in rows:
        v = v or {}
        out.append([s["label"], os.path.basename(s["image"]), int(bool(s.get("use", True)))]
                   + [v.get(k, "") for k in SECTION_COLUMNS[3:-1]] + [err])
    return out


def summary_table(summary):
    out = [list(SUMMARY_COLUMNS)]
    for lab, d in summary.items():
        out.append([lab] + [d[k] for k in SUMMARY_COLUMNS[1:]])
    return out


def evaluate(project):
    """Values of every outlined section and the summary per label.

    Returns (rows, summary): rows = list of (section, values or None, error);
    summary = {label: summarise(...)} in the order labels first appear."""
    px = project.get("pixel_um")
    rows, groups = [], {}
    for s in project["sections"]:
        y = project["yarns"].get(s["label"], {})
        tex, rho = y.get("tex"), y.get("rho")
        v, err = None, ""
        if len(s.get("outline", [])) >= 3 and px:
            try:
                v = section_values(s["outline"], px, tex, rho)
                v["use"] = s.get("use", True)
            except ValueError as e:
                err = str(e)
        rows.append((s, v, err))
        if v is not None:
            groups.setdefault(s["label"], []).append(v)
    summary = {}
    for lab, vs in groups.items():
        y = project["yarns"].get(lab, {})
        summary[lab] = summarise(vs, y.get("tex"), y.get("rho"))
    return rows, summary
