# Plan: LongwoodValleySink in git, with Swildons-style tools

Status: **plan only**, agreed 2026-10-06. Nothing below has been done
yet apart from committing this plan and the starting `tools/Style.md`.

## Goal

1. Make a git copy of the SVN repository
   <https://www.cave-registry.org.uk/svn/CheddarCatchment/>, limited to
   `LongwoodValleySink/` and `tools/`, with history.
2. Add the tools needed to work the way the Swildons survey does
   (<https://paperclipmonkey.github.io/caves-mendip-swildons/>, source
   at <https://github.com/paperclipmonkey/caves-mendip-swildons>), for
   LongwoodValleySink only.
3. Draw the **plan** `.th2` files that have not yet been drawn, for
   surveys undertaken **this year (2026)** only, copying the style and
   good practice of the rest of LongwoodValleySink.
4. Start `tools/Style.md` as a working file recording what improves the
   output, and improve it from what we learn.

## Decisions taken

| Question | Decision |
|---|---|
| What the git copy contains | `LongwoodValleySink/` and `tools/` with full SVN history (original author, date and message, plus `SVN-Revision:` and `SVN-URL:` trailers), keeping the SVN folder layout. Other caves later. |
| How 2026 surveys were sketched | SexyTopo. |
| Publishing | CI build artefacts and a PR comment only; no GitHub Pages (the repository is private). |
| `tools/Style.md` | Does not exist in SVN. Created new, starting from the supplied skill file (committed as-is alongside this plan), then revised as in Phase 5. |

Assumptions: "this year" means a centreline `date` in 2026. A plan is
"undrawn" if its plan `.th2` is missing, is SexyTopo's empty scrap (no
`line wall`), is not `input`, or is in no plan map.

## Background: what the Swildons system is

- An SVN-to-git migration of one folder, each commit with an
  `SVN-Revision: rNNN` / `SVN-URL:` trailer; access-restricted folders left out.
- `.github/workflows/build.yml`: Therion 6.4.0 from the pinned image
  `ghcr.io/paperclipmonkey/therion:6.4.0`, OSTN15 grid file cached,
  build fails on `therion: error`, statistics posted on PRs, sheets
  attached to the run.
- `web/make_index.py`: index page and `output/stats.md`.
- `tools/sketch2therion/`: SexyTopo/PocketTopo sketches to `.th2`
  (`check`, `plan`, `extended`, `roofs`, `details`, `tidy`, `sections`),
  with `tools/layout.thconfig` and `tools/new-trip-template.th`.
- `.claude/skills/therion-drawing/SKILL.md`: drawing conventions.
- About 35 places hard-code Swildons names (`Swil1P_`, `Swildons_MAP…`,
  `swildonsmaster.th`, `SHEETS` in `sections.py`); these move into a
  per-cave config.

## Phase 0: Prerequisites

1. Environment network access must allow `www.cave-registry.org.uk` and
   `cave-registry.org.uk` (optionally `ghcr.io`, `cdn.proj.org`), in a
   new session.
2. Toolchain: `subversion`, `git-svn` (apt); `git-filter-repo`,
   `shapely`, `pytest` (pip); Therion via the pinned CI image, or apt's
   Therion 6.2.0 for local log checks only (CI is the reference renderer).

## Phase 1: Inventory (read-only; stop and confirm)

3. `svn log -v --xml` for `LongwoodValleySink/` and `tools/`: revisions,
   authors, any paths returning 403 (restricted, to be left out). Note
   `svn:externals`, `svn:ignore`, `svn:eol-style`, large binaries.
4. `tools/svn2git/inventory.py` writes `docs/lvs-inventory.md`: every
   survey `.th` with date, team, length and plan `.th2` status; the 2026
   surveys with undrawn plans; whether their SexyTopo `.xvi` files are
   present.
5. Record LongwoodValleySink house style: naming prefixes and scrap ids,
   map files and `join`s, the layout/`.thc` in use, scale, `cs` and fix,
   label sizes, how boulders, sediment and water are drawn.
6. **Check point** with the user: the list of surveys to draw; the SVN
   username to "Name <email>" mapping; the CheddarCatchment licence (the
   Swildons tools are GPLv3).

## Phase 2: Migration (`tools/svn2git/`)

7. `git svn clone <repo> --include-paths='^(LongwoodValleySink|tools)(/|$)'
   --authors-file=tools/svn2git/authors.txt` (flat layout, unless the
   inventory shows `trunk/`).
8. `git filter-repo --message-callback`: turn each `git-svn-id:` line
   into `SVN-Revision:` / `SVN-URL:` trailers; drop empty commits.
9. `svn:ignore` to `.gitignore`, plus build outputs (`output/`, `proj/`,
   `*.3d`, `*.lox`, `*.pdf` in project folders) and `__pycache__/`.
10. `tools/svn2git/verify.py`: `diff -r` of git HEAD against `svn export`
    HEAD for both folders; commit count equals the SVN revisions touching
    them; sampled author/date check.
11. Push to `claude/eager-edison-jpd51y`. There is no `main` yet: the user
    chooses whether this branch becomes `main` or a PR goes into a new one.
    `tools/Style.md` and this plan are rebased on top as new files.

## Phase 3: Tools copied and adapted

