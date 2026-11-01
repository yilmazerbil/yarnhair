# Changelog

## 1.0.0 (unreleased)
First public release.
- Graphical program (PySide6) in English and Turkish: image list with labels,
  two-click pixel-size calibration on a stage-micrometer image, yarn count in
  tex/Ne/Nm/dtex/den, blend calculator with stored fibre densities and their
  sources, packing density entered directly or calculated from a measured
  diameter and checked against stored literature values, parallel processing,
  checking-image viewer, summary per label, Excel and text output.
- Default packing density of the theoretical diameter 0.32 (cross-sections of
  cotton/elastane core-spun ring yarn, Erbil et al. 2022); the published
  analysis was re-run with this value.
- `yarnhair diameter --blend` and count units; `--selftest` for installed and
  downloadable programs.
- Double-click programs for macOS and Windows built by GitHub Actions with the
  library versions that reproduce the published values.
- Detection and measurement code used for the hairiness results of the
  accompanying article, reorganised into a package with a command-line
  interface; the detection algorithm and its parameters are unchanged (identical frame
  results checked on two published frames).
- Command-line interface in English and Turkish (`--lang en|tr`, or
  `YARNHAIR_LANG`); README in both languages (README.md, README.tr.md).
