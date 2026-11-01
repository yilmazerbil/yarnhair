"""Command-line interface (English / Türkçe: --lang en|tr).

  yarnhair measure IMAGE [IMAGE ...] --diameter-um 242 --out results.tsv
  yarnhair diameter --ne 14 --density 1.52
  yarnhair --lang tr measure ...
"""
import argparse
import csv
import json
import os
import sys

import numpy as np

from . import __version__
from .i18n import LANGS, detect_lang, install_argparse_translation, t
from .measure import DEFAULT_CONFIG, measure_frame
from .packing import DEFAULT_PACKING, theoretical_diameter_um, ne_to_tex
from .fibres import blend_density, parse_blend

# Column names are the same in every interface language (see README).
COLUMNS = ["label", "frame", "apparent_diameter_px", "boundary_radius_px", "N", "L",
           "N05", "N1", "N2", "N3", "unresolved", "mean_length"]


def _measure(a, lang):
    try:
        cfg = json.loads(a.config) if a.config else None
    except json.JSONDecodeError as e:
        print(t("config_error", lang, err=e), file=sys.stderr)
        return 2
    new = not os.path.exists(a.out) or os.path.getsize(a.out) == 0
    done = failed = 0
    with open(a.out, "a", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        if new:
            w.writerow(COLUMNS)
        for fn in a.images:
            try:
                res, acc, q, D = measure_frame(fn, a.diameter_um, a.pixel_um, cfg)
            except Exception as e:  # unreadable or unsuitable image: report and continue
                print(t("frame_error", lang, file=fn, err=e), file=sys.stderr, flush=True)
                failed += 1
                continue
            row = [a.label, os.path.basename(fn)] + [
                f"{res[k]:.4f}" if isinstance(res[k], float) else res[k] for k in COLUMNS[2:]]
            w.writerow(row)
            fh.flush()
            done += 1
            base = os.path.splitext(os.path.basename(fn))[0]
            prefix = f"{a.label}_{base}" if a.label else base
            if a.overlay_dir:
                from .overlay import render
                os.makedirs(a.overlay_dir, exist_ok=True)
                render(D, acc, q, os.path.join(a.overlay_dir, prefix + ".png"), scale=a.overlay_scale)
            if a.geometry_dir:
                os.makedirs(a.geometry_dir, exist_ok=True)
                keep = {}
                for i, x in enumerate(acc + q):
                    pts = np.argwhere(np.isin(D["H3"], x["members"]))
                    keep[f"{'a' if i < len(acc) else 'q'}{i}"] = pts.astype(np.int16)
                np.savez_compressed(os.path.join(a.geometry_dir, prefix + ".npz"), **keep)
            print(t("measured", lang, file=fn, N=float(res["N"]), L=float(res["L"]), q=res["unresolved"]),
                  flush=True)
    print(t("summary", lang, n=done, out=a.out))
    if failed:
        print(t("failed", lang, n=failed), file=sys.stderr)
        return 1
    return 0


def _diameter(a, lang):
    tex = a.tex if a.tex else ne_to_tex(a.ne)
    if a.blend:
        try:
            rho = blend_density(parse_blend(a.blend))
        except (KeyError, ValueError) as e:
            print(t("blend_error", lang, err=e), file=sys.stderr)
            return 2
    else:
        rho = a.density
    print(f"{theoretical_diameter_um(tex, rho, a.packing):.1f}")
    return 0


def _defaults(a, lang):
    print(json.dumps(DEFAULT_CONFIG, indent=2))
    return 0


def build_parser(lang):
    install_argparse_translation(lang)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--lang", choices=LANGS, default=lang, help=t("lang_help", lang))
    p = argparse.ArgumentParser(prog="yarnhair", description=t("description", lang), parents=[common])
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True, title=t("commands", lang), metavar="{measure,diameter,defaults}")

    m = sub.add_parser("measure", parents=[common], help=t("measure_help", lang), description=t("measure_help", lang))
    m.add_argument("images", nargs="+", metavar=t("mv_image", lang), help=t("images_help", lang))
    m.add_argument("--out", required=True, metavar=t("mv_file", lang), help=t("out_help", lang))
    m.add_argument("--label", default="", metavar=t("mv_label", lang), help=t("label_help", lang))
    m.add_argument("--diameter-um", type=float, default=0.0, metavar=t("mv_diameter", lang), help=t("diameter_um_help", lang))
    m.add_argument("--pixel-um", type=float, default=3.85, metavar=t("mv_size", lang), help=t("pixel_um_help", lang))
    m.add_argument("--config", default="", metavar="JSON", help=t("config_help", lang))
    m.add_argument("--overlay-dir", default="", metavar=t("mv_folder", lang), help=t("overlay_dir_help", lang))
    m.add_argument("--overlay-scale", type=float, default=0.5, metavar=t("mv_factor", lang), help=t("overlay_scale_help", lang))
    m.add_argument("--geometry-dir", default="", metavar=t("mv_folder", lang), help=t("geometry_dir_help", lang))
    m.set_defaults(func=_measure)

    d = sub.add_parser("diameter", parents=[common], help=t("diameter_help", lang), description=t("diameter_help", lang))
    g = d.add_mutually_exclusive_group(required=True)
    g.add_argument("--tex", type=float, metavar="TEX", help=t("tex_help", lang))
    g.add_argument("--ne", type=float, metavar="NE", help=t("ne_help", lang))
    r = d.add_mutually_exclusive_group(required=True)
    r.add_argument("--density", type=float, metavar=t("mv_density", lang), help=t("density_help", lang))
    r.add_argument("--blend", metavar=t("mv_blend", lang), help=t("blend_help", lang))
    d.add_argument("--packing", type=float, default=DEFAULT_PACKING, metavar=t("mv_fraction", lang), help=t("packing_help", lang))
    d.set_defaults(func=_diameter)

    c = sub.add_parser("defaults", parents=[common], help=t("defaults_help", lang), description=t("defaults_help", lang))
    c.set_defaults(func=_defaults)
    return p


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    lang = detect_lang(argv)
    a = build_parser(lang).parse_args(argv)
    return a.func(a, a.lang)


if __name__ == "__main__":
    sys.exit(main())
