# YarnHair

[Türkçe](README.tr.md) | English

Rule-based measurement of yarn hairiness from microscope images, with a
graphical program (English/Turkish) and a command-line interface.

YarnHair finds the protruding fibres (hairs) on a microscope image of a straight
yarn segment that appears bright on a dark background, and reports, per 10 mm of
yarn:

| column | meaning |
|---|---|
| `N` | number of hairs |
| `L` | total hair length outside the yarn body (mm) |
| `N05`, `N1`, `N2`, `N3` | hairs whose tip reaches 0.5, 1, 2 and 3 mm from the body boundary |
| `mean_length` | mean hair length (mm) |
| `unresolved` | fibre fragments that could not be connected to the body (not counted) |

`L` follows the definition of the Uster hairiness index H (total protruding fibre
length, no lower distance threshold). `N1` corresponds to the 1 mm measuring height
preferred in ASTM D5647.

## Rules the method follows

1. **Every hair is attached to the yarn body.** A fragment is counted only if it
   can be connected to the body boundary: directly when it ends within 40 px of it,
   otherwise along the cheapest path through the ridge (fibre) map, which must lie
   mostly on fibre and be at most 1.6 × the gap + 30 px long. The connection is
   added to the hair length. Fragments that cannot be connected are reported as
   `unresolved`.
2. **Hair length is the length outside the body**, measured along the fibre from
   the tip to the body boundary, including hidden parts that are bridged.
3. **The body boundary is never narrower than the theoretical yarn diameter.**
   Boundary radius = max(theoretical radius, apparent half-maximum radius). The
   theoretical diameter comes from yarn count, fibre (blend) density and a
   packing density (default 0.32; see *Choosing the packing density*).
4. **No distance threshold cuts hairs.** Short or nearly parallel hairs count;
   the 0.5/1/2/3 mm classes are reported separately.
5. **Detection is by line shape, not brightness**: a multiscale ridge filter
   (Sato, σ = 1–3 px) with hysteresis thresholding; diffuse bright areas are
   not hairs.
6. Curled tips and loops belong to the hair they close on; crossing hairs are
   separated where the fibre continues straight through the junction.

Full details and all parameters: [docs/method.md](docs/method.md).

## Graphical program

Download the zip file for your computer from the **Releases** page
(`YarnHair-macOS-AppleSilicon.zip` for Macs with an Apple M-series chip,
`YarnHair-macOS-Intel.zip` for Macs with an Intel processor, or
`YarnHair-Windows.zip`), unzip it and double-click **YarnHair**. Nothing else
needs to be installed. The programs are not signed, so the system asks once:

- macOS: "YarnHair cannot be opened…" → **System Settings → Privacy & Security**
  → **Open Anyway** next to the YarnHair message.
- Windows: "Windows protected your PC" → **More info** → **Run anyway**.

The language is chosen in the **Language** menu (English / Türkçe). The window
follows the four steps of a measurement:

1. **Images** — add image files or a folder; every image gets a label (sample
   name). With *use sub-folder names as labels*, a folder `B0/…, B1/…` is
   labelled automatically.
2. **Pixel size** — type the µm per pixel at the yarn plane, or open an image of
   a stage micrometer taken at the same magnification, click two points of the
   scale and type their distance (e.g. 1000 µm); the program shows the
   calculation (µm ÷ pixels).
3. **Yarn and body boundary** — yarn count (tex, Ne, Nm, dtex or denier),
   spinning system and blend. Choose each fibre from the list and type its
   mass share; its density and source are filled in (Help → Fibre densities).
   Fibres not on the list: choose *Other* and type the density. Include the
   core of core-spun yarns. Then either
   - **enter the packing density** (default 0.32): the theoretical diameter is
     calculated, or
   - **enter a measured diameter** (from cross-sections or an optical side view):
     the packing density is calculated and checked.

   The packing density is compared with values stored from the literature
   (Help → Packing density references) for the same kind of measurement and
   spinning system, and the result is shown in colour under the inputs. A
   value ≥ 1 is impossible and cannot be used. For a value above 0.907
   (densest packing of round fibres) or more than 0.05 outside the range of
   the matching references, **Start** asks whether to correct the values, use
   the value anyway or, for a measured diameter, use the theoretical diameter.
4. **Run** — the frames are measured in parallel processes (each needs about
   1 GB of memory); checking images can be saved to a folder.

Results appear per frame (double-click a row to see its checking image) and as
mean ± SD per label. **File → Save results** writes an Excel workbook (frames,
summary per label, and all settings with the calculations) or a tab-separated
text file.

## Installation from source

Download the code (green **Code** button → **Download ZIP**, or the archive of
a release), unzip it, and run in that folder:

```bash
pip install .            # command line only
pip install ".[gui]"     # with the graphical program (PySide6, openpyxl)
yarnhair-gui             # start the graphical program
```

Python ≥ 3.9. The published values were reproduced exactly with numpy 2.2.6,
scipy 1.15.3 and scikit-image 0.25.2 (`packaging/requirements-app.txt`, also
used to build the downloadable programs); newer versions can differ by a few
tenths of a percent in `L`.

## Command line

