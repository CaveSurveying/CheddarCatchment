# Notes for agents

- Read `docs/PLAN-LongwoodValleySink.md` first: the plan, its phases and
  the decisions taken. It is a trial: only
  `LongwoodValleySink/Plan_only.thcfg` is built; leave the other
  thconfigs and caves as they are.
- Drawing conventions: `tools/Style.md` (the single source; see also
  `.claude/skills/therion-drawing/SKILL.md`). Tools and workflow:
  `tools/README.md`.
- SVN is the master copy. Do not rewrite the migrated history; bring
  SVN changes in with `python3 -m tools.svn2git.sync`.
- Tests: `python3 -m pytest -q tests`; drawings:
  `python3 tools/th2lint.py --from LongwoodValleySink/Plan_only.thcfg`.
- British English. Survey data and drawings are CC BY-NC-SA 4.0; the
  tools are GPLv3.
