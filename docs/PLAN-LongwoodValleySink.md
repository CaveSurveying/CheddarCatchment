# Plan: LongwoodValleySink in git, with Swildons-style tools

Status: agreed 2026-10-06. **Phase 1 done** (findings and check point
answers in `docs/lvs-phase1.md`, survey table in `docs/lvs-inventory.md`).
**Phase 2 done** (`tools/Style.md` revised). **Phase 3 done**
(2026-10-07): SVN history to r501 merged, `verify` clean, authors with
placeholder emails. **Phase 4 done** (2026-10-07): the tools, the
plan-only thconfig and CI (see "Phase 4 as built"). **Phase 5 started**
(2026-10-07): `place` and `zip`, and a test review zip of the GoSouth
draft. The plan was revised on 2026-10-06 after review
against the SVN repository (revision 501), then for the
`Plan_only.thcfg` trial scope, and on 2026-10-07 for Phase 4.

## Goal

1. Make a git copy of the SVN repository
   <https://www.cave-registry.org.uk/svn/CheddarCatchment/>, limited to
   `LongwoodValleySink/` and the root files it needs to build
   (`common_layout.th`, `Symbols/`), with history.
2. Add a `tools/` folder, **new in git** (there is no `tools/` in SVN),
   holding the tools needed to work the way the Swildons survey does
   (<https://paperclipmonkey.github.io/caves-mendip-swildons/>, source
   at <https://github.com/paperclipmonkey/caves-mendip-swildons>), for
   LongwoodValleySink only.
3. Add `LongwoodValleySink/Plan_only.thcfg`, a new thconfig that
   produces **only the plan**, with its own copy of the `plan` layout
   from the existing `LongwoodValleySink/thconfig`.

**This is a trial run.** Only `LongwoodValleySink/Plan_only.thcfg` is
built and checked. The existing `thconfig`, the elevation, the 3D model
and every other thconfig are left exactly as they are and are not run;
they will be worked on over time.
4. Draw the **plan** `.th2` files that have not yet been drawn, for
   surveys undertaken **this year (2026)** only, copying the style and
   good practice of the rest of LongwoodValleySink.
5. Keep `tools/Style.md` as a working file recording what improves the
   output, and improve it from what we learn.

## Decisions taken

| Question | Decision |
|---|---|
| What the git copy contains | `LongwoodValleySink/`, `common_layout.th` and `Symbols/` with full SVN history (original author, date and message, plus `SVN-Revision:` and `SVN-URL:` trailers), keeping the SVN folder layout. Anything further found by the dependency walk (Phase 1) is added at the check point. Other caves later. |
| `tools/` | Does not exist in SVN. Created new in git; it has no SVN history. |
| thconfig naming | The current convention is `name.thcfg` (as the root's `LongwoodValley.thcfg`). Older names (`thconfig`, `thconfig_A0plan`, `thconfig_overview`, …) are still in use and are not renamed. |
| Plan-only build | New `LongwoodValleySink/Plan_only.thcfg`. The layout blocks are **copied** into it from `LongwoodValleySink/thconfig`, which is not changed; the two are expected to diverge. |
| Trial scope | Only `Plan_only.thcfg` is run, locally and in CI. Everything else is ignored for now. |
| Licences | Aligned. Survey data: CC BY-NC-SA, as on the existing sheets (version to confirm). Tools: GPLv3, as the Swildons tools. `Style.md` and `Plan_only.thcfg` say the same; the existing files are left as they are in this trial. |
| How 2026 surveys were sketched | SexyTopo. |
| Publishing | CI build artefacts and a PR comment only; no GitHub Pages (the repository is private). |
| `tools/Style.md` | Does not exist in SVN. Created new, starting from the supplied skill file (committed as-is alongside this plan), then revised as in Phase 2. |
| Working branch | `claude/serene-cerf-h45zcu`. |

Assumptions: "this year" means a centreline `date` in 2026. A plan is
"undrawn" if its plan `.th2` is missing or is SexyTopo's empty scrap (no
`line wall`). A scrap that is drawn but not `input`, or in no plan map,
is **reported, not drawn**: LongwoodValleySink already comments out some
inputs on purpose (`GoWest`, `TickleRift`).

## Findings from the SVN repository (revision 501)

- No `tools/` folder at the root (404).
- `LongwoodValleySink/thconfig` ends with `input ../common_layout.th`,
  which in turn has `input Symbols/Symbols.th`. `Symbols/` (`Areas/`,
  `Lines/`, `Special/`) has no further outside dependencies.
- The `plan` layout does `\loadpicture{Outputs/LongwoodValleySinkE315.pdf}`
  (the elevation inset), but the elevation export is commented out and
  `LongwoodValleySink/Outputs/` is empty, so a clean checkout cannot
  build the plan sheet as it stands.
- Licences conflict: the map header says "Copyright 2014-25 CC BY NC SA";
  `LongwoodValleySink.th` has `#copyright 2014 "GNU GPL"`; the starting
  `Style.md` says GPL3+; the Swildons tools are GPLv3.
- The root also has `Long_Vall_Sink/` and `Longwood/`: possible earlier
  homes of the same data.
- House style seen so far: scale 1:500, base-scale 1:350, plan rotated
  45°, elevations projected to 315°, scrap ids such as `CyclopsSP1` and
  `CrossRoadsSE315_3`, maps `…MP` / `…ME315` in each survey's `.th`,
  grouped in `Maps.th`.

## Background: what the Swildons system is

- An SVN-to-git migration of one folder, each commit with an
  `SVN-Revision: rNNN` / `SVN-URL:` trailer; access-restricted folders left out.
- `.github/workflows/build.yml`: Therion 6.4.0 from the image
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

1. Network access to `www.cave-registry.org.uk` (confirmed working in
   this environment); optionally `ghcr.io`, `cdn.proj.org`.
2. Toolchain: `subversion`, `git-svn` (apt); `git-filter-repo`,
   `shapely`, `pytest` (pip); Therion via the CI image, or apt's
   Therion 6.2.0 for local log checks only (CI is the reference renderer).

## Phase 1: Inventory (read-only; stop and confirm)

3. `svn log -v --xml` for `LongwoodValleySink/`, `common_layout.th` and
   `Symbols/`: revisions, authors, any paths returning 403 (restricted,
   to be left out). Note `svn:externals`, `svn:ignore`, `svn:eol-style`.
   Without an `svn` client, `tools/svn2git/svnhttp.py` reads the same
   over plain HTTP (WebDAV `PROPFIND`, `REPORT log-report`, `GET`).
4. **Copy history:** `svn log --stop-on-copy` and the `copyfrom-path` of
   each path. If LongwoodValleySink (or files in it) were copied or
   renamed from `Long_Vall_Sink/`, `Longwood/` or elsewhere, add those
   source paths to the include filter for the revisions before the copy,
   so history is not cut at the copy.
5. **Dependency walk:** `tools/svn2git/deps.py` follows every `input`,
   `source`, `load` and `\loadpicture` from
   `LongwoodValleySink/Plan_only.thcfg` (as planned) and lists every
   file outside
   `LongwoodValleySink/` that the build needs.
6. **Large files:** list binaries over 1 MB (`.xcf`, `.odt`, photos,
   PDFs) and decide on Git LFS or leaving them out.
7. `tools/svn2git/inventory.py` writes `docs/lvs-inventory.md`: every
   survey `.th` with date, team, length and plan `.th2` status; the 2026
   surveys with undrawn plans; drawn-but-not-input scraps (reported
   only); whether their SexyTopo `.xvi` files are present.
8. Record LongwoodValleySink house style in full (adding to the findings
   above): `cs` and fix, label sizes, `join`s, how boulders, sediment and
   water are drawn.
9. **Check point** with the user:
   - the list of surveys to draw;
   - the SVN username to "Name <email>" mapping;
   - the CC BY-NC-SA version for the survey data (the sheets give none);
   - **whether SVN stays the master copy** (this decides how Phase 3 is
     done; see "Incremental sync");
   - Git LFS;
   - extra paths from the dependency walk and copy history.

## Phase 2: First revision of `tools/Style.md`

Done before the tools, because `th2lint` (Phase 4) reads the `[lint]`
rules from it. The committed file is the supplied starting version,
unchanged. Revise it:

1. **General to the catchment:** remove the skill front-matter, Footleg
   references, the "displaced upper level of the Entrance Series" and the
   `swildons*.thconfig` commands; use `LongwoodValleySink/Plan_only.thcfg`
   with a placeholder per cave, and state the `name.thcfg` convention
   for new thconfigs.
2. **British English spelling:** boarder → border, tranistion →
   transition, Indiviually → Individually, carful → careful, completly
   accross → completely across, decending → descending, passge → passage,
   boudary → boundary, overlaping → overlapping; "look  like" (double
   space).
3. **Precise symbol names:** "pitch boundary" → `line pit`; "floor step"
   → `line floor-step`, with which side the low side is on **confirmed by
   a test render** before it becomes a rule; "do not close gaps" → also
   no invisible walls and no `-outline none` fill line, as Therion closes
   the outline itself; closed rocks → `-close on`, ending exactly on the
   first point (avoids xTherion's "no such element in array"); water →
   the `area water` refers to the border's `-id`; the four text sizes →
   `-scale xl / l / m / s` with a LongwoodValleySink example of each.
4. **Licence:** "title should have a licence GPL3+" becomes CC BY-NC-SA
   for the survey data (the tools are GPLv3).
5. **New sections:** SexyTopo sketching (colours: black walls, brown/grey
   another level, blue water, green formations, red/orange notes, which
   the converter ignores; draw both views and cross-sections); splay-based
   fill where unsketched, drawn as presumed walls, never guessed;
   `-author` / `-copyright` on every scrap; git and CI (case-sensitive
   filenames, one survey per commit, CI and `th2lint` green); "how to
   update this file": add whatever a review or drawing session teaches,
   in the same commit.
6. Tag machine-checkable rules `[lint: id]`, the id being the
   `th2lint` check's name.

Phase 5 keeps revising it as drawing teaches us more.

## Phase 3: Migration (`tools/svn2git/`)

10. `git svn clone <repo>
    --include-paths='^(LongwoodValleySink(/|$)|Symbols(/|$)|common_layout\.th$)'
    --authors-file=tools/svn2git/authors.txt` (flat layout), plus any
    paths added at the check point (proposed: the root `Symbols.th`, from
    which `Symbols/Symbols.th` was copied at r416). Phase 1 found no
    restricted (403) paths. Expect 56 revisions (60 with the root
    `Symbols.th`; that is what the migration gave).
11. If SVN stays the master copy, keep this raw `git svn` clone as a
    mirror and do step 12 on a copy, because `git filter-repo` removes
    the metadata an incremental sync needs.
12. `git filter-repo --message-callback`: turn each `git-svn-id:` line
    into `SVN-Revision:` / `SVN-URL:` trailers; drop empty commits.
13. `svn:ignore` to `.gitignore` (the only one, `svn:global-ignores`
    `Triasic` / `Triasic2`, is left out: those folders were renamed to
    `Triassic` / `Triassic2` long ago), plus build outputs (`output/`, `proj/`,
    `*.3d`, `*.lox`, and `LongwoodValleySink/Outputs/*`, keeping the
    folder with a `.gitkeep` because the thconfigs write into it) and
    `__pycache__/`.
14. `tools/svn2git/verify.py`: `diff -r` of git HEAD against `svn export`
    HEAD for every included path; commit count equals the SVN revisions
    touching them; sampled author/date check.
15. The plan and all work stay on the working branch
    `claude/serene-cerf-h45zcu`. The filtered SVN history (an
    independent root) is joined to it with one
    `git merge --allow-unrelated-histories` commit, so neither the
    branch nor `main` is rewritten and no force push is needed. `main`
    (which already holds the plan) is updated only by a pull request
    from the working branch, when the user asks for one.

## Phase 4: Tools added, the plan-only thconfig, and CI

### `LongwoodValleySink/Plan_only.thcfg`

- Named by the current `name.thcfg` convention. The existing
  `LongwoodValleySink/thconfig` is **not changed**.
- `encoding utf-8`, `source LongwoodValleySink.th`, the existing
  `select LongwoodValleySinkMP@LongwoodValleySink -map-level 1`, and one
  export: `export map -proj plan -layout plan -o
  Outputs/LongwoodValleySinkP.pdf`. No elevation, model or `.lox`
  export, and no elevation `select`.
- **Layout copied:** the `plan` and `local` layout blocks are copied
  from `thconfig` (`Projected315` is not needed), followed by
  `input ../common_layout.th` as now. They are expected to diverge from
  `thconfig` over time.
- **Changes in the copy**, kept to what a plan-only build needs:
  - remove the elevation inset
    (`\legendbox{-2}{104}{SW}{\loadpicture{Outputs/LongwoodValleySinkE315.pdf}}`),
    since no elevation PDF is made; this lets it build from a clean
    checkout;
  - the location, grade, licence and credits text (`map-comment`) is
    defined only in the `Projected315` layout and reaches the plan
    sheet through the elevation inset, so removing the inset removes it.
    The copied `plan` layout therefore gains that `map-comment`, with
    the aligned CC BY-NC-SA licence wording, so the sheet keeps its
    licence and credits (position checked on the render);
  - otherwise unchanged (scale 1:500, base-scale 1:350, rotate 45, the
    same `code tex-map`).
- Built with `therion Plan_only.thcfg` from `LongwoodValleySink/`,
  output to `LongwoodValleySink/Outputs/LongwoodValleySinkP.pdf`.

### `tools/` (all new)

| New path | From | Change |
|---|---|---|
| `tools/project.toml`, `tools/project.py` | new | Per-cave config: master `.th`, thconfig (`Plan_only.thcfg`), the plan map and the file it is in, file/scrap/map name patterns, which sketches are plans, line endings, map scale, licence, sheets. LongwoodValleySink first. |
| `tools/svn2git/` | new | `svnhttp.py`, `deps.py`, `inventory.py`, `authors.txt`, `verify.py`, `migrate.sh`, and `sync.py` (Python, so it shares the rewrite and is tested) as SVN stays master; `sync.py` records SVN revisions already in git (option C, below). |
| `tools/sketch2therion/` | Swildons | Names read from `project.toml`; output on LongwoodValleySink sketches identical to the unmodified upstream code apart from the licence line (regression test). `sections` not ported (no LongwoodValleySink plan has cross-sections). `review` ported, working per survey on a rotated sheet. |
| `tools/layout.thcfg`, `tools/layout.th` | Swildons | Renamed from `layout.thconfig` to the `.thcfg` convention; point at the LongwoodValleySink master survey; also export `output/layout.sql` for `roofs` and `details`. |
| `tools/new-trip-template.th` | Swildons | LongwoodValleySink naming (`…SP1`, `…SE315_1`) and equate example. |
| `tools/web/make_index.py` | Swildons | Sheet list from config; writes `output/index.html` and `output/stats.md` (statistics from the log). |
| `tools/th2lint.py` | new | Checks the `.th2` files that `Plan_only.thcfg` builds against the `[lint]` rules in `tools/Style.md`. Existing drawings are covered by a baseline file (`tools/th2lint-baseline.txt`); CI fails only on new findings, and fixing a baseline entry removes it. |
| `.github/workflows/build.yml` | Swildons | Builds `LongwoodValleySink/Plan_only.thcfg` only, pytest, `th2lint`, Therion error gate, PR comment, run artefact. Therion image pinned by digest, not tag. OSTN15 grid only if the cave's `cs` needs it. No Pages deploy. |
| `.claude/skills/therion-drawing/SKILL.md`, `AGENTS.md` | Swildons | Short pointers to `tools/Style.md`, the single source of truth. |
| `tools/README.md`, `README.md` | Swildons | LongwoodValleySink SexyTopo workflow, building, history. |

Not copied: `routes/`, `surface/` (Swildons-specific; possible later).
Any Swildons fixture copied for the regression test is checked for a
licence that allows it.

### Phase 4 as built (2026-10-07)

- `review build` derives its config from `Plan_only.thcfg` (no
  separate `tools/review.thcfg`), with station names on and the
  centreline shown. `review show` places stations from the printed
  station names, allowing for the sheet's 45° rotation, and takes
  `--survey` because station names restart in each survey.
- `roofs` reads Therion's SQL with bare `nan` values (90° projected
  maps) as NULL.
- The CI Therion image is pinned to
  `sha256:6f7365a75e338a99a3772e6aaf48872f75717ebd4167ef5bd5e88777b24a2d45`
  (tag 6.4.0). No OSTN15 grid: the plan-only build does not need it
  (Therion 6.2.0 builds it without), to be confirmed by the first CI
  run on 6.4.0.
- `LongwoodValleySinkMP` is in `LongwoodValleySink.th`, not `Maps.th`
  (which holds group maps such as `CyclopsMP`); corrected in
  `tools/Style.md` and `docs/lvs-phase1.md`.
- Local build (Therion 6.2.0): no errors, 5 "scrap outline intersects
  itself" warnings from existing drawings. The sheet's `map-comment`
  still says "Length 1004.00m. Vertical Range 126.27m" (copied from
  `thconfig`); Therion now gives 1682.2 m and 132.19 m with the 2026
  surveys. Left for the user to decide.
- For Phase 5: on GoSouth the converter's whole pipeline (`plan`,
  `roofs`, `details`, `smooth`) gives a valid outline but leaves one
  wall with `-outline none`, which `th2lint` (`wall-outline-none`)
  rejects. To be settled when drawing: fix by hand, or refine the rule
  if such a wall is right.