| New path | From | Change |
|---|---|---|
| `tools/project.toml` | new | Per-cave config: master `.th`, plan/elevation maps, file prefixes, sheet scale, sheets for `sections`. LongwoodValleySink first. |
| `tools/sketch2therion/` | Swildons | Names read from `project.toml`; Swildons output unchanged (regression test). |
| `tools/layout.thconfig`, `tools/layout.th` | Swildons | Point at the LongwoodValleySink master survey. |
| `tools/new-trip-template.th` | Swildons | LongwoodValleySink naming and equate example. |
| `tools/web/make_index.py` | Swildons | Sheet list from config; writes `output/stats.md`. |
| `tools/th2lint.py` | new | Checks every `.th2` against the `[lint]` rules in `tools/Style.md`. |
| `.github/workflows/build.yml` | Swildons | LongwoodValleySink thconfig(s), pytest, `th2lint`, Therion error gate, PR comment, run artefact. No Pages deploy. |
| `.claude/skills/therion-drawing/SKILL.md`, `AGENTS.md` | Swildons | Short pointers to `tools/Style.md`, the single source of truth. |
| `tools/README.md`, `README.md` | Swildons | LongwoodValleySink SexyTopo workflow, building, history. |

Not copied: `routes/`, `surface/` (Swildons-specific; possible later).

## Phase 4: Draw the 2026 plans (plan view only)

For each confirmed survey:

1. SexyTopo export and originals in the folder LongwoodValleySink uses
   (else `SexyTopo/<yyyymmdd>_<Where>/`). Ask for any that are missing.
2. Build; `therion tools/layout.thconfig`.
3. `python3 -m tools.sketch2therion check plan.xvi --survey X`; report a
   poor fit.
4. `python3 -m tools.sketch2therion plan plan.xvi --floor ee.xvi
   --author … --copyright … --map-scale <LVS scale>`, written over the
   empty scrap under its existing name. The elevation sketch is used for
   floor steps only; no elevation `.th2` is drawn.
5. `roofs` (walls from splays where unsketched), `details`, `tidy`;
   `sections` only if cross-sections were sketched and LongwoodValleySink
   plans show them.
6. Hand-finish to match existing LongwoodValleySink plans: passage names
   at its label sizes, boulders, water and flow, `C2`/`P5`, `join`s to
   neighbouring scraps.
7. Un-comment the `input` lines; add the scraps to the plan map.
8. Checks: no `therion: error` or `invalid scrap outline`, no new
   "intersects itself", `th2lint` clean, opens in xTherion without error,
   before/after PDF compared.
9. One commit per survey. Anything learnt goes into `tools/Style.md` in
   the same commit.

## Phase 5: Revise `tools/Style.md`

The committed file is the supplied starting version, unchanged. Revise it:

1. **General to the catchment:** remove the skill front-matter, Footleg
   references, the "displaced upper level of the Entrance Series" and the
   `swildons*.thconfig` commands; use LongwoodValleySink's thconfig names
   with a placeholder per cave.
2. **British English spelling:** boarder → border, tranistion →
   transition, Indiviually → Individually, carful → careful, completly
   accross → completely across, decending → descending, passge → passage,
   boudary → boundary.
3. **Precise symbol names:** "pitch boundary" → `line pit`; "floor step"
   → `line floor-step`, low side on the line's left; "do not close gaps"
   → also no invisible walls and no `-outline none` fill line, as Therion
   closes the outline itself; closed rocks → `-close on`, ending exactly
   on the first point (avoids xTherion's "no such element in array");
   the four text sizes → `-scale xl / l / m / s` with a
   LongwoodValleySink example of each.
4. **New sections:** SexyTopo sketching (colours: black walls, brown/grey
   another level, blue water, green formations, red/orange notes, which
   the converter ignores; draw both views and cross-sections); splay-based
   fill where unsketched, drawn as presumed walls, never guessed;
   `-author` / `-copyright` on every scrap; git and CI (case-sensitive
   filenames, one survey per commit, CI and `th2lint` green); "how to
   update this file": add whatever a review or drawing session teaches,
   in the same commit.
5. Tag machine-checkable rules `[lint]`.

## Unit tests (`tests/`, pytest, run in CI)

- **svn2git:** `git-svn-id` line becomes the two trailers with the body
  kept; an unmapped author fails listing the missing usernames; the path
  filter accepts `LongwoodValleySink/a.th` and `tools/Style.md` and rejects
  `LongwoodValleySinkOld/` and `Other/tools/`; `verify` reports equal and
  differing trees.
- **inventory:** date parsing (`date 2026.03.14`, ranges, several dates,
  commented-out dates, nested surveys); year filter with a fixed "today"
  (excludes 2025.12.31, includes 2026.01.01); empty SexyTopo scrap versus
  drawn scrap; commented-out `input`; scrap in no map; `input` whose case
  differs from the file.
- **sketch2therion:** a Swildons fixture `.xvi` gives byte-identical
  output before and after the config refactor; the LongwoodValleySink
  `project.toml` loads; SexyTopo `.xvi` reader gets stations and colour
  classes; walls have the passage on their left (signed area); closed
  lines end on their first point; no invisible walls; climb labels have
  no units.
- **th2lint:** a failing and a passing tiny `.th2` per rule (closed line
  not ending on its first point, smoothed `rock-border`, `ceiling-step`,
  unexplained `-clip off`, undated draught, bad label `-scale`).
- **Style.md and th2lint stay in step:** every `[lint]` rule in
  `tools/Style.md` has a matching `th2lint` check.
- **make_index:** statistics parsed from a sample `therion.log`; a
  missing PDF is skipped without failing.

## Delivery

Commits pushed to `claude/eager-edison-jpd51y`; changed files also
supplied as numbered zips (`CheddarCatchment-1.zip`, `-2`, …) with their
relative paths.

## Open question

Will SVN stay the master copy? If so, add `tools/svn2git/sync.sh` to
bring new revisions across incrementally.
