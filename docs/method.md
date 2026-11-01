# Method and parameters

All distances in pixels (px) unless stated; the published set-up had 3.85 µm/px.

## 1. Yarn body

- In every 8th column the brightness profile (9 px moving average) is cut at half
  its maximum above the image median; the midpoint and width of that cut give the
  local centre and apparent diameter.
- A straight line y = m·x + b is fitted to the centres (yarn axis); the median width
  is the apparent diameter.
- Body boundary: two lines parallel to the axis at radius
  `Rb = max(theoretical diameter / 2, apparent diameter / 2)`.
- Theoretical diameter: `d = sqrt(4·tex / (π·ρ·φ·10^5))` cm, with ρ the fibre (blend)
  density in g/cm³ and packing density φ (default 0.32, cross-sections of cotton/elastane
  core-spun ring yarn, Erbil et al. 2022; `yarnhair diameter`). Blend density from mass
  shares wᵢ: `ρ = 1 / Σ(wᵢ/ρᵢ)`.
- From a measured diameter d the packing density is `φ = 4·tex / (π·ρ·d²·10^5)`.

## 2. Fibre (ridge) map

- Background: 151 px box filter of the image clipped at its 40th percentile; subtracted.
- Sato ridge filter for bright ridges, σ = 1, 2, 3 px.
- Normalisation to the far background (pixels ≥ 400 px from the body edge):
  z = (R − median) / (1.4826·MAD).

## 3. Segmentation

| parameter | default | meaning |
|---|---|---|
| `lo`, `hi` | 3, 20 | hysteresis thresholds on z |
| `zone_px`, `zone_k` | 40, 3 | inside 40 px of the boundary thresholds are ×3 (suppresses the halo around the body) |
| — | 12 px | objects smaller than this are removed |
| `spur` | 25 | side branches shorter than this are pruned |

## 4. Hair graph

- Skeleton split at junctions. At a junction, arms are paired when the fibre
  continues within 60° (crossing hairs stay separate); a junction with only two arms
  is joined; a loop returning to the same junction belongs to the hair it closes on.
- Gap bridging: free ends of different hairs ≤ 120 px apart are joined with a cubic
  Bézier curve along their directions when both turn ≤ 45° (gap ≤ 20 px) or ≤ 30°
  (longer gaps), the lateral offset is ≤ 0.3 × gap, and the curve does not enter the
  body. The bridged part is added to the hair.

## 5. Connection to the body

For each hair, from the one nearest the body outwards:

| parameter | default | rule |
|---|---|---|
| — | 3 px | hairs touching the boundary are attached |
| `gap_ok` | 40 | gaps up to 40 px: straight drop to the boundary (length added) |
| `win` | 320 | otherwise the cheapest path to the boundary is searched in a 320 px window, cost = 1 / (0.3 + clip(z, 0, 20)/5) |
| `lenk` | 1.6 | the path is accepted if its length ≤ 1.6 × gap + 30 px … |
| `ridge_min`, `onr_min` | 2.0, 0.5 | … and ≥ 50 % of it lies on fibre (z ≥ 2) |
| `cont_px` | 50 | if the path meets another hair within 50 px of that hair's outer end, both are the same fibre |

Hairs that cannot be connected are `unresolved` and not counted.

## 6. Measures

- Hair length = (detected pixels + connection) × pixel size, i.e. the length outside
  the boundary.
- A hair is counted if its length ≥ `minlen` (0.1 mm) and its detected part ≥ `minvis`
  (40 px ≈ 0.15 mm).
- Tip distance = largest distance of the hair from the boundary; classes ≥ 0.5, 1, 2, 3 mm.
- Counts and lengths are scaled to 10 mm of yarn using the frame width along the axis.

## 7. Validation (published set-up)

Thresholds were set on four frames whose hairs were traced by hand. Pixel coverage /
precision against the hand tracing (12–15 px tolerance) was 0.43–0.85 / 0.53–0.64.

With the default packing density, across the ten yarns of the published analysis
(25 frames each, 50 for one yarn) total hair length correlated with the Uster H index
(r = 0.86). Ten further frames, the hardest per yarn, were checked by hand for hairs
reaching 1 mm (4–28 per 10 mm): r = 0.84, concordance correlation 0.80, mean excess of
the program 2.0 hairs per 10 mm (95 % limits of agreement −7.2 to 11.3).

