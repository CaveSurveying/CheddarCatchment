# Tools

How to get a new SexyTopo trip into the LongwoodValleySink survey, with
its plan drawn, and how the git copy is kept in step with SVN. The
conventions for drawing are in [`Style.md`](Style.md); the overall plan
is [`docs/PLAN-LongwoodValleySink.md`](../docs/PLAN-LongwoodValleySink.md).

| Path | What it is |
|---|---|
| `project.toml`, `project.py` | Per-cave settings: the master survey, the trial config, file and scrap names, line endings, licence, sheets. |
| `sketch2therion/` | Converts SexyTopo (and PocketTopo) sketches into Therion drawings (`.th2`), and checks drawings against the sketches (`review`). |
| `layout.thcfg`, `layout.th` | Export where Therion puts every station, and the centreline as SQL, for the converter. |
| `new-trip-template.th` | A starting point for a new trip's survey file. |
| `th2lint.py`, `th2lint-baseline.txt` | Checks drawings against the `[lint]` rules in `Style.md`. |
| `web/make_index.py` | The index page and statistics for a build. |
| `svn2git/` | The git copy of SVN: migration, verification and sync. |
| `requirements.txt` | Python libraries (`pip install -r tools/requirements.txt`). |

`sketch2therion/` and `web/` are adapted from the Swildons survey's
tools (<https://github.com/paperclipmonkey/caves-mendip-swildons>).
The tools are GPLv3 (`LICENSE`); the survey data and drawings are
CC BY-NC-SA 4.0.

## Setting up

You need Python 3.11 or later with the libraries in `requirements.txt`,
and Therion. CI uses Therion 6.4.0 in Docker (see
`.github/workflows/build.yml`) and is the reference renderer; a local
Therion (Ubuntu's `therion` package is 6.2.0) is fine for checking
logs. Run everything from the top of the repository unless it says
otherwise.

## Building

```bash
cd LongwoodValleySink && therion -l ../output/therion.log Plan_only.thcfg && cd ..
python3 tools/th2lint.py --from LongwoodValleySink/Plan_only.thcfg
python3 -m tools.web.make_index          # output/index.html, output/stats.md
```

This is a trial: only `Plan_only.thcfg` (the plan) is built and checked.
The other thconfigs are left as they are.

## A new trip

### Underground, in SexyTopo

The converter reads the sketch colours (the rules in full: `Style.md`,
"Sketching in SexyTopo"):

| Colour | Becomes |
|---|---|
| Black | Walls; a dashed black line is a wall not seen (`-subtype presumed`). A thin tapering triangle becomes a slope arrow pointing to its narrow end. |
| Brown | The floor: closed loops are boulders (0.3 m across or more) or debris (smaller); dots or short dashes are sand (mud is drawn as sand: no clay). In elevations, a brown floor line is sand. |
| Grey | Steps, ledges, pitches and channels inside the passage. |
| Blue | Water: hatching or a closed outline becomes a pool, a squiggle a water-flow arrow. |
| Green | Formations: concentric rings a boss, a small "Y" a stalactite, anything else flowstone; a solid green line a gour. In elevations, a green stroke carrying a wall on is flowstone wall. |
| Purple | Walls of a passage where it overlaps another (rare: elsewhere it is drawn in the normal colours); read as black, and may join a black wall. |
| Red, orange | Other lines of an overlapping passage, only to tell them apart: read by shape, as grey. |

Colours are hints: the shape decides (ticks make a step or pitch in any
colour, a closed loop is a boulder whatever its colour), and for an
overlapping passage its symbols say what its lines are. Notes (P for a
pitch, C for a climb) are SexyTopo text, not strokes.

Draw both the plan and the extended elevation: the elevation gives the
plan its floor steps, climbs and gradient arrows.

### After the trip

1. **Export** from SexyTopo (set up for the house style) into
   `LongwoodValleySink/X/`: `X.th`, the sketches in `X/Notes/`.
   `tools/new-trip-template.th` shows what `X.th` should contain.
2. **Tie it in** in `LongwoodValleySink/LongwoodValleySink.th`:
   `input X/X.th` and an `equate` to the station the trip started
   from. Build and check the log for loop errors.
3. **Therion's layout:**
   ```bash
   therion -l output/therion-layout.log tools/layout.thcfg
   ```
   writes `output/layout-plan.xvi`, `output/layout-extended.xvi` and
   `output/layout.sql`. Rerun it whenever the survey data change.
4. **Check the sketch:**
   ```bash
   python3 -m tools.sketch2therion check LongwoodValleySink/X/Notes/XP.xvi --survey X
   ```
   A fit within a few centimetres is normal; stations Therion doesn't
   know mean the trip isn't input, the layout is stale or `--survey`
   is wrong.
5. **Convert the plan:**
   ```bash
   python3 -m tools.sketch2therion plan LongwoodValleySink/X/Notes/XP.xvi \
     --survey X --floor LongwoodValleySink/X/Notes/XEE.xvi \
     --author 2026.04.25 "Andrew Atkinson" --copyright 2026 "CC BY-NC-SA 4.0" \
     -o LongwoodValleySink/X/X.plan.th2
   python3 -m tools.sketch2therion roofs LongwoodValleySink/X/X.plan.th2
   python3 -m tools.sketch2therion details LongwoodValleySink/X/X.plan.th2
   python3 -m tools.sketch2therion smooth LongwoodValleySink/X/X.plan.th2
   ```
   Scraps are named `XSP1`, `XSP2`, … (`project.toml`). Then
   ```bash
   python3 -m tools.sketch2therion place X
   ```
   files the drawing: it removes SexyTopo's empty `XP.th2`, inputs
   `X.plan.th2` in `X.th` with a `map XMP` of its scraps, and adds
   `XMP@X` to `LongwoodValleySinkMP` in `LongwoodValleySink.th`. `roofs` and
   `details` use the splays from `output/layout.sql`; `smooth` comes
   last. `tidy` redoes drawings converted earlier.
6. **Finish by hand** in xTherion (the sketch is linked as a
   backdrop): passage names at the label sizes in `Style.md`, flow
   arrows, `C2`/`P5`, `join`s to neighbouring scraps.
7. **Check**, as in `Style.md` ("Checking"), and with `review` below.
   For review on another computer,
   ```bash
   python3 -m tools.sketch2therion zip X review-X.zip --extra review/
   ```
   zips the drawing, its sketches (the backdrop works when unzipped),
   `X.th`, `LongwoodValleySink.th` and the files in `review/`.
8. **Commit** one survey per commit, with anything learnt added to
   `Style.md`. While SVN is the master copy, the drawing then goes to
   SVN by hand (see "SVN" below).

### Reviewing a drawing

```bash
python3 -m tools.sketch2therion review build      # output/review-plan.pdf, with station names
python3 -m tools.sketch2therion review show out.png 90 91 92 --survey NorthRift [--before old.pdf]
python3 -m tools.sketch2therion review check LongwoodValleySink/X/X.plan.th2
python3 -m tools.sketch2therion review gaps LongwoodValleySink/X/X.plan.th2 XSP1
```

- `build` makes the plan from `Plan_only.thcfg` with station names on;
  copy it aside before editing to have a "before".
- `show` puts the sketch (its colours, legs and stations, turned to
  the sheet) beside the drawing round those stations. Station names
  restart in each survey, so give `--survey`.
- `check` reports each outline as Therion and MetaPost see it: valid,
  and the turning number (0 means "scrap outline intersects itself").
- `fillcheck [--build] [--survey X ...]` builds the whole cave in plan,
  extended and 315 elevation (`check_build` in `project.toml`:
  `LongwoodValleySink/Whole_cave.thcfg`) and lists legs outside Therion's
  fill, and splay ends more than 0.5 m outside it, from the ESRI and XVI
  exports in `output/check/`. Run it at the end of every run that edits
  th2 files.
- `gaps` lists where Therion will close the outline with a straight
  line, and how much of it the sketch draws as wall.

## Another cave

Copy `project.toml` and change it; the tools read every cave-specific
name from it. `sections` (placing cross sections) is not ported. The converter
writes each section line with `-direction both`, the view direction on
its left and 0.5 m past the passage (`section_arrows`); placing the
section drawings clear of passages is still by hand.

## SVN

SVN (<https://www.cave-registry.org.uk/svn/CheddarCatchment/>) is the
master copy for now. `svn2git/` keeps git in step:

- `migrate.sh` makes the raw `git svn` mirror (outside the repository,
  `../CheddarCatchment-svn-mirror`) and a filtered copy with
  `SVN-Revision:` / `SVN-URL:` trailers, and checks it with `verify.py`.
- `sync.py` brings new SVN revisions onto the current branch. A
  revision whose changes git already has is recorded as an empty
  commit with its trailers.

Drawings made in git reach SVN by hand: the changed files are
committed to SVN as usual, and the next `sync.py` records that
revision. A file changed differently on both sides stops the sync for
a person to resolve.
