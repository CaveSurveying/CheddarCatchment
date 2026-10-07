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
| 49 | Borders drawn over rocks deleted by hand (nine in all: three by 17 and 18 in the first edit, six by 3 to 4 and 8 to 13 now). Hopefully that can be tightened. | Converter (`marks.py`); `Style.md` | All but one were open brown strokes, part of the boulders' sketch. With `area_lines = false`, an open brown line at least half inside a boulder or debris area (allowing for the area's spline) is dropped: all eight brown ones go. The ninth was grey (a step or ledge) and is left. The converter also drops a brown line by 20 that the reference keeps: to ask. |

Draft 9 (`review/GoSouth.draft9.plan.th2`) against the reference: the
same from 1 to 12 apart from the wall by 10; the two `wall-outline-none`
findings by 17 (the pillar) remain hand work.
