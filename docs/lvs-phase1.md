# LongwoodValleySink: Phase 1 findings and check point

Phase 1 of `docs/PLAN-LongwoodValleySink.md` (read-only inventory),
done 2026-10-06 against SVN revision 501 (HEAD). The survey table is in
`docs/lvs-inventory.md`.

## How it was done

The environment's network policy blocks the Ubuntu archive and PyPI, so
`svn`, `git-svn`, `git-filter-repo` and `pytest` could not be installed
(Phase 0 step 2). The SVN server itself is reachable, so the inventory
reads it over plain HTTP (WebDAV) with `tools/svn2git/svnhttp.py`:
`PROPFIND` for listings, sizes and SVN properties, `REPORT log-report`
for history with changed paths and copy sources, `GET` for files. The
tests use `unittest`, so they run without `pytest` and `pytest` will
still collect them.

Phase 3 (the migration) does need `git-svn` and `git-filter-repo`. To
make them available, add to the environment's setup script:

    apt-get install -y subversion git-svn
    pip install git-filter-repo shapely pytest

and allow `archive.ubuntu.com`, `security.ubuntu.com` and `pypi.org` /
`files.pythonhosted.org` in the environment's network access.

## History (step 3)

| Path | Revisions | First | Last | Authors |
|---|---|---|---|---|
| `LongwoodValleySink/` | 47 | r270, 2013-11-19 | r501, 2026-09-13 | andrew 32, JohnCooper 13, graham 2 |
| `common_layout.th` | 7 | r1, 2011-12-13 | r475, 2025-02-19 | andrew |
| `Symbols/` | 6 | r415, 2019-11-12 | r483, 2025-02-21 | andrew |

- 56 distinct revisions touch the three paths: the expected commit
  count for `verify.py`.
- **No path returned 403**: nothing is access-restricted.
- Twelve of the revisions also change other caves (e.g. r430 touches 20
  folders). Their messages will mention caves that are not in the git
  copy; that is expected.
- **Properties:** `svn:global-ignores` on `LongwoodValleySink/`
  (`Triasic`, `Triasic2`): left out of git (decided at Phase 3; the
  folders were renamed to `Triassic`, `Triassic2`, so nothing matches);
  `svn:mime-type application/octet-stream` on the three PocketTopo
  `.top` files (binary, mark `-diff` in `.gitattributes`);
  `svn:executable` on 224 of the 348 files (data files, not scripts):
  recommend dropping the executable bit in git. No `svn:externals`,
  `svn:ignore` or `svn:eol-style`.

## Copy history (step 4)

- `LongwoodValleySink/` has **no copy sources**: it was created at r270
  and its history is complete from there. `Long_Vall_Sink/` (r1 only,
  2011) and `Longwood/` are separate and not needed.
- `Symbols/Symbols.th` was copied at r416 from the root `/Symbols.th@415`.
  To keep its earlier history, add `^Symbols\.th$` to the include
  filter (one more root file, deleted at r416, so absent from HEAD).

## Dependency walk (step 5)

`python3 -m tools.svn2git.deps ROOT LongwoodValleySink/thconfig --within LongwoodValleySink`
(the existing thconfig: `Plan_only.thcfg` will use the same sources):

- 123 files reached. Outside `LongwoodValleySink/`: `common_layout.th`
  and five files in `Symbols/` (`Symbols.th`, `Areas/a_blocks_BCA.th`,
  `Lines/l_u_rail.th`, `Lines/l_wall_debris_CHED.th`,
  `Special/s_northarrow_BCA.th`). Nothing else.
- One missing target: `LongwoodValleySink/thconfig:67:
  Outputs/LongwoodValleySinkE315.pdf` (the elevation inset, as
  expected; `Plan_only.thcfg` drops it).
- No `input` whose letter case differs from the file.

## Size (step 6)

17.5 MB at HEAD for all three paths. The largest files are SexyTopo
`.plan.json` (up to 1.1 MB); JSON is 13.8 MB of the total, `.xvi`
3.1 MB. All are text. **Git LFS is not needed.**

## Surveys (step 7)

See `docs/lvs-inventory.md`. Summary:

