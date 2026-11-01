# Tools

How to get a new SexyTopo trip into the LongwoodValleySink survey, with
its plan drawn, and how the git copy is kept in step with SVN. The
conventions for drawing are in [`sketch2therion/Style.md`](sketch2therion/Style.md); the overall plan
is [`docs/PLAN-LongwoodValleySink.md`](../docs/PLAN-LongwoodValleySink.md).

| Path | What it is |
|---|---|
| `sketch2therion/` | The shared tools and drawing rules, the same for every cave: converting SexyTopo (and PocketTopo) sketches into Therion drawings (`.th2`) and checking them. How to use them is in [`sketch2therion/README.md`](sketch2therion/README.md). |
| `project.toml` | This cave's settings: the master survey, the trial config, file and scrap names, line endings, licence, sheets. |
| `th2lint-baseline.txt` | The findings in this cave's existing drawings. |
| `layout.thcfg`, `layout.th` | Export where Therion puts every station (for `check`, `joins`, `sections`, `review`), and the centreline as SQL for the converter. |
| `new-trip-template.th` | A starting point for a new trip's survey file. |
| `web/make_index.py` | The index page and statistics for a build. |
| `svn2git/` | The git copy of SVN: migration, verification and sync. |

`sketch2therion/` and `web/` are adapted from the Swildons survey's
tools (<https://github.com/paperclipmonkey/caves-mendip-swildons>).
The tools are GPLv3 (`LICENSE`); the survey data and drawings are
CC BY-NC-SA 4.0.

## Setting up

`tools/sketch2therion` is a link to `../../Therion-Sketching`, the
tools and drawing rules shared with other caves
([CaveSurveying/Therion-Sketching](https://github.com/CaveSurveying/Therion-Sketching)).
Clone that repository in the same folder as this one, so the link
finds it:

```bash
git clone https://github.com/CaveSurveying/Therion-Sketching.git
```

Every cave uses whatever is checked out there, so keep it up to date
with `git pull`, and make any change to the rules there. The first note
in each drawing gives the converter commit that made it.

You need Python 3.11 or later with the libraries in `sketch2therion/requirements.txt`,
and Therion. CI uses Therion 6.4.0 in Docker (see
`.github/workflows/build.yml`) and is the reference renderer; a local
Therion (Ubuntu's `therion` package is 6.2.0) is fine for checking
logs. Run everything from the top of the repository unless it says
otherwise.

## Building

```bash
cd LongwoodValleySink && therion -l ../output/therion.log Plan_only.thcfg && cd ..
python3 -m tools.sketch2therion.th2lint --from LongwoodValleySink/Plan_only.thcfg
python3 -m tools.web.make_index          # output/index.html, output/stats.md
```

This is a trial: only `Plan_only.thcfg` (the plan) is built and checked.
The other thconfigs are left as they are.

## A new trip

Follow "A new trip" in [`sketch2therion/README.md`](sketch2therion/README.md),
with this cave's names:

| | |
|---|---|
| Survey folder | `LongwoodValleySink/X/`, sketches in `LongwoodValleySink/X/Notes/` |
| Master file | `LongwoodValleySink/LongwoodValleySink.th` (`input X/X.th` and the `equate`) |
| Plan map | `LongwoodValleySinkMP`, in the master file |
| Layout | `tools/layout.thcfg` |
| Build | `Plan_only.thcfg`, as in "Building" above |
| Check build (`fillcheck`) | `LongwoodValleySink/Whole_cave.thcfg`: plan, extended and 315 elevation |
| Drawings | `--copyright 2026 "CC BY-NC-SA 4.0"` |

While SVN is the master copy, a committed drawing then goes to SVN by
hand (see "SVN" below).

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
