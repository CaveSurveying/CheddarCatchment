"""Read `authors.txt` (SVN username = Name <email>) and find gaps.

    python3 -m tools.svn2git.authors [USERNAME ...]   # fails on unmapped names
"""

import os
import re
import sys

AUTHORS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "authors.txt")
LINE = re.compile(r"^(.+?)\s*=\s*(.+?)\s*<([^<>]*)>\s*$")


def parse(text):
    """{username: (name, email)}; # comments and blank lines skipped."""
    authors = {}
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = LINE.match(line.strip())
        if not m:
            raise ValueError(f"authors.txt:{number}: not 'user = Name <email>': {line!r}")
        authors[m.group(1)] = (m.group(2), m.group(3))
    return authors


def load(path=AUTHORS):
    with open(path, encoding="utf-8") as f:
        return parse(f.read())


def missing(authors, usernames):
    """Usernames with no mapping, sorted. An empty SVN author is '(no author)'."""
    return sorted({u or "(no author)" for u in usernames} - set(authors))


def main(argv=None):
    names = sys.argv[1:] if argv is None else argv
    gaps = missing(load(), names)
    if gaps:
        print("not in authors.txt: " + ", ".join(gaps), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
