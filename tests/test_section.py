"""Cross-section packing density: geometry, phi, summary, outline suggestion and files."""
import math

import numpy as np
import pytest

from yarnhair.packing import substance_area_um2, theoretical_diameter_um
from yarnhair.section import (ASPECT_LIMIT, evaluate, load_outlines, polygon_props, save_outlines, section_values,
                              self_intersects, suggest_outline, summarise, empty_project, synthetic_section)


def circle(r, n=720, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def ellipse(a, b, angle_deg=0.0, n=720):
    t = math.radians(angle_deg)
    pts = []
    for k in range(n):
        u = 2 * math.pi * k / n
        x, y = a * math.cos(u), b * math.sin(u)
        pts.append((x * math.cos(t) - y * math.sin(t), x * math.sin(t) + y * math.cos(t)))
    return pts


def test_circle_area_and_axes():
    p = polygon_props(circle(100, cx=50, cy=-20))
    assert p["area"] == pytest.approx(math.pi * 100 ** 2, rel=1e-4)
    assert p["major"] == pytest.approx(200, rel=1e-4) and p["minor"] == pytest.approx(200, rel=1e-4)
    assert (p["cx"], p["cy"]) == (pytest.approx(50, abs=1e-6), pytest.approx(-20, abs=1e-6))


def test_rectangle_moments_and_direction():
    sq = [(0, 0), (40, 0), (40, 10), (0, 10)]
    p = polygon_props(sq)
    assert p["area"] == pytest.approx(400)
    # full axes of the ellipse with the same second moments: 4 * sqrt(w^2 / 12)
    assert p["major"] == pytest.approx(4 * math.sqrt(40 ** 2 / 12))
    assert p["minor"] == pytest.approx(4 * math.sqrt(10 ** 2 / 12))
    # drawing direction does not matter
    q = polygon_props(sq[::-1])
    assert q["area"] == pytest.approx(p["area"]) and q["major"] == pytest.approx(p["major"])


def test_ellipse_aspect_and_angle():
    p = polygon_props(ellipse(150, 100, angle_deg=30))
    assert p["major"] == pytest.approx(300, rel=1e-3) and p["minor"] == pytest.approx(200, rel=1e-3)
    assert p["angle"] == pytest.approx(30, abs=0.1)


def test_self_intersection():
    assert self_intersects([(0, 0), (10, 10), (10, 0), (0, 10)])          # bow tie
    assert not self_intersects([(0, 0), (10, 0), (10, 10), (0, 10)])
    with pytest.raises(ValueError):
        section_values([(0, 0), (10, 10), (10, 0), (0, 10)], 1.0)
    with pytest.raises(ValueError):
        section_values([(0, 0), (10, 0)], 1.0)


def test_phi_of_a_section():
    # Ne 14 cotton yarn (42.18 tex, 1.52 g/cm3) drawn as a circle of 332.3 um:
    # the theoretical diameter at phi = 0.32, so phi must come back as 0.32
    tex, rho = 590.5 / 14, 1.52
    d = theoretical_diameter_um(tex, rho, 0.32)
    px = 2.0                                     # um per pixel
    v = section_values(circle(d / 2 / px), px, tex, rho)
    assert v["phi"] == pytest.approx(0.32, rel=1e-4)
    assert v["d_eq_um"] == pytest.approx(d, rel=1e-4)
    assert v["fibre_area_um2"] == pytest.approx(1000 * tex / rho)
    assert v["aspect"] == pytest.approx(1.0, abs=1e-3) and v["flag"] == ""


def test_oblique_cut_flag_and_minor_axis():
    # a round yarn cut at 45 deg: long axis 1/cos(45) longer, short axis unchanged
    tex, rho, px = 42.18, 1.50, 1.0
    r = theoretical_diameter_um(tex, rho, 0.35) / 2
    v = section_values(ellipse(r / math.cos(math.radians(45)), r), px, tex, rho)
    assert v["aspect"] == pytest.approx(math.sqrt(2), rel=1e-3) and v["aspect"] > ASPECT_LIMIT
    assert v["flag"] == "aspect"
    assert v["phi"] == pytest.approx(0.35 * math.cos(math.radians(45)), rel=1e-3)
    assert v["phi_minor"] == pytest.approx(0.35, rel=1e-3)


def test_summary():
    tex, rho = 42.18, 1.50
    af = substance_area_um2(tex, rho)
    vals = []
    for phi in (0.30, 0.32, 0.34, 0.36):
        r = math.sqrt(af / phi / math.pi)
        vals.append(section_values(circle(r), 1.0, tex, rho))
    vals.append(dict(section_values(circle(5.0), 1.0, tex, rho), use=False))   # excluded section
    s = summarise(vals, tex, rho)
    assert s["n"] == 4
    assert s["phi_mean"] == pytest.approx(0.33, rel=1e-4)
    sd = np.std([0.30, 0.32, 0.34, 0.36], ddof=1)
    assert s["phi_sd"] == pytest.approx(sd, rel=1e-4)
    assert s["phi_ci95"] == pytest.approx(3.182446 * sd / 2, rel=1e-4)     # t(0.975, 3)
    assert s["d_theoretical"] == pytest.approx(theoretical_diameter_um(tex, rho, s["phi_mean"]))
    assert s["d_theoretical"] == pytest.approx(theoretical_diameter_um(tex, rho, 0.33), rel=1e-4)


@pytest.mark.parametrize("bright", [True, False])
def test_suggested_outline(bright):
    img = synthetic_section(bright=bright)
    pts = suggest_outline(img, expected_diameter_px=250)
    assert pts is not None
    p = polygon_props(pts)
    assert p["area"] == pytest.approx(math.pi * 120 ** 2, rel=0.12)
    assert (p["cx"], p["cy"]) == (pytest.approx(300, abs=8), pytest.approx(300, abs=8))


def test_suggested_outline_on_a_large_image():
    # a 2400 x 2400 image is reduced for the suggestion; vertices come back in full-size pixels
    img = np.kron(synthetic_section(), np.ones((4, 4)))
    pts = suggest_outline(img, expected_diameter_px=1000)
    p = polygon_props(pts)
    assert p["area"] == pytest.approx(math.pi * 480 ** 2, rel=0.12)
    assert (p["cx"], p["cy"]) == (pytest.approx(1200, abs=30), pytest.approx(1200, abs=30))


def test_suggested_outline_on_empty_image():
    assert suggest_outline(np.full((100, 100), 50.0)) is None


def test_outline_file_round_trip(tmp_path):
    img = tmp_path / "B0" / "s1.png"
    img.parent.mkdir()
    img.write_bytes(b"")
    pr = empty_project()
    pr["pixel_um"] = 1.0
    pr["yarns"]["B0"] = dict(count=14, unit="Ne", tex=42.18, blend=[["cotton", 100, 1.52]], rho=1.52)
    pr["sections"].append(dict(label="B0", image=str(img), outline=circle(180, n=60), use=True))
    pr["sections"].append(dict(label="B0", image=str(img), outline=[], use=True))      # not outlined yet
    f = tmp_path / "outlines.json"
    save_outlines(str(f), pr, program="test")
    back = load_outlines(str(f))
    assert back["sections"][0]["image"] == str(img)
    rows, summary = evaluate(back)
    assert rows[1][1] is None and summary["B0"]["n"] == 1
    phi = 1000 * 42.18 / 1.52 / polygon_props(circle(180, n=60))["area"]
    assert summary["B0"]["phi_mean"] == pytest.approx(phi, rel=1e-3)
    # the command line gives the same value
    from yarnhair.cli import main
    out = tmp_path / "sections.tsv"
    assert main(["section", str(f), "--out", str(out)]) == 0
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0].split("\t")[:3] == ["label", "image", "use"] and len(lines) == 3
    assert float(lines[1].split("\t")[8]) == pytest.approx(phi, rel=1e-3)
