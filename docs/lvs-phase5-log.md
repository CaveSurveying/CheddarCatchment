# Phase 5 log: review comments and what was done about them

Each review comment, the kind of change it needs (converter, rule in
`tools/Style.md`, or hand work) and the outcome. See "Phase 5" in
`docs/PLAN-LongwoodValleySink.md`.

## GoSouth test zip (2026-10-07), draft straight from the converter

| # | Comment | Kind | Outcome |
|---|---|---|---|
| 1 | Brown is used for boulders, debris, mud and sand. Boulders can be drawn individually or as an area fill; the others are always area fills. (The converter reads brown as another level's walls, Swildons' convention, and found 0 boulders.) | Converter (`[convert]` in `project.toml`, `marks.py`); `Style.md` | Draft 2: boulders by size, debris areas, sand (dots), mud (dashes), other brown lines borders |
| 2 | Green is flowstone or pretties: there are area fills, and point symbols for the different stals. | Converter; `Style.md` | Not yet: green is still made point symbols only (as upstream) |
| 3 | Climb and pitch labels: whole numbers (`C2`, not `C1.5`). | Converter; `Style.md` | Draft 2: whole metres, half up |
| 4 | Passage names: later. | Hand work, later | Deferred |
| 5 | The `-outline none` wall (GoSouth.plan.th2 line 61, about 2.6 m beside stations 1 to 2, by the junction with CrystalPitch) is exceptional. Do not change the `wall-outline-none` rule; do not fix ones drawn elsewhere. | Open | Deferred: to come back to |
| 6 | Joins to neighbouring surveys: later, once the drawings are reasonable. | Plan | Added to the plan as a later stage |
| 7 | The walls have steps where no step is drawn. Follow-up: a step in a wall (stations 21 to 22) is a border, not outline; the channel near station 5 runs the whole way down and the wall should not step there. | Converter (`jogs.py`; walls from black only) | Draft 2: wall steps cut out as borders, the wall split; the outline is made from black strokes only, so the channel no longer pulls the wall in |
| 8 | A blue shape (closed, between stations 22 and 23) should be water. The converter made it a water-flow arrow. | Converter (`features.py`) | Draft 2: a closed blue outline is a pool |
| 9 | The ceiling step is missing. Follow-up: grey is ceiling step but also floor steps and pitches; the symbol (ticks) says which. Grey near station 7 should be small floor steps, i.e. borders. | Converter (`marks.py`) | Draft 2: grey lines inside the passage are borders. Not yet: recognising the tick symbol (step, pitch, low side) |
| — | The backdrop opens in the user's own viewer. | Review zip | Not yet confirmed |

## GoSouth draft 2 (2026-10-07)

Converter changes, all set per cave in `[convert]` in
`tools/project.toml` (the defaults reproduce the upstream converter,
which the regression test still checks): only black makes the outline;
lines inside the passage stay borders (`details` no longer guesses
floor steps from them); brown floor marks; closed blue outlines are
pools; wall steps up to 0.4 m become borders; climb and pitch labels in
whole metres. The elevation floor profile still reads black, brown and
grey (with black only the pitch below station 1 was lost).

The `-outline none` wall from draft 1 no longer appears; the rule was
not changed and no other drawing was touched.

## GoSouth draft 2 review (2026-10-07) and draft 3

