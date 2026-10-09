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
  its extended elevation `X.extended.th2` (scraps `XSE1`, …, in `map
  XMEe`), projected elevations `XE315.th2` (and `XE000.th2`,
  `XE090.th2`), sketches in `X/Notes/*.xvi`. An extended elevation is
  drawn as sketched: laid out with the survey's own `extend` flags,
  not as it falls in the whole cave.
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
- Do not bridge real gaps between walls with made-up lines: Therion
  closes the outline itself (but ends that nearly meet are one point,
  below). No invisible walls (`line wall -subtype invisible`)
  **[lint: wall-invisible]**.
- Every line has at least two points **[lint: line-points]**.
- Never use `-outline none` on a wall **[lint: wall-outline-none]**.
  Every outer line of the passage is drawn as a wall; a line inside the
  passage is not a wall (see below).
- Outer or inner is decided by the line's own passage: the legs that
  see it (no other drawn line between), within 1.5 m of the nearest. A
  line is inner (a border) only with those legs' stations on both sides
  of it, or their splays crossing it and reaching more than 0.5 m past
  it (a splay crossing a wall by less is a drawing error; one from a
  station on the line doesn't count). A station whose nearest point on
  the line is within 1 m of its end doesn't say (the line hands over to
  the next wall there). With no station to say, the legs do, and if they
  tie, the leg along the line. Otherwise it is a wall, drawn with the
  passage on its left: draw it that way round, and keep `-reverse on`
  for hand edits.
- A wall is never made a border to mend the outline. Where the outline
  crosses itself the drawing is mended: a small loop at a sharp turn cut
  out, walls run on past a corner cut back to it, two wall pieces ending
  together joined into one, a stray wall mark (under 0.5 m, joined to no
  other wall) dropped; anything left is reported to check.
- Wall ends that nearly meet (under 0.3 m) are one point, in a scrap and
  across a scrap join; a step or border ending on such an end moves with
  it. A drawn line that joins two wall ends (to within 15 cm) is wall.
  Two free wall ends under 1 m apart, each the other's nearest, meet if
  each wall heads within 20 degrees of the other end (a gap in a wall:
  the walls run along it; at a continuation they are nearer square to
  it), where the outline is no worse.
- A line meeting another of its kind end to end is merged into it: always
  one of 2 nodes, one of 3 or 4 unless the join turns 90 degrees or more,
  walls included (where the outline is no worse). A short piece running
  on from a border is a border (Connection 13 to 15).
- A station on a line: its splays reaching well out on both sides, across
  the line's length and into the drawn passage, make the line inner
  (Connection 15); splays into passage not drawn yet, or past the line's
  end, don't (TridentLeft 35).
- In an elevation, a passage seen across a line with nothing between is
  the passage below or above it, not one beyond: the line is inner, the
  floor of one and the roof of the other.
- In an elevation the splays straight up and down say which floor and
  ceiling is which: a wall a scrap's station's splay ends on is that
  scrap's (both scraps' if splays of each end on it), and a grey line two
  or more splays end on is a wall, a floor or ceiling (Connection 22 to
  26).
- A splay crossing a line counts as passage beyond it only if it ends in
  the drawn passage (one up an aven doesn't: Connection 15 to 16).
- Walls round an outline all run the same way (a short piece by a
  junction is not drawn start to start with the wall beside it).
- Two walls side by side between two scraps' passages (both passages'
  legs along them): the one on the other passage's side is that scrap's
  wall (GoSouth 16 to 21).
- Hand edits used as examples are checked against these rules first
  (an edit can carry a mistake too: TridentLeft 27, a piece the wrong way
  round).
- Two walls drawn on past the corner where they meet (crossing near an
  end of each) are cut at the crossing and the ends past it go (Trident
  17, hand edit). The rock the fill's closing-up takes in (a tongue
  between two walls, round a passage end) is not passage, in elevations
  as in plans; a station within 0.1 m of a face's edge doesn't make it
  passage.
- An outer line ending on the middle of a wall (a T) is a wall there as
  a hand edit does it: the wall split at the T, and the piece of it
  then inside the passage a border, if its legs say it is inner.
- Only strokes in a wall colour (black in plans) can be outer lines. A
  grey or brown line inside the passage is a border whichever side the
  legs are on (a channel either side of the leg: TridentLeft 21 to 29).
