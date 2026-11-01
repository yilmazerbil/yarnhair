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