| # | Comment | Outcome in draft 3 |
|---|---|---|
| 10 | Show GoSouth alone, not CrystalPitch over it. | `review build --survey GoSouth` (and `--plain`): its plan map only, without the cave sheet's legend, north arrow and scale bar (which landed on the drawing). |
| 11 | Colours are hints, sometimes wrong. | The notation decides steps, pitches and overhangs, whatever the colour. |
| 12 | Pitches and floor steps are shown by notation (ticks); guess if none. Really small steps are solid lines, borders. | `notation.py`: a line with ticks is a floor step, or a pit where the elevation drops 2 m or more; no notation: a step is guessed from the elevation only for a drop of 1 m or more (else just the label). Ticks go on the left of the line, where Therion draws them (test render). |
| 13 | Ceiling steps and overhangs are dashed lines with a tick on each dash: `line overhang`. | Found as rows of short dashes with ticks: 2 in GoSouth (stations 1 to 3). |
| 14 | Solid green lines are usually gours. | `line rimstone-dam` (Therion has no `line rimstone`: the build caught it); green rings and curls stay formations. |
| 15 | Borders have far too many points. | Lines resampled every 0.4 m along their own path and drawn as splines; boulders stay straight-sided. |
| 16 | Boulders drawn with a border as well as an area; areas preferred; the debris near 5 crossed the trench. | Groups of loops are one area (`blocks` if mostly boulder-sized, else `debris`), cut along interior lines and steps so they stay on their side; only an isolated boulder is drawn alone. |
| 17 | The pool does not touch the wall but was run along it. | Pools keep their sketched outline (`water_to_walls = false`). `tidy` also treated every closed border with an `-id` as water: now only those an `area water` uses. |
| 18 | Floor steps near 22 not in the sketch. | Gone (see 12). |
| 19 | Rapid steps in the wall (21 to 22 and elsewhere) are the sketcher's strokes not joining. | The wall is joined through them (`jogs.py`). |
| 20 | Boulder edges not on the PDF; two edge lines where one would do. | One edge line, corner to corner through a ridge, after the boulder (they were after it already, but 0.2 m long). The GoSouth boulder is now small enough to need none. |
| 21 | Lines ending at a wall or another line should end on a node. | Rule in `Style.md`, `th2lint` check `end-on-node` (walls only so far; existing drawings baselined, not changed); the converter moves ends within 0.2 m of a wall onto a wall node (inserting one if needed). |
| 22 | An outer wall drawn as a border, clipped. | A wall piece outside the passage stays wall. Not fixed where the converter's passage bulges past the wall (station 7, right). |
| — | (found while checking) The boulder at 26 was run 0.4 m along and past the wall, 2.3 m long from a 0.8 m loop. | `boulder_over_wall = 0.1`: it just crosses the wall. |

## GoSouth draft 3 review (2026-10-07) and draft 4

| # | Comment | Outcome in draft 4 |
|---|---|---|
| 23 | Boulder edges may meet at a point; more than one edge line may be needed, but as few as possible. | Edges meet at a ridge and end on corners: one line through two corners, a short extra line per further corner. |
| 24 | Only draw what is on the diagram: no pitches or floor steps inferred from the data. | `elevation_data = false`: `--floor` is ignored; no guessed steps, pitches, climb labels or slope arrows. A ticked line is a floor step. |
| 25 | Little marks come from a dirty environment: ignore them; lots together are mud or sand. | Marks under 0.15 m: alone ignored, three or more together sand (dots, tiny loops) or mud (dashes). |
| 26 | Gours are good but should be smooth arcs, not the rough hand sketch. | Each gour is a spline through three or four evenly spaced points. |
| 27 | Green loops are still boulders (the colour is wrong). | A single green loop is a boulder or debris; only rings inside one another stay a formation. Boulders from 0.3 m across (was 0.6). |
| 28 | Still too many control points on most borders. | Points only where a line bends: smoothed over 0.5 m, then simplified to 0.04 m (a 6 m border: 8 points, was 17). |
| 29 | The wall is still drawn as a border. | Not fixed. A test for "nothing beyond it on one side" broke the outline at the pillar (stations 16 to 21) and was taken out. The cause is how the passage outline is made (a closed-up blob round all strokes and legs); the proper fix is to build it from the wall strokes. Next round. |
| 30 | The two overhangs are one, joined by a curve drawn as a dash and a tick (and a stray dash). | Overhang pieces whose ends are within 1.2 m are joined through the strokes between them: one overhang round the U at stations 1 to 3. |
| 31 | Areas only work with room to draw the objects; thin parts are pointless. | Parts narrower than 0.5 m (0.3 m for sand and mud) are dropped, and areas under 0.4 m². |
| 32 | Is `common_layout.th` (and the symbols it calls) used? | Yes: `Plan_only.thcfg` inputs it and its layouts copy `common`, which copies `symbols` (BCA areas, overhang, pit, floor step). The tick-side test render had not used it; redone with it: ticks still on the left. |

## GoSouth draft 4 review (2026-10-07) and draft 5

