# Upstream converter output

Written by the unmodified Swildons `tools/sketch2therion` (commit
198bf46 of <https://github.com/paperclipmonkey/caves-mendip-swildons>)
from LongwoodValleySink sketches, with no station layout (so not fitted
to the survey), before it was ported. `tests/test_sketch2therion.py`
checks the port gives the same output, apart from the licence line,
the backdrop image path (relative to where the file is written) and
line endings (upstream writes CRLF). The commands, run from the top of
the Swildons repository with `L` the LongwoodValleySink folder:

    python3 -m tools.sketch2therion plan $L/GoSouth/Notes/GoSouthP.xvi --floor $L/GoSouth/Notes/GoSouthE.xvi \
      -o GoSouth-plan.th2 --survey GoSouth --name GoSouthS \
      --author 2026.04.25 "Andrew Atkinson" --copyright 2026 "CC BY-NC-SA 4.0"
    python3 -m tools.sketch2therion plan $L/Trident/Notes/TridentP.xvi -o Trident-plan.th2 --survey Trident \
      --name TridentS --author 2026.06.13 "Andrew Atkinson" --copyright 2026 "CC BY-NC-SA 4.0"
    python3 -m tools.sketch2therion extended $L/GoSouth/Notes/GoSouthE.xvi -o GoSouth-ext.th2 \
      --survey GoSouth --name GoSouthS

The drawings are LongwoodValleySink survey data: CC BY-NC-SA 4.0.
