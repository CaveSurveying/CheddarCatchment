# Cheddar Catchment: Longwood Valley Sink

A git copy of Longwood Valley Sink from the Cheddar Catchment Therion
survey (SVN: <https://www.cave-registry.org.uk/svn/CheddarCatchment/>),
with tools for drawing new surveys from SexyTopo sketches and for
checking and building the plan.

| Path | What it is |
|---|---|
| `LongwoodValleySink/` | The survey, with its full SVN history. `Plan_only.thcfg` builds the plan. |
| `common_layout.th`, `Symbols/` | Shared layout and symbols, also from SVN. |
| `tools/` | Converting sketches, linting drawings, the build index, and the SVN sync ([`tools/README.md`](tools/README.md)). |
| `tests/` | Unit tests: `python3 -m pytest -q tests`. |
| `docs/` | The plan and the Phase 1 inventory. |

## Building

```bash
mkdir -p output
cd LongwoodValleySink && therion -l ../output/therion.log Plan_only.thcfg
```

The plan is written to `LongwoodValleySink/Outputs/LongwoodValleySinkP.pdf`.
CI (`.github/workflows/build.yml`) runs the tests, `th2lint` and the
same build with Therion 6.4.0, and attaches the sheet to the run.

## History

Every commit from SVN keeps its author, date and message, with
`SVN-Revision:` and `SVN-URL:` trailers. SVN is still the master copy:
see "SVN" in [`tools/README.md`](tools/README.md).

## Licences

- Survey data and drawings: CC BY-NC-SA 4.0
  (<https://creativecommons.org/licenses/by-nc-sa/4.0/>).
- Tools (`tools/`, `tests/`): GPLv3 ([`tools/LICENSE`](tools/LICENSE)).
  `tools/sketch2therion/` and `tools/web/` are adapted from the
  Swildons survey's tools
  (<https://github.com/paperclipmonkey/caves-mendip-swildons>).