## Phase 5: Draw the 2026 plans (plan view only)

Agreed 2026-10-07. The ten 2026 surveys, neighbours first so that joins
have something to meet:

| Order | Survey | Joins |
|---|---|---|
| 1 (pilot) | GoSouth | 27@CrystalPitch |
| 2 | Trident | 133@CrossRoads |
| 3 | TridentCentre, TridentLeft | 12@Trident, 11@Trident |
| 4 | IDontCare, BoldStep, TritonNorth, TritonSouth | 32, 36, 37, 38@TridentLeft |
| 5 | Connection, FairyChimneys | 94@NorthRift, TritonSouth, BoldStep |

Status 2026-10-08: all ten converted, plans and extended elevations
(the elevations added at the user's request); GoSouth and Trident
reviewed and hand-edited, the other eight first drafts for review (see
`docs/lvs-phase5-log.md`).

What the pilot teaches goes into `tools/Style.md` and the converter
before Trident is started. A test review zip of the GoSouth draft
was sent first, to check the backdrop opens on the user's computer.

For each survey X:

1. **Prepare:** `therion -l output/therion-layout.log tools/layout.thcfg`;
   `python3 -m tools.sketch2therion check X/Notes/XP.xvi --survey X`
   (stop and report a fit worse than about 0.3 m); keep the current
   plan PDF as "before".
2. **Convert:** `plan --floor` (the elevation sketch gives floor steps
   only; no elevation `.th2` is drawn), `roofs`, `details`, `smooth`,
   writing `X/X.plan.th2` with the sketch linked as xTherion's backdrop.
3. **File it:** `python3 -m tools.sketch2therion place X` removes
   SexyTopo's empty `XP.th2`, inputs `X.plan.th2`, writes `map XMP` and
   adds `XMP@X` to `LongwoodValleySinkMP`.
4. **Hand-finish** (editing the `.th2` text): water and flow,
   `C2`/`P5`, anything the conversion got wrong against the sketch.
   Passage names and joins come later (stages 5b and 5c).
5. **Check:** build `Plan_only.thcfg` with no `therion: error` or
   `invalid scrap outline` and no new "intersects itself"; `th2lint`
   clean; `review check` valid; opens in xTherion (headless, Xvfb)
   without an error.
6. **Review zip** (`python3 -m tools.sketch2therion zip X OUT.zip
   --extra review/`), opened by the user in xTherion or wtherion: the
   `.th2`, its sketches (the backdrop path works when unzipped), `X.th`,
   `LongwoodValleySink.th`, and under `review/` the plan PDF before and
   after, the review plan with station names, `review show` pictures,
   and `NOTES.md` (what was converted, what was changed by hand and
   why, the check results, and the questions). The pictures and PDFs
   are also shown in the chat.
7. **Improve the process:** each review comment is recorded in
   `docs/lvs-phase5-log.md` and handled as a converter fault (fixed in
   `sketch2therion`, with a test), a rule (`Style.md`, with a `th2lint`
   check where possible) or one-off hand work.
8. **Commit** one survey per commit, only after the user approves its
   zip; then the changed files go to SVN by hand (option C).

### Later stages

- **5b, passage names** (decided after the GoSouth test zip): added
  once the drawings are reasonable, with the user.
- **5c, joins to neighbouring surveys** (decided after the GoSouth test
  zip): once every survey's drawing is reasonable on its own, join each
  to its neighbours (`join`s, walls meeting without overlaps, outlines
  not crossing, no passage drawn twice), in the order of the table
  above, with a review zip of each junction.

Review comments and their outcomes are in `docs/lvs-phase5-log.md`.

### Difficulties (where the user's eye is needed)

1. Whether the drawing is true to the cave: only the sketch, splays
   and data are available to the converter and to Claude.
2. Passage names: SexyTopo exports text as strokes, read by eye from
   the rendered sketch; guessed names are listed for confirmation.
3. Joins to neighbouring surveys (CrossRoads, CrystalPitch, NorthRift,
   then the 2026 surveys themselves): walls meeting without overlaps,
   outlines not crossing, and passages not drawn twice where a new
   survey revisits drawn passage.
4. Label placement on the 45° sheet, judged at screen resolution.
5. The low side of `line floor-step` and `line pit` (`Style.md` leaves
   it to a test render; existing drawings use `line pit` both ways).
6. xTherion is only checked headless for errors; the user views the
   zip locally.
7. The leftover `-outline none` wall from `smooth` (lint rule
   `wall-outline-none`): fix by hand, or allow it; decided after the
   pilot.
8. The sheet's `map-comment` length (1004 m) against Therion's
   1682.2 m: the user's decision.
9. Therion 6.2.0 here against 6.4.0 in CI: CI is the reference (the
   first CI build on 6.4.0 was clean).

## Unit tests (`tests/`, pytest, run in CI)

- **svn2git:** `git-svn-id` line becomes the two trailers with the body
  kept; an unmapped author fails listing the missing usernames; the path
  filter accepts `LongwoodValleySink/a.th`, `Symbols/Lines/l_u_rail.th`
  and `common_layout.th`, and rejects `LongwoodValleySinkOld/`,
  `Long_Vall_Sink/`, `Other/Symbols/` and `common_layout.th.bak`;
  build outputs are ignored and no tracked file is; `verify` reports
  equal and differing trees.
- **svnhttp:** a `PROPFIND` response gives paths (URL-decoded), folder
  or file, size and SVN properties; a `log-report` gives revision,
  author, date, message, changed paths and copy sources, and copes with
  a revision that has no author or message.
- **deps:** follows `input`, `source` and `\loadpicture` relative to the
  file that contains them (`../common_layout.th` then
  `Symbols/Symbols.th` resolves to the root `Symbols/`); a missing
  target fails naming the file and line; commented-out lines are
  ignored; a loop of inputs terminates.
- **inventory:** date parsing (`date 2026.03.14`, ranges, several dates,
  commented-out dates, nested surveys); year filter with a fixed "today"
  (excludes 2025.12.31, includes 2026.01.01, a range 2025.12.30 -
  2026.01.02 counts); empty SexyTopo scrap versus drawn scrap;
  commented-out `input` reported, not listed for drawing; scrap in no
  map; `input` whose case differs from the file.
- **Plan_only.thcfg:** has exactly one `export`, which is `map -proj
  plan -layout plan`; selects no elevation map; contains no
  `\loadpicture`; has a `map-comment` containing the data licence;
  every file it reaches (`deps`) exists in the git tree;
  its `plan` layout equals the one in `thconfig` apart from the listed
  changes (a test that will be relaxed as they diverge); the existing
  `thconfig` is byte-identical to the SVN version.
- **thconfig naming:** a new thconfig added under a cave folder is named
  `*.thcfg`; the historic names are allowed as they are.
- **licence:** `Style.md` and `Plan_only.thcfg` give the same data
  licence text.
- **project.toml:** the LongwoodValleySink config loads; a missing key
  fails naming the key; every file it names exists.
- **sketch2therion:** a Swildons fixture `.xvi` gives byte-identical
  output before and after the config refactor; SexyTopo `.xvi` reader
  gets stations and colour classes; walls have the passage on their left
  (signed area); closed lines end on their first point; no invisible
  walls; climb labels have no units.
- **th2lint:** a failing and a passing tiny `.th2` per rule (closed line
  not ending on its first point, smoothed `rock-border`, `ceiling-step`,
  unexplained `-clip off`, undated draught, bad label `-scale`, `area
  water` with no matching border `-id`); a finding in the baseline does
  not fail; a new one does; a fixed one reports the stale baseline entry.
- **Style.md and th2lint stay in step:** every `[lint]` rule in
  `tools/Style.md` has a matching `th2lint` check, and the reverse.
- **make_index:** statistics parsed from a sample `therion.log`; a
  missing PDF is skipped without failing.
- **sync.py** (SVN stays master; against a local `svnadmin` repository): a second run with no new SVN
  revisions brings nothing across; a new revision arrives with its
  trailers.

## Delivery

Commits pushed to `claude/serene-cerf-h45zcu`; changed files also
supplied as numbered zips (`CheddarCatchment-1.zip`, `-2`, …) with their
relative paths.

## Incremental sync

If SVN stays the master copy (decided at the Phase 1 check point), add
`tools/svn2git/sync.py`: fetch new revisions into the raw `git svn`
mirror (Phase 3 step 11), apply the same trailer rewrite to the new
commits only, and bring them onto the git branch. If git becomes the
master, SVN is frozen and no sync is needed.

### Drawings back to SVN (decided 2026-10-07: option C)

Drawings are made and checked in git (CI, `th2lint`, `review`), then
handed over (as the numbered zips in "Delivery") and committed to SVN
by hand in the usual way, keeping their real authors. The next
`sync.py` finds that revision's changes already in git and records it
as an empty commit with its `SVN-Revision:` / `SVN-URL:` trailers and
a note saying so, so `verify` still counts every revision. A file
changed differently in SVN and git stops the sync for a person. The
alternatives considered were writing back automatically
(`git svn dcommit`, needs SVN credentials here), making git the master
for LongwoodValleySink, and splitting by file type; option B (git as
master) remains the simplest if the SVN users agree to it later.
