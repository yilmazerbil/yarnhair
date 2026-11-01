"""Summaries and result files (TSV, Excel). No Qt imports here."""
import csv
import math
import os

from ..cli import COLUMNS

EXTRA = ["pixel_um", "diameter_um"]
SUMMARY_KEYS = ["N", "L", "N05", "N1", "N2", "N3", "mean_length", "apparent_diameter_um"]


def frame_row(r):
    row = [r["label"], os.path.basename(r["path"])]
    for k in COLUMNS[2:]:
        row.append(r[k])
    return row + [r["pixel_um"], r["diameter_um"]]


def summarise(results):
    """{label: {"n": n, key: (mean, sd)}} in the order labels first appear."""
    groups = {}
    for r in results:
        groups.setdefault(r["label"], []).append(r)
    out = {}
    for lab, rs in groups.items():
        d = {"n": len(rs)}
        for k in SUMMARY_KEYS:
            if k == "apparent_diameter_um":
                v = [x["apparent_diameter_px"] * x["pixel_um"] for x in rs]
            else:
                v = [float(x[k]) for x in rs]
            m = sum(v) / len(v)
            sd = math.sqrt(sum((a - m) ** 2 for a in v) / (len(v) - 1)) if len(v) > 1 else float("nan")
            d[k] = (m, sd)
        out[lab] = d
    return out


def write_tsv(path, results):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(COLUMNS + EXTRA)
        for r in results:
            row = frame_row(r)
            w.writerow([f"{v:.4f}" if isinstance(v, float) else v for v in row])


def write_xlsx(path, results, settings, names):
    """settings: list of (name, value); names: dict of sheet titles."""
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook()
    ws = wb.active
    ws.title = names["frames"]
    ws.append(COLUMNS + EXTRA)
    for r in results:
        ws.append(frame_row(r))
    for c in ws[1]:
        c.font = Font(bold=True)
    ws.freeze_panes = "A2"

    ws2 = wb.create_sheet(names["summary"])
    head = ["label", "n"]
    for k in SUMMARY_KEYS:
        head += [f"{k}_mean", f"{k}_sd"]
    ws2.append(head)
    for lab, d in summarise(results).items():
        row = [lab, d["n"]]
        for k in SUMMARY_KEYS:
            m, sd = d[k]
            row += [m, None if math.isnan(sd) else sd]
        ws2.append(row)
    for c in ws2[1]:
        c.font = Font(bold=True)

    ws3 = wb.create_sheet(names["settings"])
    for name, value in settings:
        ws3.append([name, value])
    ws3.column_dimensions["A"].width = 34
    ws3.column_dimensions["B"].width = 60
    wb.save(path)