| # | Comment | Outcome in draft 5 |
|---|---|---|
| 33 | Pitches and floor steps are often drawn alike; a C# or P# near one is the only indication (P always a pitch, C depends on the height). A human will check; take a guess. Then: no elevations, just plans for now. | Plans only: the elevation sketch is not used (`--floor` ignored). No sketch has text labels (the C and P are hand-drawn strokes the converter cannot read), so a ticked line is drawn as a floor step: check each against its C or P note and change it to `line pit` where needed. GoSouth has four, near 26 to 27. |
| 34 | Get the wall sorted: it is the most important. Near station 5 is a good interpretation. | Station 5 unchanged. Outer walls the passage fill had bridged (station 7, right) are found by tracing out from the stroke (nothing between it and the fill's edge, a leg on the other side) or by splays ending on it, and the fill is cut back to them: they are walls. |
| 35 | A border has small gaps where the sketcher did not quite continue the line (as with walls). | Border pieces whose ends are within 0.3 m and carry on (turning less than 60°) are joined. |
| 36 | A splay through the interpreted wall shows the sketched line was right. | Splays ending on a stroke count as evidence that it is a wall (see 34). |
| 37 | Near 21 the wall should be continuous, with the border coming off it. | A stroke drawn mostly along the passage's edge is wall all along, even where the fill takes in a stretch of it: strokes 182, 192 and 194 are one wall from 18 round to the top of the alcove; stroke 148 is the border off it. The outline builder (`tidy`) no longer routes the outline to the end of such a stretch, nor makes it a border. |
| 38 | Near 21 there are still steps in the wall. | Two causes, both fixed. Where a wall is drawn twice a little apart (strokes 183 and 193), the outline now goes on along the outer one instead of cutting in to the inner and jumping out at its end. Joining walls refitted the whole wall each time, so the error added up (0.25 m off by the fifth join): now only a metre either side of a join is refitted (`join_local`), and every refit is checked to stay within 0.1 m of the sketch. A Bézier segment whose control points fall behind its start (the zigzag where 193 and 195 overlap near 22) is drawn straight. |
| — | (found while checking) `traced_outer` measured the fill's width from 0.3 m out, so the cut-back left a 0.15 m strip. | Measured from the stroke. |

Still open: the wall from 18 to the alcove is partly inside the passage
fill, so it is written `-outline none` (one new `wall-outline-none`
finding, the open question in rows 22 and 29). The junction with
CrystalPitch stays a border until the joins (stage 5c).

## GoSouth draft 5 review (2026-10-07) and draft 6

Draft 5 was rebuilt and reviewed on the user's own machine (Therion
6.4.0, as CI), opened in place in xTherion instead of a zip.

| # | Comment | Outcome in draft 6 |
|---|---|---|
| 39 | The leg 15 to 17 goes from one passage into another, and they overlap slightly: they should be in different scraps. | `[scraps]` in `tools/project.toml` lists the stations of each scrap (`GoSouth = ["1-16", "17-29"]`, `hand_scraps = true` in `[convert]`). The leg 15 to 17 is in neither. Each stroke goes to the scrap of its nearest leg; a stroke running past both passages is cut where that changes (`scraps.py`). Rule in `Style.md`. |
| 40 | There is no passage between 19 and 10: the passages only get close together. | 19 is in GoSouthSP2, 9 to 11 in GoSouthSP1, so they are no longer one fill; the wall from 11 now ends by 19 where the other passage's wall begins. |
| 41 | The walls separating the passages were drawn as borders. | Each is now a wall of its own scrap (the left wall of 12 to 15 in SP1, the right wall of 19 to 18 in SP2). |

Still open: the two strokes of the narrow strip just right of the 19 to
17 leg are inside SP2's fill and written `-outline none` (two
`wall-outline-none` findings, as in rows 22 and 29): a pillar
(`-outline in`), a third passage, or the wall between the passages drawn
twice? The two scraps' fills overlap a little by 16 and 21, as the
passages do.

## GoSouth draft 6: the user's own edits (2026-10-07)

The user edited `GoSouth.plan.th2` by hand in xTherion between stations
10 and 21. Their file is now the working drawing; the converter's
draft 7 (below) is only used to check the converter learnt from it.

