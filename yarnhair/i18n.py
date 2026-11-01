"""Interface language (English / Türkçe).

The language is chosen with --lang, else the YARNHAIR_LANG environment
variable, else the system language (Turkish if it starts with "tr"), else
English. Only the interface is translated; output column names and the data
file format (decimal point) are the same in both languages.
"""
import locale
import os

LANGS = ("en", "tr")

MESSAGES = {
    "description": {
        "en": "Yarn hairiness from microscope images",
        "tr": "Mikroskop görüntülerinden iplik tüylülüğü ölçümü",
    },
    "lang_help": {
        "en": "interface language: en (English) or tr (Türkçe); default: YARNHAIR_LANG or the system language",
        "tr": "arayüz dili: en (English) ya da tr (Türkçe); varsayılan: YARNHAIR_LANG ya da sistem dili",
    },
    "commands": {"en": "commands", "tr": "komutlar"},
    "measure_help": {
        "en": "measure hairiness in one or more frames",
        "tr": "bir ya da daha çok karede tüylülüğü ölç",
    },
    "images_help": {
        "en": "image files (one yarn frame each)",
        "tr": "görüntü dosyaları (her biri bir iplik karesi)",
    },
    "out_help": {
        "en": "tab-separated output file (rows are appended)",
        "tr": "sekmeyle ayrılmış çıktı dosyası (satırlar sona eklenir)",
    },
    "label_help": {
        "en": "sample label written to every row",
        "tr": "her satıra yazılan numune etiketi",
    },
    "diameter_um_help": {
        "en": "theoretical yarn diameter in µm; body boundary = max(theoretical, apparent); 0 = apparent diameter only",
        "tr": "teorik iplik çapı, µm; gövde sınırı = en büyüğü(teorik, görünür); 0 = yalnız görünür çap",
    },
    "pixel_um_help": {
        "en": "pixel size at the yarn plane, µm (default 3.85)",
        "tr": "iplik düzleminde piksel boyutu, µm (varsayılan 3,85)",
    },
    "config_help": {
        "en": "JSON with parameter overrides, e.g. '{\"hi\": 18}' (see the 'defaults' command)",
        "tr": "değiştirilecek parametreler (JSON), ör. '{\"hi\": 18}' ('defaults' komutuna bakın)",
    },
    "overlay_dir_help": {
        "en": "save checking images (PNG) in this folder",
        "tr": "kontrol görüntülerini (PNG) bu klasöre kaydet",
    },
    "overlay_scale_help": {
        "en": "size factor of the checking images (default 0.5)",
        "tr": "kontrol görüntülerinin boyut katsayısı (varsayılan 0,5)",
    },
    "geometry_dir_help": {
        "en": "save hair pixel coordinates (.npz) in this folder",
        "tr": "tüy piksel koordinatlarını (.npz) bu klasöre kaydet",
    },
    "diameter_help": {
        "en": "theoretical yarn diameter (µm) from count, density and packing density",
        "tr": "numara, yoğunluk ve paketleme yoğunluğundan teorik iplik çapı (µm)",
    },
    "tex_help": {"en": "linear density, tex", "tr": "doğrusal yoğunluk, tex"},
    "ne_help": {"en": "English cotton count, Ne", "tr": "İngiliz pamuk numarası, Ne"},
    "density_help": {
        "en": "fibre (blend) density, g/cm³",
        "tr": "lif (karışım) yoğunluğu, g/cm³",
    },
    "blend_help": {
        "en": "blend by mass, e.g. 'cotton=50,lyocell=25,pla=25' or 'other:1.21=5' (see fibres.py)",
        "tr": "kütlece karışım, ör. 'cotton=50,lyocell=25,pla=25' ya da 'other:1.21=5' (fibres.py'ye bakın)",
    },
    "blend_error": {
        "en": "--blend could not be read: {err}",
        "tr": "--blend okunamadı: {err}",
    },
    "packing_help": {
        "en": "packing density (default 0.32, Erbil et al. 2022)",
        "tr": "paketleme yoğunluğu (varsayılan 0,32, Erbil ve ark. 2022)",
    },
    "defaults_help": {
        "en": "print the default parameters",
        "tr": "varsayılan parametreleri yazdır",
    },
    "measured": {
        "en": "{file}: N={N}  L={L} mm (per 10 mm of yarn), unresolved={q}",
        "tr": "{file}: N={N}  L={L} mm (10 mm iplik başına), bağlanamayan={q}",
    },
    "frame_error": {
        "en": "{file}: could not be processed ({err}); skipped",
        "tr": "{file}: işlenemedi ({err}); atlandı",
    },
    "config_error": {
        "en": "--config is not valid JSON: {err}",
        "tr": "--config geçerli bir JSON değil: {err}",
    },
    "summary": {
        "en": "{n} frame(s) written to {out}",
        "tr": "{n} kare {out} dosyasına yazıldı",
    },
    "failed": {
        "en": "{n} frame(s) could not be processed",
        "tr": "{n} kare işlenemedi",
    },
    # placeholders shown in the help text
    "mv_file": {"en": "FILE", "tr": "DOSYA"},
    "mv_label": {"en": "LABEL", "tr": "ETİKET"},
    "mv_diameter": {"en": "DIAMETER", "tr": "ÇAP"},
    "mv_size": {"en": "SIZE", "tr": "BOYUT"},
    "mv_folder": {"en": "FOLDER", "tr": "KLASÖR"},
    "mv_factor": {"en": "FACTOR", "tr": "KATSAYI"},
    "mv_image": {"en": "IMAGE", "tr": "GÖRÜNTÜ"},
    "mv_density": {"en": "DENSITY", "tr": "YOĞUNLUK"},
    "mv_fraction": {"en": "PHI", "tr": "PHI"},
    "mv_blend": {"en": "BLEND", "tr": "KARIŞIM"},
}

