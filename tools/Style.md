# Drawing Therion scraps in the Cheddar Catchment survey

How to draw or edit Therion scraps (`.th2`) and what to check afterwards.
It started from a Therion expert's review of converted drawings and is
kept up to date from each drawing session and review (see "Updating
this file"). `tools/sketch2therion` (`plan`, `tidy`, `sections`) follows
it; keep to it when editing by hand too.

Rules tagged **[lint: id]** are checked by `python3 tools/th2lint.py`
under that id; every id here has a check there, and the reverse. The other rules
need a person to look at the render.

Examples are from LongwoodValleySink. For another cave, read
`<Cave>` for `LongwoodValleySink` and `<Cave>/Plan_only.thcfg` for its
plan-only config.

## Names and files

- New config files are named `name.thcfg` (e.g.
  `LongwoodValleySink/Plan_only.thcfg`). Older names (`thconfig`,
  `thconfig_A0plan`, SexyTopo's `X.thconfig`) stay as they are.
- A survey `X` lives in `<Cave>/X/`: `X.th`, its plan `X.plan.th2`,
  elevations `XE315.th2` (and `XE000.th2`, `XE090.th2`), sketches in
  `X/Notes/*.xvi`.
- Plan scraps are `XSP1`, `XSP2`, …; elevation scraps `XSE315_1`, ….
- `X.th` has a `map XMP` listing its plan scraps (and `map XME315` for
  the elevation). The cave's plan map, `LongwoodValleySinkMP` in
  `LongwoodValleySink.th`, lists `XMP@X`; `Maps.th` holds group maps
  such as `CyclopsMP` (which lists `CyclopsSP1@Cyclops`) that it can
  list instead.
- Filenames and `input` lines must match in letter case: CI runs on
  Linux, where `TickleWest.th` and `ticklewest.th` are different files.

## Licence and authorship

- Survey data and drawings: **CC BY-NC-SA 4.0**. The tools: GPLv3.
- Every new scrap has `-author <year> "<Name>"` and
  `-copyright <year> "CC BY-NC-SA 4.0"`. **[lint: scrap-author-copyright]**
- Sheets print the licence and credits from `map-comment` in the
  layout; it says CC BY-NC-SA 4.0.

## Walls and the outline

- `line wall` has `-outline out` by default; do not set it.
- Walls are the scrap's outline. Draw each wall with the passage on its
  **left**, or add `-reverse on` if the passage is on its right.
- A wall round an internal pillar has `-outline in`.
- Do not close gaps between walls: Therion closes the outline itself.
  No invisible walls (`line wall -subtype invisible`)
  **[lint: wall-invisible]** and no `-outline none` fill line on a wall
  **[lint: wall-outline-none]**.
- The outline must not cross itself, and no wall may loop back on
  itself. Otherwise Therion warns "invalid scrap outline" (no 3D model
  for the scrap) or MetaPost "scrap outline intersects itself".
- A line inside the passage (a ledge, the edge of another level) is a
  `line border`, not a wall.
- Passages that overlap in plan, or only come close together without
  joining, go in **different scraps**: one scrap would join them up and
  turn the walls between them into borders. A leg from one into the
  other (dropping into a passage below) is between the scraps. For the
  converter, list each scrap's stations under `[scraps]` in
  `tools/project.toml` (GoSouth: 15 to 17 drops into the passage beside;
  19 comes close to 10 and 11 but does not join them).
- One wall that runs from one scrap into the next is two walls that
  meet exactly: the last point of one is the first of the other.
- Where a passage was not sketched, walls may be drawn from the splays,
  as `line wall -subtype presumed`. Never guess a wall that neither the
  sketch nor the splays show.

## Symbols: general

- Default clipping normally gives the best result. Most symbols are
  clipped by the outer walls; use this for the best effect.
- `-clip off` only in exceptional cases, with a `#` comment on the line
  before saying why. **[lint: clip-off-reason]**
- Labels and cross-sections must not overlap passage or each other,
  including when combined with other surveys on the same sheet.

## Symbols: points

- Slope arrows (`point gradient`) are inside the walls, do not cross
  steps or pitch edges, and are not in water.
- Water flow (`point water-flow`) is inside the walls.
- Climbs and pitches are labelled `C2`, `P5`: no units **[lint: climb-units]**,
  in whole metres, placed outside the passage.
- Draught arrows (`point air-draught -orientation N`) go beside the
  passage, not across it, with a `point x y date -value YYYY.MM.DD` in
  the same scrap for when the draught was seen. **[lint: draught-date]**
- Text sizes: labels use `-scale` `xl`, `l`, `m`, `s` or `xs` only
  **[lint: label-scale]**, in descending order of importance:

  | `-scale` | For | LongwoodValleySink example |
  |---|---|---|
  | `xl` | Area name | none yet |
  | `l` | Main passage | `[Triassic Tunnel]` (`Triassic/TriassicP.th2`) |
  | `m` | Minor passage | `Century` (`Century/Centry.plan.th2`) |
  | `s` | Feature | `[Dig Face May 2018]` (`Triassic2/Triassic2P.th2`) |
  | `xs` | Small note | `[Too Tight]` (`CyclopsEye/CyclopsEye.plan.th2`) |

## Symbols: lines

- Use the fewest points that follow the drawing, smooth in both
  directions.
- Rocks and boulders (`line rock-border`) are closed with `-close on`,
  ending exactly on the first point **[lint: rock-closed]**
  **[lint: close-on-first-point]**, and are not smoothed (no curve
  control points) **[lint: rock-not-smooth]**. A closed line that does not end
  on its first point gives xTherion's "no such element in array".
- Rocks are drawn in file order and clip each other.
- Large boulders get a `line rock-edge` inside them to look like 3D
  rocks.
- Rocks on the edge of a passage are best drawn going over the wall.
- Steps, by height:
  - significant boundaries and low steps under 20 cm: `line border`;
  - 20 cm to 2 m and easily climbed: `line floor-step`;
  - harder climbs and anything over 2 m: `line pit`.
- The low side is the left of the line's direction (see above).
  Existing LongwoodValleySink drawings use `line pit` both ways round
  (45 plain, 17 with `-reverse on`): check old ones when they are next
  edited.
- Use `line overhang`, not `line ceiling-step`, for ceiling steps and
  overhangs (dashed lines with a tick on each dash in the sketch).
  **[lint: ceiling-step]**
- Therion draws the ticks of `line floor-step` and `line pit`, and the
  teeth of `line overhang`, on the **left** of the line's direction
  (test render with the house symbols from `common_layout.th`,
  2026-10-07): draw the line with the low (or
  overhanging) side on its left. In the sketch these are lines with
  ticks on the low side; really small steps are plain solid lines and
  are drawn as `line border` (grey in rock, brown in mud).
- A line that ends at a wall (or another line) ends exactly on one of
  its nodes. **[lint: end-on-node]** (walls only so far)

## Symbols: areas

- Water: a `line border -subtype invisible -id X -close on`, and an
  `area water` that refers to it by `X`. **[lint: water-border]** No other border on
  water.
- Water against an outer wall is best drawn with its border outside the
  wall.
- Areas can overlap to show a transition, or pebbles in water.
- No borders drawn over boulder or debris areas: the sketch's lines
  among the rocks are part of the rocks, which the area's symbols show.
- An area's border has few control points and is smooth (a spline):
  where it meets a wall, run it out over the wall and let the wall clip
  it, rather than following the wall point by point.
- Individually drawn rocks can be above or below the water; this needs
  careful ordering and use of clipping.

## Cross-sections

- `line section` goes completely across the passage.
- Direction arrows do not overlap the passage they mark, and best not
  other passages.
- Prefer `-direction both`; arrows only at the start or end if that is
  the only option.
- Therion draws the arrows on the line's left, so draw the line with
  the view direction (along the survey, from the station towards the
  next) on its left.
- A section drawing must not overlap a passage or another section,
  including those of other surveys on the same sheet.
  `python3 -m tools.sketch2therion sections` fixes both (see
  `tools/README.md`).

## Layouts

- Water: solid blue. Sump: a darker solid blue. Water flow: the same
  colour as water.
- Text sizes as in the table above.

## Sketching in SexyTopo

- Sketch both the plan and the extended elevation, and cross-sections
  where the passage shape matters.
- Colours (`[convert]` in `tools/project.toml` tells the converter):
  - black: walls;
  - brown: the floor: boulders and debris are closed loops, told apart
    by size (boulders drawn singly or as an area); sand is dots, mud is
    dashes, always as area fills; other brown lines are steps in mud;
  - grey: ceiling steps, but also floor steps, pitches and channels;
  - colours are hints and are sometimes wrong: the notation decides;
  - blue: water (a closed outline is a pool, kept to its sketched
    outline: not run along a wall it only touches);
  - green: flowstone and pretties (area fills, and point symbols for the
    different stals); solid green lines are gours (`line rimstone-dam`);
  - red or orange: notes, which the converter ignores.
- A step or pitch is shown by its symbol (the ticks), not its colour: it
  can be any colour (brown for a step in mud).
- Short jogs in a wall where the sketcher's strokes did not meet are not
  features: the wall is drawn through them. The same goes for a wall
  stroke started again a little beside the last (the outer one is the
  wall) and for small gaps in a border.
- A stroke drawn on as the wall is wall all along, even where a border
  comes off it close by. Splays ending on a stroke show it is a wall.
- Pitches and floor steps are often drawn alike: a P near the line means
  a pitch, a C one depending on its height. The converter cannot read
  these notes and draws a floor step: check each one.
- Draw only what the plan sketch shows: no steps, pitches, labels or
  slope arrows inferred from the survey data or the elevation sketch.
- Little marks (dots, tiny loops, short dashes) come from sketching in a
  dirty place: ignore one on its own; many together are sand (dots) or
  mud (dashes).
- Brown dashes (up to about 1.5 m) are mud: draw the whole stretch where
  they lie as one `area clay`, wall to wall, not a patch round each
  group; keep it off boulder and debris areas. Brown dashes beside a
  wall are mud, not the ticks of a step.
- A brown stroke curled round on itself is a boulder, even if the loop
  was not quite closed.
- Closed loops are boulders (about 0.3 m across or more) or debris
  (smaller), whatever their colour: a green loop on its own is a boulder,
  only rings inside one another are a formation.
- An area needs room to draw its symbols: leave out thin parts (under
  about 0.5 m) and small areas; this matters most for boulders and debris.
- Gours (`line rimstone-dam`) are smooth, regular arcs, not every wobble
  of the hand sketch.
- Where there are several boulders or much debris, use an area
  (`area blocks` or `area debris`) rather than drawing each one as well;
  an area stops at a trench or step and does not cross to the other
  side. A single boulder is a `line rock-border` (straight sides, not
  smoothed) with its `line rock-edge` after it in the file, one edge line
  where its pieces share a point.
- Lines other than boulders are smooth: points only where the line
  really bends, with splines, not every point of the sketch. How closely
  a line follows the sketch goes with the length of the legs nearby (the
  drawing is zoomed so that legs fit the screen), not a fixed distance.
- Walls the sketcher did not quite join are joined: their ends meet
  exactly, end to end (not across the passage). Too close to see is
  relative to the legs nearby, with a minimum.
- No two nodes of a line so close that they cannot be told apart and
  picked when editing (about 2% of the nearby legs' length, at least
  5 cm; the check uses the 5 cm) **[lint: node-gap]**: where a line ends
  on a wall, use the wall's node if one is that close, rather than adding
  another beside it.
- Do not draw a wall where nothing was sketched: no presumed walls to
  close an outline; leave the gap for Therion.
- Where two passages, or the two sides of a bend, come close, the rock
  between them is rock: their walls are walls, not borders, and the
  passage's fill does not cross between them.
- A small loop off a wall, left open where it meets it, is part of the
  wall (a projection the wall goes round), not a boulder.
- Walls follow the sketch closely (within about 2% of the nearby legs'
  length), with nodes where the wall bends rather than where the hand
  wobbled.
- A cross-section is its own scrap, with its wall drawn, placed (in the
  file's coordinates) by its section mark, so xTherion shows it there.
- A boulder's edge lines meet at a ridge point and end on its corners;
  more than one may be needed, but as few as possible.
- SexyTopo is set up to export in the house style (`X.plan.th2`, `XSP1`,
  `map XMP`).

## Git and CI

- Case-sensitive filenames (see above).
- One survey per commit, with anything learnt added to this file in the
  same commit.
- CI and `th2lint` must be green before merging.

## Checking

Build with `therion -l ../output/therion.log Plan_only.thcfg` in
`LongwoodValleySink/`, then (logs in `output/`):

- `grep -E "^therion: error|invalid scrap outline" output/*.log`:
  there should be none.
- `grep "intersects itself" output/*.log | sort -u`: only scraps you
  didn't touch.
- `python3 tools/th2lint.py --from LongwoodValleySink/Plan_only.thcfg`
  is clean.
- `python3 -m tools.sketch2therion review check X/X.plan.th2`: every
  outline valid and its turning number not 0 (0 is MetaPost's
  "intersects itself"), before building.
- `review show` (see `tools/README.md`): the drawing beside the sketch
  round the new stations, with someone who knows the cave.
- Render and look. poppler (pdftoppm, Evince, Okular) can show white
  holes in Therion's smooth altitude shading that are not in the PDF;
  check with another renderer (MuPDF) before chasing them.
- PDF viewers show overlapping rocks fading rather than clipping; this
  is a viewer fault, do not try to fix it.

## Updating this file

Add whatever a review or drawing session teaches, in the same commit as
the drawing. Tag a rule **[lint]** only when `tools/th2lint.py` checks
it, under a new id, and add the check in the same commit.
