---
name: therion-drawing
description: Conventions for drawing or editing Therion scraps (.th2) in the Cheddar Catchment survey, and the checks to run afterwards. Use when converting sketches, editing walls, water, labels or other symbols, or reviewing a drawing.
---

# Drawing Therion scraps

The conventions live in one place, `tools/sketch2therion/Style.md`: read it before
drawing or editing a `.th2`, and add to it (in the same commit) what
the work teaches. Do not copy its rules here.

- Workflow (SexyTopo to a finished plan, and `review`): `tools/README.md`.
- Cave settings (names, scale, licence): `tools/project.toml`.
- Checks: `python3 -m tools.sketch2therion.th2lint --from LongwoodValleySink/Plan_only.thcfg`,
  the build log checks in `tools/sketch2therion/Style.md` ("Checking"), and
  `python3 -m tools.sketch2therion review check FILE.th2`.
- Scope and decisions: `docs/PLAN-LongwoodValleySink.md`.
