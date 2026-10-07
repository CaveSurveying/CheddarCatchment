"""Check the git copy against SVN.

1. Revisions: every SVN revision touching the included paths has one
   git commit (found by its `SVN-Revision:` trailer), with the mapped
   author and the same date, and git has no others. A revision that
   only changes SVN properties or adds empty folders has no git commit
   (git records neither); those are listed, not failed.
2. Files: the tree at REF equals `svn export` of the included paths at
   HEAD, apart from the files that exist only in git (`GIT_ONLY`).
3. No migrated file has the executable bit (SVN set it on data files).

    python3 -m tools.svn2git.verify REPO [--ref REF]
"""

import argparse
import filecmp
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone

from tools.svn2git import authors as authors_mod
from tools.svn2git import paths
from tools.svn2git.rewrite import svn_revision

REPO_URL = "https://www.cave-registry.org.uk/svn/CheddarCatchment"

# Files added in git that SVN does not have.
GIT_ONLY = {
    ".gitattributes",
    ".gitignore",
    "LongwoodValleySink/Outputs/.gitkeep",
    "LongwoodValleySink/Plan_only.thcfg",
}


@dataclass
class Changed:
    action: str         # A, M, D or R
    path: str           # relative to the repository root
    kind: str           # file or dir
    text_mods: bool
    copyfrom: str = ""


@dataclass
class SvnRev:
    revision: int
    author: str
    date: str           # ISO 8601, UTC
    changed: list = field(default_factory=list)


@dataclass
class GitRev:
    revision: int
    name: str
    email: str
    date: str           # ISO 8601 with offset


def parse_svn_log(xml_text):
    """{revision: SvnRev} from `svn log -v --xml`."""
    revs = {}
    for entry in ET.fromstring(xml_text).iter("logentry"):
        rev = int(entry.get("revision"))
        changed = [
            Changed(
                action=p.get("action"),
                path=(p.text or "").lstrip("/"),
                kind=p.get("kind", ""),
                text_mods=p.get("text-mods") == "true",
                copyfrom=(p.get("copyfrom-path") or "").lstrip("/"),
            )
            for p in entry.iter("path")
        ]
        revs[rev] = SvnRev(rev, entry.findtext("author") or "", entry.findtext("date") or "", changed)
    return revs


def needs_commit(rev):
    """True if git records something for this SVN revision."""
    for c in rev.changed:
        if not paths.included(c.path):
            continue
        if c.kind == "dir":
            if c.copyfrom or c.action in ("D", "R"):
                return True
        elif c.action != "M" or c.text_mods:
            return True
    return False


def parse_git_log(text):
    """{revision: GitRev} from `git log --format=%an%x00%ae%x00%aI%x00%B%x01`."""
    revs = {}
    for record in text.split("\x01"):
        record = record.lstrip("\n")
        if not record:
            continue
        name, email, date, message = record.split("\x00", 3)
        rev = svn_revision(message.encode())
        if rev is not None:
            revs[rev] = GitRev(rev, name, email, date)
    return revs


def _instant(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc).replace(microsecond=0)


def compare_revisions(svn, git, authors):
    """(problems, skipped): lists of strings and of property/folder-only revisions."""
    problems, skipped = [], []
    for rev in sorted(svn):
        s = svn[rev]
        if rev not in git:
            if needs_commit(s):
                problems.append(f"r{rev}: no git commit")
            else:
                skipped.append(rev)
            continue
        g = git[rev]
        want = authors.get(s.author or "(no author)")
        if want is None:
            problems.append(f"r{rev}: SVN author {s.author!r} not in authors.txt")
        elif (g.name, g.email) != want:
            problems.append(f"r{rev}: author {g.name} <{g.email}>, expected {want[0]} <{want[1]}>")
        if _instant(g.date) != _instant(s.date):
            problems.append(f"r{rev}: date {g.date}, SVN {s.date}")
    for rev in sorted(set(git) - set(svn)):
        problems.append(f"r{rev}: git commit for a revision that touches no included path")
    return problems, skipped


def list_files(root):
    found = set()
    for folder, _, files in os.walk(root):
        for name in files:
            found.add(os.path.relpath(os.path.join(folder, name), root).replace(os.sep, "/"))
    return found


def compare_trees(svn_dir, git_dir, git_only=frozenset()):
    """Problems comparing two exported trees, as strings."""
    a, b = list_files(svn_dir), list_files(git_dir)
    problems = [f"only in SVN: {p}" for p in sorted(a - b)]
    problems += [f"only in git: {p}" for p in sorted(b - a - set(git_only))]
    for p in sorted(a & b):
        if not filecmp.cmp(os.path.join(svn_dir, p), os.path.join(git_dir, p), shallow=False):
            problems.append(f"differs: {p}")
    return problems


def executable_files(ls_tree):
    """Migrated paths with mode 100755 in `git ls-tree -r` output."""
    found = [line.split("\t", 1)[1] for line in ls_tree.splitlines() if line.startswith("100755 ")]
    return [p for p in found if paths.included(p)]


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout


def svn_log(repo_url=REPO_URL):
    revs = {}
    targets = [f"{repo_url}/{p}" for p in paths.HEAD_PATHS]
    targets += [f"{repo_url}/{p}@{r}" for p, r in paths.EXTRA_HISTORY.items()]
    for target in targets:
        revs.update(parse_svn_log(run("svn", "log", "-v", "--xml", "--non-interactive", target)))
    return revs


def export_svn(dest, repo_url=REPO_URL):
    for p in paths.HEAD_PATHS:
        os.makedirs(os.path.dirname(os.path.join(dest, p)), exist_ok=True)
        run("svn", "export", "-q", "--force", "--non-interactive", f"{repo_url}/{p}", os.path.join(dest, p))


def export_git(repo, ref, dest):
    os.makedirs(dest)
    archive = subprocess.run(["git", "-C", repo, "archive", ref], check=True, capture_output=True).stdout
    subprocess.run(["tar", "-x", "-C", dest], input=archive, check=True)
    # Compare only what SVN has: drop the git tree's other top-level entries.
    for name in os.listdir(dest):
        if not paths.included(name) and name not in GIT_ONLY:
            subprocess.run(["rm", "-rf", os.path.join(dest, name)], check=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--svn", default=REPO_URL)
    args = ap.parse_args(argv)

    svn = svn_log(args.svn)
    git = parse_git_log(run("git", "-C", args.repo, "log", "--format=%an%x00%ae%x00%aI%x00%B%x01", args.ref))
    problems, skipped = compare_revisions(svn, git, authors_mod.load())

    with tempfile.TemporaryDirectory() as tmp:
        export_svn(os.path.join(tmp, "svn"), args.svn)
        export_git(args.repo, args.ref, os.path.join(tmp, "git"))
        problems += compare_trees(os.path.join(tmp, "svn"), os.path.join(tmp, "git"), GIT_ONLY)

    problems += [f"executable: {p}" for p in executable_files(run("git", "-C", args.repo, "ls-tree", "-r", args.ref))]

    print(f"SVN revisions touching the included paths: {len(svn)}")
    print(f"git commits with an SVN-Revision trailer: {len(git)}")
    if skipped:
        print("no git commit (properties or empty folders only): " + ", ".join(f"r{r}" for r in skipped))
    for p in problems:
        print("PROBLEM " + p)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
