"""Yarn count, packing density and theoretical diameter.

Packing density (phi, also called packing fraction or fibre volume fraction)
is the share of the yarn cross-section occupied by fibre, 0 < phi < 1.
Its value depends on where the edge of the yarn is drawn, so literature
values are grouped by how the yarn diameter or area was obtained:

  cross_section  fibre area / yarn area on cross-sections; the yarn area is
                 drawn around the outermost fibres (envelope)
  optical        count-based value from an optical (side-view) diameter, e.g.
                 Uster 2DO: phi = yarn density / fibre density
  effective      Liberec "effective diameter" (radial packing density 0.15);
                 listed for information, not used in the checks
  coil_winding   yarn wound under tension on a spindle and flattened (Hamilton
                 1959, in Hearle et al. 1969); compressed yarn, listed for
                 information, not used in the checks

A value computed from the user's diameter is compared only with references
of the same kind. Values marked approx were read from a bar chart.
"""
import math

DEFAULT_PACKING = 0.32   # Erbil et al. 2022, cotton/elastane core-spun ring yarn (cross-sections)
CLOSE_PACKED = math.pi / (2 * math.sqrt(3))   # 0.9069, densest packing of equal circles
MARGIN = 0.05            # tolerance around the range of matching references

COUNT_UNITS = ("tex", "Ne", "Nm", "dtex", "den")

SYSTEMS = ("ring", "compact", "vortex", "siro", "two_ply", "core_spun", "other")
SYSTEM_NAMES = {
    "ring": ("Ring", "Ring"), "compact": ("Compact", "Kompakt"), "vortex": ("Vortex", "Vorteks"),
    "siro": ("Siro", "Siro"), "two_ply": ("Two-ply", "İki katlı"),
    "core_spun": ("Core-spun", "Özlü (core-spun)"), "other": ("Other", "Diğer"),
}
DIAMETER_TYPES = ("cross_section", "optical", "other")

REF_SOURCES = {
    "erbil2022": "Erbil Y, Islam R, Babaarslan O, Sırlıbaş S (2022) Effect of structural changes on the "
                 "cotton composite yarn properties. J Nat Fibers 19:1899-1907. doi:10.1080/15440478.2020.1788687",
    "kilic2014": "Kilic M, Buyukbayraktar RB, Kilic GB, Aydin S, Eski N (2014) Comparing the packing "
                 "densities of yarns spun by ring, compact and vortex spinning systems using image "
                 "analysis method. Indian J Fibre Text Res 39:351-357",
    "demir2023": "Demir M (2023) Exploring the relationship between yarn type and packing density: a study "
                 "of single-ply, two-ply, and siro-spun yarns. Tekstil ve Mühendis 30(130):124-130. "
                 "doi:10.7216/teksmuh.1320576",
    "eldessouki2016": "Eldessouki M, Ibrahim S (2016) Chan-Vese segmentation model for faster and accurate "
                      "evaluation of yarn packing density. Text Res J 86(2):167-177",
    "hearle1969": "Hearle JWS, Grosberg P, Backer S (1969) Structural mechanics of fibers, yarns, and fabrics, "
                  "Vol 1. Wiley-Interscience, New York. Table 2.8 (photographic method, van Issum and "
                  "Chamberlain 1959) and Table 2.9 (coil winding, Hamilton 1959)",
}