- A black dashed line (no ticks) is a wall the surveyors could not see
  all of, where the passage carries on: `line wall -subtype presumed`.
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
- A group of boulders is an area (`area blocks`, or `area debris` if
  mostly small). A boulder on its own, or one large for the passage it
  is in (a quarter of the passage's narrowest width across it or more,
  also within a group), is drawn as a rock. Rocks in cross-sections are
  drawn (closed brown loops there are rocks, not the section's outline).
- A rock is a simplified line drawing seen from above: its outline
  angular and roughly convex (the hull of the sketched loop cut to 5 to 8
  corners by size, corners at least 6 cm apart), its rock edges
  (`line rock-edge`, after the rock) in one of three styles, picked for
  each rock (the same every run) so they don't all look alike:
  - a line across (about 35%), corner to a corner about opposite (two
    faces), on some rocks with a second line from another corner meeting
    it part-way;
  - pointed (about 25%): a peak towards the light;
  - a wedge (about 20%, long rocks more often): a ridge along its length;
  - a block (about 20%): the top face shrunk and moved towards the light
    (top left), its shadow side drawn.
  Every corner inside the rock where edges meet has at least three lines
  meeting there, as at a corner of a solid, usually going out to corners
  of the outline. Rocks lower on the page are drawn later, in front. Not
  copied from other drawings.
- Walls that are rock or debris keep their subtype
  (`line wall -subtype debris`, `-subtype blocks`): drawn rocks do not
  replace them.
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

## Extended elevations

- Walls carry a subtype for what they are drawn as: `clay` (mud: brown),
  `sand` (brown with dots), `flowstone` (green, smooth or running down
  a step), `blocks` (rock on the floor: green boulders or a humpy line),
  `debris` (a floor with rubble: brown curls, or a line with boulders
  drawn along it), plain `line wall` for rock. Boulders along a line
  make it debris, not sand or mud.
- A floor drawn only as a row of boulders or brown curls (no line under
  them) is still a floor: `line wall -subtype debris` along the bottom of
  the row (BoldStep 13 to 11). A row of straight brown dashes is mud
  marked on a floor drawn elsewhere, not a floor. The subtype goes on the line, `line wall -subtype clay`, never
  on a point (`subtype clay` among the points: Therion takes it, but it
  is hard to follow when editing), and does not change along a line: a
  wall that changes is drawn as one line per kind, meeting end to end.
  Colour is only a hint: shape decides.
- A line inside the passage is never a wall (no `-outline none`): every
  outer line is a wall, and inner lines are drawn as what they are
  (border, ledge, step, rock-border and so on).
- A pool is an `area water` in an invisible closed border whose first two
  points are its surface, the second with `adjust horizontal` so the
  surface is level; a bowl wall under it where no floor was drawn.
- Water flow is a `water-flow` point just under the floor, pointing
  downhill along it.
- A curtain is a point `curtain`; a group of stalactites `stalactites`;
  no `flowstone` points (flowstone is a wall subtype). A rock in the
  passage is a `rock-border -close on`.

## Projected elevations (E315)

- For now (walls parked): one scrap, `XSE315_1`, with the stations on the
  dots of `Notes/XE315.xvi`, laid out as `tools/ElevationsExx.py` does
  (xvi units, offset from the lowest station, the xvi as backdrop). The
  walls are drawn round them. The rules below are for when the walls are
  generated again.

- 315 is the direction the viewer faces (`-projection [elevation 315]`).
  A survey X has `X/XE315.th2` (scraps `XSE315_1`, ...) with the
  backdrop `X/Notes/XE315.xvi`, Therion's centreline of X alone so
  projected; `X.th` inputs it with `map XME315`, and `XME315@X` is in
  `LongwoodValleySinkM315` (`LongwoodValleySink.th`).
- Walls only, drawn from the extended elevation
  (`python3 -m tools.sketch2therion projected X --file`): a wall point
  keeps its place along its nearest leg and its height above or below
  it; its offset along the passage is scaled by how much of the leg is
  seen across the view. A wall keeps its subtype; where the view mirrors
  the extended drawing the wall is reversed, so the passage stays on the
  same side of it.
- Scraps from the 3D model (Therion's walls from the splays, as Loch
  shows them): legs that do not meet but overlap in the view are passage
  drawn over passage, and go in different scraps; otherwise a scrap is
  as large as it can be. Judged on the PDF and iterated.
- No closing walls: Therion closes the outline (as for every scrap).

## Scraps

- Passages drawn over one another in a view go in separate scraps;
  otherwise a scrap is as large as it can be. Overlap is read from the
  3D model (as Loch shows it): `python3 -m tools.sketch2therion scraps X
  --view plan|extended|315`. Scraps listed in `[scraps]` or
  `[scraps_extended]` (project.toml) are used as they are.
- Order: plan scraps from the model built from the splays, before the
  plans are drawn; elevation scraps wait for the plans, from the model
  built from the drawn plans together with the splays. The plans are
  then checked against the model from the drawn plans (the feedback
  loop).
- Scraps meet where as few fill lines and points as possible are needed.
  In a plan: at simple, linear passage, never at a junction (a hard
  rule); near one, a leg or more down one of the passages. A split need
  not be far from the junction: on the leg next to it (CJPitch along the
  pitch leg, CJS a little back, CrossRoads) the junction is whole in one
  scrap, and that keeps the rule. In an
  elevation: near a junction most of the time, usually on a short piece
  of passage by it (WestPassage 57 to 59, CJPitch, CrossRoads), maybe on
  it, since that is where the split is needed (a rule still being
  developed).
- Examples to learn from are the pre-2026 hand drawings only; the 2026
  splits are ours.
- Two medium scraps are better than a short one and a very long one.
- Every scrap has at least two stations. They are inside the drawn
  passage, except at a continuation; in a short stubby scrap one may be
  outside it.
- Overlap: more than 70% of the smaller passage and at least 0.3 m2,
  with one leg more than 1 m beyond the other's walls (one passage in
  front of another, not the same space seen from two legs); in plan
  only passages one above the other. Set by `scraps --calibrate` from
  the splits made by hand.