## 8. Packing-density check (graphical program)

Literature values are stored by how the yarn diameter or area was obtained
(`yarnhair/packing.py`):

| kind | meaning | used in the check |
|---|---|---|
| `cross_section` | fibre area / area inside the outermost fibres on cross-sections | yes |
| `optical` | count-based value from a side-view diameter (Uster 2DØ, photographs) | yes |
| `effective` | Liberec effective diameter (radial packing density 0.15) | no, listed only |
| `coil_winding` | yarn flattened by winding on a spindle (Hamilton 1959) | no, listed only |

A packing density from the user's inputs is compared with the references of the same
kind (and the same spinning system when there are any): `error` if φ ≥ 1 (cannot be
used), `warning` if φ > 0.907 (densest packing of equal round fibres), `notice` if it lies
more than 0.05 outside the range of the matching references, otherwise `ok`. Values
read from bar charts are marked approx.

## 9. Packing density from cross-sections (YarnSection)

`yarnhair/section.py`; graphical program YarnSection, also opened from YarnHair
(**From cross-sections…** in step 3, or **Tools**); command `yarnhair section`.

**Principle.** The outline of the yarn body is drawn on an image of a section
perpendicular to the yarn axis: around the outermost fibres that still belong to the
compact body; protruding and displaced fibres stay outside. The fibre area of such a
section follows from the yarn count and the blend density alone,

    A_f = 1000 T / ρ   (µm²; T in tex, ρ = 1 / Σ(wᵢ/ρᵢ) in g/cm³),

because the mass per unit length of yarn equals the density times the fibre area in a
transverse section. Fibre fineness, number of fibres and twist do not enter (the number
of fibres in a section depends on twist, their total area does not). The packing density
of a section is φ = A_f / A, with A the area inside the outline; d = 2√(A/π) is the
diameter of the circle of equal area. Fibres need not be recognised in the image, so the
method also works on sections whose fibres cannot be separated. The elastane core of a
core-spun yarn is part of T and of the blend; a hole left by a lost core lies inside the
outline and changes nothing.

**Geometry.** Area and centroid by the shoelace formula; the second area moments of the
polygon give the ellipse with the same moments, whose full axes are reported as long and
short axis (both equal the diameter for a circle). An outline that crosses itself is
rejected.

**Checks.** Aspect = long / short axis. An oblique cut at angle α stretches the outline
by 1/cos α in one direction and leaves the short axis unchanged (α = 20°: area +6 %,
φ −6 %); flattening by the knife also raises the aspect. Sections with aspect > 1.3 are
flagged, and for them φ with the short axis, A_f / (π d_short² / 4), is shown (correct
only if the yarn is round and the stretch comes from the cut). Sections can be left out
of the mean ("Use").

**Summary per label.** Mean ± SD of φ over the sections used, the 95 % confidence
interval of the mean (t distribution), CV, mean ± SD of d, mean aspect, number flagged,
φ of the mean area, and the diameter YarnHair calculates from count, blend and the mean
φ. YarnHair takes the mean φ of a label with **Use φ of the selected label in YarnHair**
(at least 3 sections); its source is written to the settings sheet of the results.

**Outline suggestion.** Optional starting point: Gaussian smoothing (σ = 1.5 px), Otsu
threshold, both polarities tried; closing with a disk of 6 % of the expected diameter
(theoretical diameter at φ = 0.32 from count and blend), hole filling, opening with half
that radius (morphology by Euclidean distance transform); the compact region (solidity
≥ 0.7) not touching the border whose area is closest to the expected area (0.2–5×) is
taken; its contour is resampled to 48 points equally spaced along it (a circle comes out
0.3 % small). Images larger than 1600 px are reduced by block averaging for this step. The measurement is always the
outline the user accepts.

**Files.** Outlines, yarns (count, blend, density) and pixel size are saved as JSON with
image paths relative to the file; after the first save every change is written to the
file. `yarnhair section outlines.json --out sections.tsv` recalculates all values from
such a file.

**Recommendations.** Embed the yarn under the same light tension as during imaging (a
relaxed elastane core-spun yarn bulks and gives a lower φ); cut perpendicular to the yarn
axis; take 15–20 sections per yarn from different places; add sections when the 95 %
interval is wider than ±0.02 (±0.02 in φ is about ±3 % in diameter). Determine the pixel
size with a stage micrometer at the same magnification.