| # | Comment or edit | Kind | Outcome |
|---|---|---|---|
| 42 | Near 21 the north wall had been drawn as one wall; the conversion left it as two pieces, one per scrap, apart. Joined by hand. | Converter (`scraps.meet_ends`) | It was two sketch strokes nearly meeting, one in each scrap. With hand-chosen scraps, wall ends in different scraps within 0.3 m now meet at their midpoint, after `tidy` (which had moved them apart again). Rule in `Style.md`. |
| 43 | 18 to 19 fixed by hand: the narrow strip is a pillar, coming to a point at 17. | Hand work | Answers the open question from draft 6: no `-outline none` walls left. |
| 44 | The wall by 10 as it should be: the passage 9 to 11 closed off, not running down to 19. | Hand work | The sketch draws the wall from 11 on down to 19; only someone who knows the cave can say it stops. |
| 45 | Areas can be done with fewer control points and splines. (The user's areas: 5 or 6 spline nodes, run out over the walls, against 13 to 17 straight points along them.) | Converter (`marks.py`); `Style.md` | `area_over_walls = 0.3` (areas run over the walls, which clip them) and `area_splines = 0.15` (notches closed up, simplified, drawn as a closed spline): 6 to 10 nodes. Pools keep their sketched outline. |

Found while checking the user's file (to ask): GoSouthSP1's outline
crosses itself between 15 and 16, where the line 15 to 16 is now a
`line wall` (it was a `line border` in draft 6), so two walls fan out
from one point near 15; and three borders end 1 to 2 cm from a wall
without being on its node (`end-on-node`).

## GoSouth reference and draft 8 (2026-10-07)

| # | Comment | Kind | Outcome |
|---|---|---|---|
| 46 | The outline crossing between 15 and 16 was a wall put in the wrong scrap. Border ends should be on a wall node. | Hand work | The user moved the wall to GoSouthSP2; the three border ends were moved onto new wall nodes (rows edited, nothing else in the file touched). The drawing was committed as the reference that converter drafts are compared against. |
| 47 | Areas outside the walls are clipped, which is good: it does not matter how far out they go; what matters is that they are as readable as possible. | Converter settings | `area_over_walls = 0.5`, `area_splines = 0.25`: 5 to 8 nodes per area, as in the reference. |
| 48 | There is still the problem wall near 5 to sort. (Fixed by the user: by 2 and 3, the border outside the wall deleted and the west wall extended to where the sketch's wall turns west.) | Converter (`convert.cut_back`) | The passage fill bridged the corner, so the two strokes there were inside it: one became a border, the other an `-outline none` piece that `smooth` then dropped, leaving the wall short. `cut_back` cuts the fill back to an outer wall when tracing out from it meets nothing before the fill's edge and the passage's leg is on the other side; it now also accepts the leg off to one side, within `corner_cone = 60` degrees of straight across, as at a corner. Both strokes are now wall, as in the reference. |

Draft 8 (the converter run again on the sketch, with the changes above)
is in `review/GoSouth.draft8.plan.th2`; the committed reference drawing
was put back afterwards. Against the reference, the converter still
cannot know that the wall by 10 closes 9 to 11 off from 19, or that the
strip by 17 is a pillar (two `wall-outline-none` findings): both are
hand work.
| 49 | Borders drawn over rocks deleted by hand (nine in all: three by 17 and 18 in the first edit, six by 3 to 4 and 8 to 13 now). Hopefully that can be tightened. | Converter (`marks.py`); `Style.md` | All but one were open brown strokes, part of the boulders' sketch. With `area_lines = false`, an open brown line at least half inside a boulder or debris area (allowing for the area's spline) is dropped: all eight brown ones go. The ninth was grey (a step or ledge) and is left. The converter also dropped a brown line by 20 that the reference kept: the user confirmed it should go, and it was removed from the reference. |

Draft 9 (`review/GoSouth.draft9.plan.th2`) against the reference: the
same from 1 to 12 apart from the wall by 10; the two `wall-outline-none`
findings by 17 (the pillar) remain hand work.

## Trident draft 1 review (2026-10-08)

Trident draft 1 (the converter as left after GoSouth) was edited by the
user in xTherion; their comments and edits, and what was done. The
user's file is still being edited and is not committed.

| # | Comment or edit | Kind | Outcome |
|---|---|---|---|
| 50 | The brown dashes are mud; a mud patch just above should have been expanded. (The user drew one mud area each from 1 to 6 and 26 to 30.) | Converter (`marks.py`); `Style.md` | `dash_max = 1.5` (brown dashes up to 1.5 m, roughly straight, are mud), `mud_near = 2.0` (one patch), `mud_grow = 0.7` (grown round its marks, following the passage); sand on mud merged in; kept off rock areas; marks touching a step are its ticks; a lone longer dash stays a line. One patch each now, as drawn. |
| 51 | (Edit) Three floor steps by 1 to 4 made walls, one deleted. | Converter (`notation.py`) | The mud dashes beside the walls had been read as step ticks: `brown_ticks = false`. |
| 52 | Why was the presumed wall added where there was nothing? (Two deleted.) | Converter (`tidy.close_outline`); `Style.md` | `tidy` drew a presumed wall where Therion might close a gap badly. `presumed_walls = false`: the gap is left for Therion. The outline stays valid. |
| 53 | A wall in space, deleted. The section should be in its own scrap and have its wall drawn. | Converter (`convert.section_th2`, `smooth`); `Style.md` | The "wall in space" was the cross-section at station 2: its own scrap, but drawn at its own coordinates, far from the cave in xTherion. `sections_in_place = true` draws it where it was sketched, by its section mark; `section_tol_rel = 0.05` refits its wall to its own size (it had become a triangle). |
| 54 | Far too many control points on many lines; the person drawing zooms so the legs fit the screen, so use a measure relative to, say, the three nearest legs. | Converter (`scale.py`, `smooth`, `marks.smooth_rows`) | `wall_tol_rel = 0.06`, `line_tol_rel = 0.05`: walls and other lines follow the sketch to within that share of the mean length of the 3 nearest legs. Trident: walls 0.72 to 0.64 points/m, other lines 2.49 to 1.91. `nodes.nearest_on` now samples long segments finely (a 12 m segment had been measured 0.15 m out). |
| 55 | Lots of little joins not continuous (a few fixed by hand). | Converter (`nodes.walls_meet`); `Style.md` | `wall_ends_meet = 0.45`: wall ends this close meet; a non-outline wall's end near another's side ends on it. Not across a survey leg, and undone if the outline would no longer be sound. The user's joins by 12 to 13 and 11 to 12 are now made. |
| 56 | (Found) Brown boulders drawn as curls, not quite closed, came out as dense little borders. | Converter (`marks.py`) | `curls_closed = true`: such a stroke is a closed loop (boulder or debris). |
| 57 | Fix "scrap intersects itself" in the user's edits, and say how. | Hand work (in the user's file) | Four places, each where two walls met (see below). Valid outline; Therion builds without a warning. |

