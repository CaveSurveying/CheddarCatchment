"""Which SVN paths the git copy contains.

`INCLUDE` is passed to `git svn --include-paths`; `included()` applies
the same test in Python (for `verify` and the tests). `HEAD_PATHS` are
the included paths that exist at HEAD, and `EXTRA_HISTORY` the deleted
ones kept for their history (the root `Symbols.th`, copied to
`Symbols/Symbols.th` at r416), with the revision to read them at.

    python3 -m tools.svn2git.paths      # prints INCLUDE
"""

import re

INCLUDE = r"^(LongwoodValleySink(/|$)|Symbols(/|$)|Symbols\.th$|common_layout\.th$)"
HEAD_PATHS = ["LongwoodValleySink", "Symbols", "common_layout.th"]
EXTRA_HISTORY = {"Symbols.th": 415}

_INCLUDE = re.compile(INCLUDE)


def included(path):
    """True if `path` (relative to the repository root) is migrated."""
    return bool(_INCLUDE.search(path.lstrip("/")))


if __name__ == "__main__":
    print(INCLUDE)
