"""Synthetic check: a bright horizontal yarn with a few straight hairs."""
import numpy as np
from skimage.draw import line_aa

from yarnhair import measure_frame, theoretical_diameter_um, ne_to_tex


def synthetic(n_hairs=6, seed=0):
    rng = np.random.default_rng(seed)
    H, W = 900, 1200
    X = 20 + rng.normal(0, 1.5, (H, W))
    yc, r = H // 2, 30
    yy = np.arange(H)[:, None]
    X += 200 * np.exp(-((yy - yc) / r) ** 8)          # flat-topped bright body
    xs = np.linspace(100, W - 100, n_hairs).astype(int)
    for i, x in enumerate(xs):
        s = -1 if i % 2 else 1
        y0 = yc + s * (r - 2)
        y1 = yc + s * (r + 150)
        rr, cc, v = line_aa(y0, x, y1, x + 40)
        X[rr, cc] += 120 * v
    return X


def test_counts_straight_hairs():
    res, acc, q, D = measure_frame(synthetic(), diameter_um=0, pixel_um=3.85)
    per_frame = res["N"] / (10 / (1200 * 3.85e-3))
    assert round(per_frame) == 6
    assert res["L"] > 0


def test_theoretical_diameter():
    # default packing density 0.32 (Erbil et al. 2022)
    assert abs(theoretical_diameter_um(ne_to_tex(14), 1.52) - 332.3) < 0.05
    assert abs(theoretical_diameter_um(ne_to_tex(14), 1.52, packing=0.6) - 242.7) < 0.05


def test_cli_languages(capsys):
    import pytest
    from yarnhair.cli import main
    assert main(["--lang", "tr", "diameter", "--ne", "14", "--density", "1.52"]) == 0
    assert capsys.readouterr().out.strip() == "332.3"
    assert main(["diameter", "--ne", "14", "--density", "1.52", "--packing", "0.6"]) == 0
    assert capsys.readouterr().out.strip() == "242.7"
    assert main(["diameter", "--tex", "42.18", "--blend", "cotton=50,lyocell=25,pla=25"]) == 0
    assert capsys.readouterr().out.strip() == "341.7"
    with pytest.raises(SystemExit):
        main(["--lang", "tr", "--help"])
    out = capsys.readouterr().out
    assert "kullanım" in out and "komutlar" in out
    with pytest.raises(SystemExit):
        main(["--lang", "en", "--help"])
    out = capsys.readouterr().out
    assert "usage" in out and "commands" in out


def test_all_messages_have_both_languages():
    from yarnhair.i18n import MESSAGES, LANGS
    for key, d in MESSAGES.items():
        assert set(d) == set(LANGS), key


def test_regression_values():
    """Locks the measurement core: any change in the algorithm or its
    defaults changes these numbers (values of version 1.0.0).

    One hair end of this synthetic frame lies on a rounding boundary, so x86-64
    and ARM64 processors (Apple M chips, ARM Linux) give total and mean hair
    lengths that differ by 0.3 %; both are locked. Published frames measured on
    both processor types gave identical values (README, Reproducibility)."""
    import platform
    res, *_ = measure_frame(synthetic(), diameter_um=0, pixel_um=3.85)
    expected = dict(apparent_diameter_px=58, boundary_radius_px=29.0, N=12.987013,
                    N05=12.987013, N1=0.0, unresolved=0)
    if platform.machine().lower() in ("arm64", "aarch64"):
        expected.update(L=7.466667, mean_length=0.574933)
    else:
        expected.update(L=7.441667, mean_length=0.573008)
    for k, v in expected.items():
        assert abs(res[k] - v) <= 1e-5 * max(1.0, abs(v)), (k, res[k], v)