- **2026 surveys with undrawn plans (10)**, all added in r501 from
  SexyTopo, each with SexyTopo's empty plan scrap and its plan `.xvi`
  sketch present: GoSouth (2026-04-25), Trident (06-13), IDontCare
  (07-11), TridentCentre (07-11), TridentLeft (07-11), BoldStep (07-25),
  TritonNorth (07-25), Connection (08-01), TritonSouth (08-01),
  FairyChimneys (08-08). About 700 m of legs in all.
- They are already `input` in `LongwoodValleySink.th` but none is in
  `Maps.th` or any plan map yet.
- **Reported, not for drawing:** GoWest and TickleRift (drawn, not input
  in `LongwoodValleySink.th`, in no plan map: deliberate);
  `WestPassage/WestPassageCalib.th` (a calibration file).
- **Outside this year:** TickleCheck (2024-11-04) also has an empty plan
  scrap.

## House style (step 8)

| Item | LongwoodValleySink |
|---|---|
| Plan file | `X/X.plan.th2` (older ones); SexyTopo export is `X/XP.th2` |
| Plan scrap ids | `XSP1`, `XSP2`, …; SexyTopo export is `XP1` |
| Elevation | `X/XE315.th2`, scraps `XSE315_1`; also E000, E090 |
| Survey plan map | `map XMP` in `X.th` listing its plan scraps |
| Cave plan map | `LongwoodValleySinkMP` in `Maps.th` lists `XMP@X` (or grouped maps such as `CyclopsMP`) |
| Sketches | `X/Notes/*.xvi` (TickleWest uses `X/XVI/`) |
| Scale | 1:500, base-scale 1:350; plan rotated 45°; elevation projected 315° |
| Label sizes in `.th2` | `-scale m` 17, `s` 8, `l` 2, `xs` 2, `xl` 1: all five Therion sizes are in use |
| Symbols in use (plans) | wall, pit, rock-border with rock-edge, border, overhang, floor-step, flowstone; areas blocks, sand, water, debris |
| Copyright in data | Mixed: `"CC BY SA NC"` in 8 surveys, `"GNU GPL"` in 2, and the 2026 SexyTopo surveys `copyright 2026 "Andrew Atkinson (WCC)" # "GPLv3.0+"` in 4. To align with CC BY-NC-SA. |

Per-survey thconfigs are named `X.thconfig` (SexyTopo writes them). The
new plan-only file is `Plan_only.thcfg`, as agreed.

## Check point: decisions needed (step 9)

1. **Surveys to draw:** the ten 2026 surveys above? Also TickleCheck?
2. **Authors:** names and emails for the SVN users `andrew`,
   `JohnCooper` and `graham`.
3. **Licence version:** CC BY-NC-SA 4.0? (The sheets give no version.)
4. **SVN as master:** does SVN stay the master copy (then `sync.sh` and
   a raw `git svn` mirror), or is it frozen once git is set up?
5. **Root `Symbols.th`:** include it for the earlier history of
   `Symbols/Symbols.th` (recommended)?
6. **Executable bit:** drop it from data files in git (recommended)?
7. **Git LFS:** not needed (recommended).
8. **Toolchain:** add the packages and hosts above to the environment,
   so Phase 3 can run.
9. **New plan scraps:** when drawn, rename to house style
   (`X.plan.th2`, `XSP1`, a `map XMP`, added to `LongwoodValleySinkMP`),
   or keep SexyTopo's `XP.th2` / `XP1`?

## Check point answers (2026-10-06)

1. **Surveys to draw:** the ten 2026 surveys. Not TickleCheck (2024).
2. **Authors:** agreed; names and emails still to be supplied for
   `andrew`, `JohnCooper` and `graham` (`tools/svn2git/authors.txt`).
3. **Licence:** CC BY-NC-SA **4.0** for survey data and drawings;
   GPLv3 for the tools.
4. **SVN is the master copy for now:** keep a raw `git svn` mirror and
   add `tools/svn2git/sync.py` (plan, "Incremental sync").
5. **New plan scraps use the house style** (`X.plan.th2`, `XSP1`,
   `map XMP` added to `LongwoodValleySinkMP`). SexyTopo has been changed
   to export in the house style; the r501 files were exported before
   that, so they are renamed when drawn.
6. Recommendations taken: include the root `Symbols.th`; drop the
   executable bit from data files; no Git LFS.