How row 57 was fixed, in `LongwoodValleySink/Trident/Trident.plan.th2`:

1. By 2 (west wall): the new wall started on a node of the old one, but the
   old wall carried on 0.23 m past it, back down the new one. The old
   wall's last segment was deleted.
2. By 2 and 3: likewise, the old wall started 0.14 m back past the node
   where the new wall ended. Its first point was deleted.
3. By 13 to 17: the wall's last segment went from a point back to the
   same point with control points either side, a tiny loop left by
   moving the end. Deleted.
4. By the fork at 35/36 (37 one way, 38 and 39 the other): the 38 branch's
   west wall was `-outline none` above and a border below, so Therion
   closed the outline across the rock to the 37 branch. Both made outline
   walls; the border's hook at its foot cut off so it ends where the wall
   up to 37 starts.

Still open: the passage fill bridging rock (the inside of the U between
19 and 23, 12 to 13, 37 to 39), which leaves walls inside the fill as
`-outline none` or borders (the user made three of them walls by hand).
| 58 | Should joins also be relative, with an absolute as well? | Converter settings | `wall_ends_meet = 0.15` m or `wall_ends_meet_rel = 0.12` of the local leg length, whichever is larger (about 0.4 m in Trident, 0.26 m in GoSouth). |
| 59 | Many of the changes made to the user's edits came from two points too close together to see. A minimum distance between nodes, to let human editing work. | Converter (`nodes.thin`); `Style.md` | `node_gap = 0.05` m or `node_gap_rel = 0.02` of the local leg length, whichever is larger: a node closer than that to the one before goes (its two segments become one, keeping the outer control points; ends stay); a line's end at a wall reuses a node that close instead of adding one. Draft 2 had 17 such pairs, some of them repeated points; the new drafts none. |

The user's Trident drawing (with the row 57 fixes) was committed as its
first reference.

## Trident draft 3 review (2026-10-08)

The user edited `review/Trident.draft3.plan.th2` (a converter draft, not
the reference) to give examples.