# (kind, system, fibre, tex, value, source, note)
REFERENCES = [
    ("cross_section", "ring", "cotton", 36.9, 0.34, "erbil2022", ""),
    ("cross_section", "core_spun", "cotton / elastane core", 36.9, 0.32, "erbil2022", ""),
    ("cross_section", "core_spun", "cotton / elastane + PBT core", 36.9, 0.25, "erbil2022", ""),
    ("cross_section", "ring", "lyocell", 19.69, 0.38, "kilic2014", ""),
    ("cross_section", "compact", "lyocell", 19.69, 0.42, "kilic2014", ""),
    ("cross_section", "vortex", "lyocell", 19.69, 0.24, "kilic2014", ""),
    ("cross_section", "ring", "micro modal", 29.5, 0.382, "demir2023", "approx"),
    ("cross_section", "ring", "polyester", 29.5, 0.382, "demir2023", "approx"),
    ("cross_section", "ring", "lyocell", 29.5, 0.387, "demir2023", "approx"),
    ("cross_section", "ring", "cotton", 29.5, 0.349, "demir2023", "approx"),
    ("cross_section", "siro", "micro modal", 29.5, 0.395, "demir2023", "approx"),
    ("cross_section", "siro", "polyester", 29.5, 0.402, "demir2023", "approx"),
    ("cross_section", "siro", "lyocell", 29.5, 0.398, "demir2023", "approx"),
    ("cross_section", "siro", "cotton", 29.5, 0.350, "demir2023", "approx"),
    ("cross_section", "two_ply", "micro modal", 29.5, 0.330, "demir2023", "approx"),
    ("cross_section", "two_ply", "polyester", 29.5, 0.346, "demir2023", "approx"),
    ("cross_section", "two_ply", "lyocell", 29.5, 0.355, "demir2023", "approx"),
    ("cross_section", "two_ply", "cotton", 29.5, 0.325, "demir2023", "approx"),
    # Uster yarn density / fibre density (lyocell 1.50, cotton 1.52, polyester 1.38; see fibres.py)
    ("optical", "ring", "lyocell", 19.69, 0.44, "kilic2014", "Uster 2DØ"),
    ("optical", "compact", "lyocell", 19.69, 0.447, "kilic2014", "Uster 2DØ"),
    ("optical", "vortex", "lyocell", 19.69, 0.387, "kilic2014", "Uster 2DØ"),
    ("optical", "ring", "polyester", 29.5, 0.442, "demir2023", "Uster 2DØ, approx"),
    ("optical", "ring", "lyocell", 29.5, 0.407, "demir2023", "Uster 2DØ, approx"),
    ("optical", "ring", "cotton", 29.5, 0.309, "demir2023", "Uster 2DØ, approx"),
    ("optical", "siro", "polyester", 29.5, 0.464, "demir2023", "Uster 2DØ, approx"),
    ("optical", "siro", "lyocell", 29.5, 0.420, "demir2023", "Uster 2DØ, approx"),
    ("optical", "siro", "cotton", 29.5, 0.329, "demir2023", "Uster 2DØ, approx"),
    ("optical", "two_ply", "polyester", 29.5, 0.290, "demir2023", "Uster 2DØ, approx"),
    ("optical", "two_ply", "lyocell", 29.5, 0.273, "demir2023", "Uster 2DØ, approx"),
    ("optical", "two_ply", "cotton", 29.5, 0.217, "demir2023", "Uster 2DØ, approx"),
    # running yarn photographed, blurred edge averaged (Hearle et al. 1969, Table 2.8)
    ("optical", "ring", "cotton", None, 0.358, "hearle1969", "photographic"),
    ("optical", "ring", "spun rayon", None, 0.427, "hearle1969", "photographic"),
    ("optical", "other", "worsted", None, 0.452, "hearle1969", "photographic"),
    ("optical", "other", "woollen", None, 0.321, "hearle1969", "photographic"),
    ("effective", "ring", "lyocell", 20.0, 0.453, "eldessouki2016", "measured fibre area"),
    ("effective", "ring", "viscose", 16.0, 0.414, "eldessouki2016", "measured fibre area"),
    ("effective", "ring", "cotton", 16.0, 0.387, "eldessouki2016", "measured fibre area"),
    # Hearle et al. 1969, Table 2.9 (Hamilton 1959): cotton-spun staple yarns, twist factor 33 tex^0.5 turns/cm
    ("coil_winding", "ring", "rayon 1.5 den", 29.5, 0.61, "hearle1969", ""),
    ("coil_winding", "ring", "rayon 3 den", 31.3, 0.59, "hearle1969", ""),
    ("coil_winding", "ring", "rayon 3 den", 30.3, 0.58, "hearle1969", ""),
    ("coil_winding", "ring", "acetate", 31.9, 0.59, "hearle1969", ""),
    ("coil_winding", "ring", "triacetate", 28.8, 0.55, "hearle1969", ""),
    ("coil_winding", "ring", "acrylic", 27.0, 0.54, "hearle1969", ""),
    ("coil_winding", "ring", "nylon", 27.4, 0.60, "hearle1969", ""),
    ("coil_winding", "ring", "polyester", 33.6, 0.56, "hearle1969", ""),
    ("coil_winding", "ring", "cotton", 32.0, 0.53, "hearle1969", ""),
]


def to_tex(value, unit):
    """Linear density in tex from tex, Ne (English cotton count), Nm, dtex or denier."""
    v = float(value)
    if v <= 0:
        raise ValueError("count must be positive")
    if unit == "tex":
        return v
    if unit == "Ne":
        return 590.5 / v
    if unit == "Nm":
        return 1000.0 / v
    if unit == "dtex":
        return v / 10.0
    if unit == "den":
        return v / 9.0
    raise ValueError(f"unknown count unit {unit}")


def ne_to_tex(ne):
    return to_tex(ne, "Ne")


def substance_area_um2(tex, density_g_cm3):
    """Cross-sectional area of the fibre material alone (no air), um2."""
    return (tex / 1e5) / density_g_cm3 * 1e8


def theoretical_diameter_um(tex, density_g_cm3, packing=DEFAULT_PACKING):
    """Diameter (um) of a circular yarn of this count, density and packing density:
    d = sqrt(4 T / (1000 pi phi rho)) with T in tex, rho in g/cm3, d in mm."""
    if not 0 < packing <= 1:
        raise ValueError("packing density must be in (0, 1]")
    area = substance_area_um2(tex, density_g_cm3) / packing
    return math.sqrt(4 * area / math.pi)


def packing_from_diameter(tex, density_g_cm3, diameter_um):
    """Packing density implied by a measured diameter: phi = 4 T / (1000 pi d^2 rho)."""
    if diameter_um <= 0:
        raise ValueError("diameter must be positive")
    return substance_area_um2(tex, density_g_cm3) / (math.pi * diameter_um ** 2 / 4)


def references(kind, system=None):
    """References of one kind; restricted to the spinning system when it has any."""
    refs = [r for r in REFERENCES if r[0] == kind]
    if system and system != "other":
        same = [r for r in refs if r[1] == system]
        if same:
            return same
    return refs


def check_packing(phi, kind="cross_section", system=None):
    """Compare a packing density with physical limits and with the literature.

    Returns dict(level, phi, kind, refs, low, high), where level is
      "error"   phi >= 1: impossible,
      "warning" phi above the densest packing of equal round fibres (0.907),
      "notice"  outside the matching references' range by more than MARGIN,
      "ok"      otherwise ("ok" also when there are no matching references).
    """
    out = dict(phi=phi, kind=kind, refs=[], low=None, high=None)
    if phi >= 1:
        out["level"] = "error"
        return out
    if phi > CLOSE_PACKED:
        out["level"] = "warning"
        return out
    refs = references(kind, system) if kind in ("cross_section", "optical") else []
    out["refs"] = refs
    if refs:
        vals = [r[4] for r in refs]
        out["low"], out["high"] = min(vals), max(vals)
        if phi < out["low"] - MARGIN or phi > out["high"] + MARGIN:
            out["level"] = "notice"
            return out
    out["level"] = "ok"
    return out