- In an extended elevation an overlap of 2 m2 or more is a clash whatever
  share of the smaller passage it is (TritonSouth); the older 315
  drawings keep larger overlaps in one scrap, so not in 315.
- Where a scrap meets the next in an elevation, its walls end in line:
  a floor does not run on past the nearest end of the ceiling (or the
  next scrap's short bit of ceiling), and the other way round.
- Each scrap is a passage, in plan or elevation. At a junction the
  passage through it (the two ways on to the most passage) stays one
  scrap, its floor and roof running on past the junction; a branch drawn
  over it is its own scrap, holding the junction station (Trident, hand
  edit: 9-10-13 one scrap, the ramp 10 to 12 another with 10 in it). The
  branch's walls start on the through passage's walls, on a
  near-vertical line through the junction station: drawn on to it, or
  cut at it (only walls within about 2 m of the junction's height). A
  wall starting at the junction belongs to the passage whose leg it runs
  along, not the nearest (the ramp's floor runs past 13). A wall
  between two scraps' passages, alongside both legs, one either side of
  it, is a wall of each scrap (elevations).
- In an extended elevation two legs from one station clash when each
  far end is more than 1.5 m beyond the other's walls and they share 2 m2
  or more of the drawing (Trident 10 to 12 over 10 to 13; BoldStep 5 to 7
  and 5 to 8, 2.4 m, stays one scrap).
- Plans are calibrated from the pre-2026 plans: they split where
  passages overlap by more than 30% one above the other, on the leg by
  a junction where needed (the junction whole in one scrap).
- More than one split can be right: a split is judged by these rules
  (no passage over another in a scrap, joins at simple passage, sizes,
  stations), not by matching another split.

## Cross-sections

- One scrap each, named survey + `PX` + station in a plan
  (`FairyChimneysPX5`), `EX` in an elevation.
- The leg and splay rule applies: the section's station and its splays
  (the station's copy at the section in the xvi) are inside its
  outline, splay ends no more than 0.5 m outside. Only the section's own
  strokes go in it, never a stroke of the main drawing.

- `line section` goes completely across the passage, and about 0.5 m
  past it, so the arrows are clear of the walls.
- Direction arrows do not overlap the passage they mark, and best not
  other passages.
- Every section line has its arrows **[lint: section-direction]**:
  prefer `-direction both`; arrows only at the start or end if that is
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
  another beside it. How many nodes a line needs goes with how it bends:
  a long sweep needs only a couple, an S bend more.
- An area mostly outside the walls (rocks drawn along the wall) is not
  drawn. Areas run only just over the walls (about 0.15 m): more makes
  odd shapes and is not needed.
- Areas (not water) spread out from what is drawn in them to fill the
  space they belong to, but stop at walls, steps and longer borders; one
  area over a boulder floor, not each rock outlined.
- At a node, the control points either side are in line with it (a
  smooth node) unless the line needs a sharp corner there.
- A short line (2 nodes, sometimes 3 or 4) that meets a line of the same
  kind end to end is part of it: one line, not several. A line sketched
  in pieces with small gaps is one line too.
- Lines of different kinds ending close together share the end (a
  border running on as a floor step, then a pitch).
- A deliberate bulge or pocket in a wall is drawn; it is not a glitch to
  smooth away. Clear corners stay sharp.
- Mud dashes beside a line are mud, not the ticks of a step; an area of
  rocks stays on its side of the line, the mud on the other.
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

- This file is the source of truth: check every drawing run against
  every rule here, and record what a review teaches.
- At the end of every run that edits th2 files, build the whole cave in
  plan, extended elevation and 315 projected elevation, from one config
  (`LongwoodValleySink/Whole_cave.thcfg`, PDFs and SVGs in
  `LongwoodValleySink/Outputs/WholeCave*`), and check legs and splays
  against the fill: `python3 -m tools.sketch2therion fillcheck --build
  [--survey X ...]` (report in `output/check/fillcheck.txt`). The SVGs
  draw the same as the PDFs.
- Check the PDF after processing drawings. The coloured fill shows
  where Therion thinks the passage is (inside the walls). Legs and
  splays are all inside the fill, except at passage ends where the
  continuation is not drawn yet. A splay end may occasionally go
  outside a wall: record it as a thing to check if it is outside by
  more than 0.5 m.

## Updating this file

Add whatever a review or drawing session teaches, in the same commit as
the drawing. Tag a rule **[lint]** only when `tools/th2lint.py` checks
it, under a new id, and add the check in the same commit.