```bash
# theoretical diameter of an Ne 14/1 yarn of cotton (density 1.52 g/cm3)
yarnhair diameter --ne 14 --density 1.52
# -> 332.3   (packing density 0.32; with --packing 0.6: 242.7)

# blend density from the fibre list (shares by mass)
yarnhair diameter --tex 42.18 --blend cotton=50,lyocell=25,pla=25
# -> 341.7

# measure all frames of one yarn; append to results.tsv; save checking images
yarnhair measure frames/B0/*.bmp --label B0 --diameter-um 331 \
         --pixel-um 3.85 --out results.tsv --overlay-dir overlays
```

From Python:

```python
from yarnhair import measure_frame
res, hairs, unresolved, details = measure_frame("frame.bmp", diameter_um=331, pixel_um=3.85)
print(res["N"], res["L"])
```

`yarnhair defaults` prints the default parameters; override them with
`--config '{"hi": 18}'`.

### Language

Both interfaces are available in English and Turkish. Command line:
`yarnhair --lang tr measure ...`, or set `YARNHAIR_LANG=tr` (default: the system
language, else English). Output column names and the data format of text files
(decimal point) are the same in both languages.

## Input images

- One straight yarn segment, roughly horizontal, brighter than the background
  (dark background).
- Known pixel size at the yarn plane, e.g. from a stage micrometer.
- The published analysis used 2592 × 1944 px frames at 3.85 µm/px
  (≈ 10 mm of yarn per frame), 25 frames per yarn, taken ≥ 1 m apart.
- Thresholds were tuned on four hand-traced frames for this set-up. Check them
  on a few hand-traced frames before using a different microscope,
  magnification or illumination.

## Checking images

For every frame a checking image can be saved: dashed white lines mark the body
boundary, each counted hair has its own colour (including its connection to the
body), and unresolved fragments are red. The checking image uses a fixed display
enhancement (background subtraction, fixed scale, gamma 0.5, unsharp mask);
measurements are always made on the raw image.

## Choosing the packing density

Packing density φ (also called packing fraction or fibre volume fraction) is the
share of the yarn cross-section filled by fibre. It is not a constant: it
depends on fibre, spinning system and twist, and above all on where the edge of
the yarn is drawn:

- cross-sections, edge drawn around the outermost fibres: about 0.24–0.42
  (Kilic et al. 2014; Demir 2023; Erbil et al. 2022);
- photographs of running yarn: 0.32–0.45 (Hearle et al. 1969, Table 2.8);
- yarn flattened by winding it on a spindle (coil winding): 0.53–0.61
  (Hearle et al. 1969, Table 2.9).

The body boundary in YarnHair is the outer edge of the yarn, so the default is a
cross-section value: 0.32, measured on cotton/elastane core-spun ring yarn, the
yarn type of the published analysis (Erbil et al. 2022). Use one value for all
yarns of a comparison, or a measured value per yarn if available.

In the published analysis, 0.6 instead of 0.32 made the boundary up to 27 %
narrower and raised hair counts and lengths by 16–29 %, with almost the same
ranking of the ten yarns (Spearman ρ ≥ 0.96). The published theoretical
diameters used the density of the staple sheath only (elastane core left out);
including the core, as the program asks, changes them by less than 1 %.

## Run time

About 15–80 s per 5-megapixel frame on a desktop CPU. Frames are independent,
so several processes run in parallel as far as memory allows.

## Reproducibility

Version 1.0.0 contains the algorithm and default parameters used for the
article below; its 275 frame values were produced with this code and the
library versions above. `yarnhair-gui
--selftest` (or `YarnHair --selftest` for the downloaded program) measures a
synthetic frame in a worker process and opens the window off-screen; exit code 0
means that the installation works.

## References

- Demir M (2023) Exploring the relationship between yarn type and packing
  density: a study of single-ply, two-ply, and siro-spun yarns. Tekstil ve
  Mühendis 30(130):124–130. https://doi.org/10.7216/teksmuh.1320576
- Erbil Y, Islam R, Babaarslan O, Sırlıbaş S (2022) Effect of structural
  changes on the cotton composite yarn properties. J Nat Fibers 19:1899–1907.
  https://doi.org/10.1080/15440478.2020.1788687
- Hearle JWS, Grosberg P, Backer S (1969) Structural mechanics of fibers,
  yarns, and fabrics, vol 1. Wiley-Interscience, New York.
- Kilic M, Buyukbayraktar RB, Kilic GB, Aydin S, Eski N (2014) Comparing the
  packing densities of yarns spun by ring, compact and vortex spinning systems
  using image analysis method. Indian J Fibre Text Res 39:351–357.

The sources of the stored fibre densities and the remaining packing-density
references are listed in the program (Help menu) and in `yarnhair/fibres.py`
and `yarnhair/packing.py`.

## How to cite

Please cite the software (see `CITATION.cff`, or the Zenodo DOI of the release)
and the article describing its first application:

> Celayir E, Erbil Y, Babaarslan O. Effect of ternary blends of cotton, hemp,
> TENCEL™, PLA, rPET and Naia™ on yarn quality, mechanical properties, air
> permeability and wettability of elastane core-spun denim weft. (submitted)

## Use of AI

The code was written with the help of a large language model (Claude,
Anthropic) from the author's specifications, and was revised after each check
against frames traced by hand. The images are processed only by the
rule-based code in this repository; no generative model creates or alters any
image or measurement.

## Licence

MIT — see [LICENSE](LICENSE).