# Built-in argparse texts (Python 3.9-3.13); untranslated texts stay in English.
ARGPARSE_TR = {
    "usage: ": "kullanım: ",
    "positional arguments": "konumsal argümanlar",
    "options": "seçenekler",
    "optional arguments": "seçenekler",
    "show this help message and exit": "bu yardım iletisini göster ve çık",
    "show program's version number and exit": "program sürümünü göster ve çık",
    "%(prog)s: error: %(message)s\n": "%(prog)s: hata: %(message)s\n",
    "the following arguments are required: %s": "şu argümanlar gerekli: %s",
    "unrecognized arguments: %s": "tanınmayan argümanlar: %s",
    "invalid choice: %(value)r (choose from %(choices)s)": "geçersiz seçim: %(value)r (seçenekler: %(choices)s)",
    "argument %(argument_name)s: %(message)s": "argüman %(argument_name)s: %(message)s",
    "expected one argument": "bir değer bekleniyor",
    "one of the arguments %s is required": "şu argümanlardan biri gerekli: %s",
    "not allowed with argument %s": "şu argümanla birlikte kullanılamaz: %s",
    "invalid %(type)s value: %(value)r": "geçersiz %(type)s değeri: %(value)r",
    "ambiguous option: %(option)s could match %(matches)s": "belirsiz seçenek: %(option)s şunlardan biri olabilir: %(matches)s",
}


def detect_lang(argv=None):
    """Language from --lang in argv, YARNHAIR_LANG, or the system locale."""
    argv = list(argv or [])
    for i, a in enumerate(argv):
        if a == "--lang" and i + 1 < len(argv):
            v = argv[i + 1].lower()
            return v if v in LANGS else "en"
        if a.startswith("--lang="):
            v = a.split("=", 1)[1].lower()
            return v if v in LANGS else "en"
    env = os.environ.get("YARNHAIR_LANG", "").lower()
    if env in LANGS:
        return env
    loc = ""
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        if os.environ.get(var):
            loc = os.environ[var]
            break
    if not loc:
        try:
            loc = locale.getlocale()[0] or ""
        except ValueError:
            loc = ""
    return "tr" if loc.lower().startswith("tr") else "en"


def t(key, lang, **kw):
    """Translated message; numbers passed as floats get a decimal comma in Turkish."""
    if not kw:
        return MESSAGES[key][lang]
    if lang == "tr":
        kw = {k: (f"{v:.1f}".replace(".", ",") if isinstance(v, float) else v) for k, v in kw.items()}
    else:
        kw = {k: (f"{v:.1f}" if isinstance(v, float) else v) for k, v in kw.items()}
    return MESSAGES[key][lang].format(**kw)


def install_argparse_translation(lang):
    """Translate argparse's own texts (usage, error prefix, -h help ...)."""
    import argparse
    import gettext

    if lang == "tr":
        argparse._ = lambda s: ARGPARSE_TR.get(s, s)
    else:
        argparse._ = gettext.gettext
