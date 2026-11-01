"""Fibre densities and blend density.

Every density in FIBRES comes from a source whose text was read; the source
key refers to SOURCES. Fibres without such a source are not listed: choose
"other" and type the density.

Blend density uses mass fractions: rho = 1 / sum(w_i / rho_i).
"""

SOURCES = {
    "eldessouki2016": "Eldessouki M, Ibrahim S (2016) Chan-Vese segmentation model for faster and "
                      "accurate evaluation of yarn packing density. Text Res J 86(2):167-177, Table 1",
    "dnfi": "Zimniewska M, Kicinska-Jakubowska A. Vegetable fibers sheet. Institute of Natural Fibres "
            "& Medicinal Plants / Discover Natural Fibres Initiative (dnfi.org)",
    "eastman_naia": "Eastman Naia(TM) Renew cellulosic fiber, 1.3 dtex 38 mm bright: technical data sheet",
    "avinc2009": "Avinc O, Khoddami A (2009) Overview of poly(lactic acid) (PLA) fibre. Part I. "
                 "Fibre Chem 41(6):391-401, Table 3",
    "hearle2001": "Hearle JWS, Hollick L, Wilson DK (2001) Yarn texturing technology. Woodhead, "
                  "Cambridge, Table 7.1 (data of the British Textile Technology Group)",
}

# Sources whose full text is still to be read (values shown with a note).
SOURCE_PENDING = {
    "eldessouki2016": "pre-print version read; published version to be checked",
    "dnfi": "PDF to be read",
}

SOURCE_SHORT = {
    "eldessouki2016": "Eldessouki & Ibrahim 2016",
    "dnfi": "Zimniewska & Kicińska-Jakubowska (DNFI)",
    "eastman_naia": "Eastman Naia\u2122 TDS",
    "avinc2009": "Avinc & Khoddami 2009",
    "hearle2001": "Hearle et al. 2001",
}

# key: (English name, Turkish name, density g/cm3, source key, note on the source value)
FIBRES = {
    "cotton":  ("Cotton", "Pamuk", 1.52, "eldessouki2016", ""),
    "hemp":    ("Hemp", "Kenevir", 1.48, "dnfi", "1.48-1.49"),
    "flax":    ("Flax (linen)", "Keten", 1.50, "dnfi", ""),
    "jute":    ("Jute", "Jüt", 1.46, "dnfi", "1.44-1.49"),
    "ramie":   ("Ramie", "Rami", 1.53, "dnfi", "1.51-1.55"),
    "viscose": ("Viscose", "Viskon", 1.50, "eldessouki2016", ""),
    "lyocell": ("Lyocell (e.g. TENCEL™)", "Liyosel (ör. TENCEL™)", 1.50, "eldessouki2016", ""),
    "acetate": ("Cellulose acetate (Naia™)", "Selüloz asetat (Naia™)", 1.32, "eastman_naia", ""),
    "pla":     ("PLA", "PLA", 1.25, "avinc2009", ""),
    "pet":     ("Polyester (PET, rPET)", "Polyester (PET, rPET)", 1.38, "hearle2001", ""),
    "pa":      ("Polyamide", "Poliamid", 1.17, "hearle2001", "1.17-1.18"),
    "pp":      ("Polypropylene", "Polipropilen", 0.91, "hearle2001", "0.90-0.93 (polyolefins)"),
}

OTHER = "other"


def fibre_name(key, lang="en"):
    if key == OTHER:
        return "Other" if lang == "en" else "Diğer"
    en, tr = FIBRES[key][:2]
    return tr if lang == "tr" else en


def fibre_density(key):
    return FIBRES[key][2]


def blend_density(components):
    """Density of a blend, g/cm3.

    components: list of (mass percent or fraction, density g/cm3). The shares
    are normalised, so percentages or fractions both work.
    """
    comps = [(float(w), float(r)) for w, r in components if float(w) > 0]
    if not comps:
        raise ValueError("no components")
    if any(r <= 0 for _, r in comps):
        raise ValueError("density must be positive")
    total = sum(w for w, _ in comps)
    return 1.0 / sum((w / total) / r for w, r in comps)


def parse_blend(text):
    """'cotton=50,lyocell=25,pla=25' or 'cotton=94.9,other:1.21=5.1' -> [(share, density)]."""
    out = []
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        name, share = item.split("=")
        name = name.strip().lower()
        if name.startswith(OTHER + ":"):
            dens = float(name.split(":", 1)[1])
        else:
            dens = fibre_density(name)
        out.append((float(share), dens))
    return out
