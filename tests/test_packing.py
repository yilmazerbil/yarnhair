"""Count units, blend density, packing density and the literature check."""
import math

import pytest

from yarnhair.fibres import FIBRES, SOURCES, blend_density, parse_blend
from yarnhair.packing import (CLOSE_PACKED, DEFAULT_PACKING, REF_SOURCES, REFERENCES, check_packing,
                              packing_from_diameter, theoretical_diameter_um, to_tex)


def test_default_packing():
    assert DEFAULT_PACKING == 0.32


@pytest.mark.parametrize("value, unit, tex", [(42.18, "tex", 42.18), (14, "Ne", 590.5 / 14), (20, "Nm", 50.0),
                                              (78, "dtex", 7.8), (90, "den", 10.0)])
def test_to_tex(value, unit, tex):
    assert to_tex(value, unit) == pytest.approx(tex)


def test_to_tex_rejects_bad_input():
    with pytest.raises(ValueError):
        to_tex(0, "tex")
    with pytest.raises(ValueError):
        to_tex(10, "yards")


def test_packing_round_trip():
    d = theoretical_diameter_um(42.18, 1.45, packing=0.37)
    assert packing_from_diameter(42.18, 1.45, d) == pytest.approx(0.37)


def test_blend_density_harmonic_mean():
    rho = blend_density(parse_blend("cotton=50,lyocell=25,pla=25"))
    assert rho == pytest.approx(1 / (0.5 / 1.52 + 0.25 / 1.50 + 0.25 / 1.25))
    # shares are normalised and 'other' takes a typed density
    assert blend_density([(1, 1.38)]) == pytest.approx(1.38)
    assert blend_density(parse_blend("cotton=94.9,other:1.21=5.1")) == pytest.approx(
        1 / (0.949 / 1.52 + 0.051 / 1.21))


def test_every_fibre_and_reference_has_a_source():
    for key, (_, _, rho, src, _) in FIBRES.items():
        assert 0.8 < rho < 1.6 and src in SOURCES, key
    for ref in REFERENCES:
        assert ref[5] in REF_SOURCES and 0 < ref[4] < 1, ref


def test_check_levels():
    assert check_packing(1.2)["level"] == "error"
    assert check_packing(0.95)["level"] == "warning" and 0.95 > CLOSE_PACKED
    ok = check_packing(0.32, "cross_section", "core_spun")
    assert ok["level"] == "ok" and ok["low"] == 0.25 and ok["high"] == 0.32
    assert check_packing(0.60, "cross_section", "ring")["level"] == "notice"
    # informational kinds are never compared with the literature
    assert check_packing(0.60, "coil_winding")["level"] == "ok"


def test_close_packing_value():
    assert CLOSE_PACKED == pytest.approx(math.pi / (2 * math.sqrt(3)))
