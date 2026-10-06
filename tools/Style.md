---
name: therion-drawing
description: Conventions for drawing or editing Therion scraps (.th2) in this survey, and the checks to run afterwards. Use when converting sketches, editing walls, water, labels, cross-sections or other symbols, or reviewing a drawing.
---

# Drawing Therion scraps in this survey

These come from a Therion expert's review of the converted drawings.
`tools/sketch2therion` (convert, `tidy`, `sections`) already follows
them; keep to them when editing by hand too.
- The sheets print the licence from `map-comment` in `gb_layout.thc`.


## Walls and the outline

- Walls have -outline out as default, it does not need to be set
- Walls are the scrap's outline. Draw each `line wall` with the passage
  on its LEFT or use -reverse on if passage on right
  (Footleg's drawings do; `-reverse on` flips a line).
- Walls enclosing an internal pillar should have -outline in set
- Do not close gaps between walls
- The outline must not cross itself, and no wall may loop back on
  itself. Otherwise Therion warns "invalid scrap outline" (no 3D model
  for the scrap) or MetaPost "scrap outline intersects itself".
- A line inside the passage (a ledge, the edge of another level) is a
  `line border`, not a wall.

## Symbols - General

- Default clipping settings normally give the best results.
- most symbols are clipped by outer walls, this property should be used to
  give the best effect.
- `-clip off`. Should only be used in exceptional circumstances
- labels, cross sections, should not overlap passage or each other including
  when combined with other surveys.

## Symbols - Points

- Slope arrows (point gradient) should be :-
	- inside the wall boundaries
	- not cross steps or pitch boundaries
	- not be in water
- Water flow should be inside the wall boundaries
- Climbs and pitches are labelled `C2`, `P5`: no units, placed
  outside the passage.
- Draught arrows (`point air-draught -orientation N`) go beside the
  passage, not across it, with a `point x y date -value YYYY.MM.DD`
  for when the draught was seen.

## Symbols - Lines

- Should be drawn with minimum points with smooth in both directions that
  allows the drawing line to be followed
- Rock/boulders should be closed and not use smooth.
- Rock/boulders are drawn in the order of the file and clip each other.
- Large boulders (`line rock-border -close on`) get a `line rock-edge`
  inside them to make them look  like 3d rocks.
- Rock/boulders on the edge of a passage are best drawn going over the wall
- significant boundaries and low steps < 20cm should be shown with border
- 20cm < step < 2m and easily climbed should be shown with floor step.
- harder climbs and anything > 2m should be shown as pitch boudary
- overhang should be used not ceiling-step

## Symbols - Areas

- Water: `line border -subtype invisible -id X -close on` with no other
  boarder
- Water that is against an outer wall is best drawn with the border
  outside the wall
- No other border should be added to water
- Areas can overlap to show a tranistion, or pebble in water
- Indiviually drawn rocks can be above or below the water, this requires
  carful ordering and use of clip

## Cross-sections

- line section should go completly accross the passage
- Direction arrows should not overlap the passage they mark and best not
  to overlap other passages
- `line section` should have `-direction both` as preference, arrows 
  may be only at the start or end if that is the only option 
- Therion draws the arrows on the line's left, so draw it
  with the view direction (along the survey, from the station towards the
  next) on its left.
- A section drawing must not overlap a passage or another section,
  including those of other surveys on the same sheet and the displaced
  upper level of the Entrance Series.
  `python3 -m tools.sketch2therion sections` fixes both (see
  `tools/README.md`).

## .thconfig layouts

- water: solid blue
- sump: a darker solid blue
- waterflow should be the same colour as water
- title should have a licence GPL3+
- Use 4 text sizes in decending order
	- Area name
	- Main passge
	- Minor passage
	- Feature 

## Checking

Build with the `swildons*.thconfig` files (see `README.md`), then:

- `grep -E "^therion: error|invalid scrap outline" output/*.log`:
  there should be none.
- `grep "intersects itself" output/*.log | sort -u`: only scraps you
  didn't touch.
- Render and look. poppler (pdftoppm, Evince, Okular) can show white
  holes in Therion's smooth altitude shading that aren't in the PDF;
  check with another renderer (MuPDF) before chasing them.
- pdf files have a bug that overlaping rocks fade rather than clip,
  do not try to fix.