| # | Comment or edit | Kind | Outcome |
|---|---|---|---|
| 60 | Lots of the walls are not close enough to the sketch (one or two redrawn as examples). | Converter (`smooth.fit_wall`) | Draft 3's walls strayed 0.116 m from the sketch (90th percentile, by length) against 0.058 m in the hand-drawn `Trident.plan.th2`. The raw conversion is close (0.039 m); the refit lost it: 6% of the leg length was too loose, and tightening alone spent nodes on hand wobble (2%: 310 nodes for 0.069 m). Now the wall is smoothed first (running mean over 3 times the tolerance, `wall_presmooth = 3`) and refitted to 2% (`wall_tol_rel = 0.02`): 0.059 m with 187 nodes (hand drawing: 0.058 m, 214). GoSouth unchanged (0.046 m). |
| 61 | A border on the edge changed to a wall (by 11 to 12; the wall from 12 round to 13). | Open | The fill took in only a sliver at the tip of the rock between the 12 and 13 branches, so this face is not dropped (row 63); still a border. |
| 62 | The rock to the left of station 5 should be drawn as in `Trident.plan`. | Converter (`convert.wall_strokes`) | It is a hook of the wall (an open black loop starting at the wall), not a boulder: `wall_hooks = true` keeps it as wall. |
| 63 | The border that should be a wall between 34, 35 and 36; the process keeps getting this type of passage wrong: a better solution is needed. | Converter (`convert.drop_rock_faces`) | The cause, here and at the U (19 to 23), 12 to 13 and the hook by 5: the passage fill is closed up by 1.8 m, which takes in rock wherever two passages (or the two sides of a bend) come within 3.6 m; walls inside it become borders or `-outline none`. Now (`rock_faces = true`) the fill is cut into faces along the wall strokes (gaps up to 0.3 m between strokes, and 0.5 m from a stroke's end to the fill's edge, closed first); a face with no leg or station whose edge has at least 0.5 m more than 0.3 m from any stroke (made by closing up, not sketched) is rock and goes; pillars and alcoves along sketched walls stay. Trident: the U, the tongue between the 37 and 38 branches, by 34 to 35 and by 7 to 8; GoSouth: between the 9 to 11 passage and 12, close to the wall the user drew by 10. |
| 64 | The rock area all outside the wall near station 15. | Converter (`marks.py`) | The mud patch in the alcove by 17, grown and run over the walls and splined, became a bubble outside its walls reaching into the passage by 13 to 15 (the walls clip only to the scrap's outline, which holds that passage too). An area no longer runs into another part of the passage. (To confirm this is the area meant.) |
| 65 | Ability to do lint checks would be good (node gap). | `th2lint` (`node-gap`); `Style.md` | `node-gap`: no two neighbouring nodes of a line within 0.05 m. Lint has no legs, so it uses the fixed minimum. It finds 5 lines in Trident.plan and 4 in GoSouth.plan, none in older drawings. These and the Trident reference's 6 `wall-outline-none` and 1 `end-on-node` findings (committed with it; CI's lint step failed on them) are in the baseline, to be cleared by hand. |

## Trident draft 4 review (2026-10-08)

| # | Comment or edit | Kind | Outcome |
|---|---|---|---|
| 66 | The area outside the wall is between 14 and 15 (deleted by hand), not the one by 17. | Converter (`marks.py`) | Boulders drawn along the wall, mostly outside it: the area, once run over the wall, was 0% inside the passage. An area less than `area_inside_min = 0.2` inside is not drawn (the lowest kept, the mud by 1, is 46%). |
| 67 | 34 to 36 better, but the points are too close together so it looks angular. | Converter (`nodes.thin`) | `node_gap_rel = 0.05` (about 0.17 m in Trident). |
| 68 | The border that comes very close to station 34 is well off the line (corrected by hand). | Converter (`marks.smooth_rows`) | With relative accuracy, borders were smoothed over 12.5 times their tolerance (2 m there, longer than the border). Now 3 times, as walls; `line_tol_rel = 0.02`. Borders and steps now 0.039 m from the sketch (90th percentile; the hand drawing 0.033 m); that border 0.010 m on average. |
| 69 | A hole in the wall to the left of station 34. | Converter (`smooth.one_line_per_wall`) | One sketch stroke round a bend: its middle 0.5 m was inside the fill, so `-outline none`, and dropped as doubling the walls either side. `wall_links = 0.4`: such a piece at least 0.4 m long, its ends on two outline walls' ends, is wall, turned to run on so the three join into one line. A link is kept only if the finished outline (after the refit) is as good without it; Therion builds draft 5 with no warning. |
| 70 | Should node separation take account of the change of direction? Large sweeps need only a couple of nodes, S bends more. | Converter (`nodes.merge`, `nodes.thin`); `Style.md` | Yes: the refit already places nodes by how far the curve strays (sweeps get few). Thinning now refits the joined segment to the shape of both (least squares, leaving and arriving as before), and keeps a node where that would move the line more than its tolerance: a tight S keeps its node, a sweep loses it. Below 5 cm a node always goes; nodes other lines end on, and boulder outlines (straight-sided), are left alone. |

Draft 5 against the hand drawing `Trident.plan.th2`: walls 0.059 m from
the sketch (179 nodes; hand 0.058 m, 214), other lines 0.039 m (198
nodes; hand 0.033 m, 285). GoSouth: walls 0.046 m, other lines 0.040 m.

## Trident draft 5 review (2026-10-08)

The user edited `review/Trident.draft5.plan.th2` with examples.

| # | Comment or edit | Kind | Outcome |
|---|---|---|---|
| 71 | `-outline none` should be very rare. | Converter | Draft 6 has 2 (draft 5: 5): mainly from row 72. |
| 72 | (Edit) The outer wall of the U by 20 to 21 was borders; made a wall. | Converter (`drop_rock_faces`) | The leg 20 to 22 runs out through that wall to a station beyond the drawing, so the rock it crossed counted as passage. A leg that crosses a wall stroke, and a station reached only by such legs, no longer keeps a face. |
| 73 | Dog-bone areas: the bit outside the walls is not needed (TridentSP1-clay10 changed; others are odd too). | Converter (`smooth._areas_to_outline`, settings) | `area_over_walls` 0.5 to 0.15 m; after the walls are final, each area (not water) is clipped to the outline the walls make plus that, and its spline given more points where it would bulge out (shrinking instead ate long thin areas). Areas now at most 0.2 m past the walls. |
| 74 | Control points ("splays") either side of a node should nearly always be in line, unless a sharp corner is needed. | Converter (`nodes.align_handles`) | `smooth_nodes = 60`: at a node turning less than 60 degrees the two control points are put in line with it (both turned to the mean direction, or the curve's to a straight neighbour's). Not boulders. |
| 75 | Areas other than water need some expansion to work well; they should not cross borders, floor steps etc. (Edits: one area over the floor of the U instead of many rock outlines drawn as borders; areas by 23 to 25 spread out to the walls and the step.) | Converter (`marks.py`) | `rock_curves`: curved brown strokes up to 1.5 m are rock outlines (not borders). `area_grow = 1.0`: rock areas grow 1 m round their rocks within the passage, cut at walls, steps and lines of `barrier_min = 1.5` m or more; shorter lines do not stop an area and go where mostly inside one. Overlapping rock areas of a kind merge. |
| 76 | (Edits) Many short borders deleted, most of them ticks drawn clear of their floor-step lines (15 to 18) or rock detail. | Converter (`notation.py`) | `tick_reach = 0.35`: a tick may stand up to 0.35 m clear of its line, only for a line that is not black (wall) or brown (mud beside it) and only ticks of the line's own colour. Borders under 1 m: draft 5 23, draft 6 6 (the user's GoSouth keeps 7, so there is no blanket rule). |
| 77 | Lines with 2 nodes connected to a line of the same type should be merged into it; strong consideration for 3 or 4 nodes. | Converter (`nodes.merge_short`) | `merge_short = 4`: a 2-node line whose end is within the wall-join reach (0.15 m or 12% of the legs' length) of the end of a line of the same type is merged into it unless it turns right back (over 120 degrees); up to 4 nodes if the join turns under 90 degrees. Gours stay separate; walls are joined as before. |

Not yet: the direction of floor-step ticks (two borders by 24 made floor
steps `-reverse on`); the wall from 12 round to 13.

## Converted run of both surveys (2026-10-08)

| # | Comment | Kind | Outcome |
|---|---|---|---|
| 78 | Short lines can be merged even when the join is sharp; the control points there need not line up, but most nodes should have theirs in line. | Converter (`nodes.merge_short`) | Merged at any angle; a sharp join keeps its corner (`align_handles` only lines up turns under 60 degrees). A floor step, pitch or overhang is only joined where it already runs the same way: turning one round would move its ticks to the other side (the cause of the steps the user reversed by 16 to 18 and by 25). |
| 79 | Ticks on the wrong side: possibly the line was reversed (`-reverse on`) rather than the ticks moved, which is convenient when editing but should not be in an original drawing. | Noted | The converter writes every line the right way round and never uses `-reverse on`; see row 78 for its own cause. |
| 80 | Lines of different kinds ending close together usually share the end (border to floor step to pit: the height changing along the edge). | Converter (`nodes.ends_meet`) | `ends_meet = true`: within the wall-join reach they meet halfway, or at the end already on a wall. |
| 81 | (Found by the build) MetaPost warned GoSouthSP1 "intersects itself". | Converter (`nodes.walls_meet`) | Joining two wall ends round a sharp corner (by 2 and 3) moved their curves into a small loop. Wall ends are now joined only where the walls carry on (turn under 75 degrees); at a corner Therion's straight closing is left. |
| 82 | Produce Trident.th2 and GoSouth.th2 for the user to go through. | Run | Both converted with the current settings into `LongwoodValleySink/{GoSouth,Trident}/*.plan.th2`, replacing the hand-edited references (still in git: GoSouth `efd798c`, Trident `1732381`). Build: no errors, no MetaPost warning for either. Walls 0.041 m (GoSouth) and 0.063 m (Trident) from the sketch (p90), other lines 0.043 and 0.045 m. Lint: the two `-outline none` walls of GoSouth's pillar by 17 (in the baseline). Known: the wall from 12 round to 13 in Trident. |

## Review of the converted run (2026-10-08)

| # | Comment | Kind | Outcome |
|---|---|---|---|
| 83 | Trident 3-5-6: the line was partly missing and partly a floor step, because of the mud beside it (path fixed by hand as one floor step). | Converter (`notation.py`, `marks.py`) | Its brown "ticks" were mud dashes: on a brown line, brown ticks are now mud where they are sparse (under 0.8 a metre) or there are four times as many other dashes within 1 m (`mud_ticks`; GoSouth's four brown steps by 24 to 27 stay steps). The middle had been dropped as rock detail: lines of 1.5 m or more never are. The sketch draws it in three pieces with gaps up to 0.9 m: brown line strokes ending within `chain_gap = 1.0` m of the next and carrying on (under 45 degrees) are one line. Now one border from 3 past 6. |
| 84 | 3-5-6: the debris should not go over that line; below it is the mud across to the wall, which seems squashed out. | Converter (`marks.py`) | Long brown lines now stop areas, and each rock's 1 m growth keeps to its own side of any line it would cross (the cut area had stayed joined round the line's ends). Mud is kept off the rocks themselves (0.3 m round each), not the hull of them all (which took in the mud beside them). Rock outlines are only clearly curved brown strokes. Now debris on one side, mud to the wall on the other (below 5 the debris still reaches round the line's end). |
| 85 | 15-16-18 shown as a border should be a floor step. | Converter (`notation.py`) | Two step lines side by side: the ticks between them went to whichever line was looked at first. Each tick now goes to its nearest line; most of the line is now part of a 7 m floor step (a 2.6 m piece near 16 is still a border). |
| 86 | Left of 5 the bulge is still wrong: there is an important difference between a deliberate bulge and a discontinuity. | Converter (`smooth.one_line_per_wall`, `fit_wall`) | The pocket's stroke was left off the outline (the walls either side had been joined straight across its mouth) and dropped as a stray piece. `pockets = true`: a piece off the outline, outside the passage, with both ends on one outline wall is spliced into that wall (its own curves kept, only if the outline is no worse). Wall smoothing now keeps clear corners (over 70 degrees at a coarse simplification) and smooths only between them, so the pocket keeps its shape (its inner corner, 0.15 m from the outer, is still a little rounded). |
| 87 | GoSouth: nodes still too close together on flowing curves; lots could be vastly reduced. | Converter setting | `node_gap_rel` 0.05 to 0.4: thinning only removes a node where the shape allows (row 70), so a large gap is safe. GoSouth walls 164 to 101 nodes (0.042 to 0.046 m from the sketch), Trident 187 to 149. |
| 88 | Produce both again. | Run | The user's Trident edits committed first (`2e39485`). Build: no errors, no MetaPost warning for either. GoSouth walls 0.046 m, other lines 0.063 m; Trident walls 0.065 m, other lines 0.113 m (the chained lines bridge the gaps in the sketch). |
