"""Bring new SVN revisions onto the current git branch (SVN is the master).

Fetches into the raw `git svn` mirror made by `migrate.sh`, then
applies each mirror commit newer than the branch's latest
`SVN-Revision:` trailer: same changes, author and date, the git-svn-id
line turned into trailers, no executable bits. Revisions that change
nothing git records are skipped, as in the first migration. Stops on a
conflict (a file changed in both SVN and git), leaving it for a person.

    python3 -m tools.svn2git.sync [--mirror MIRROR] [--no-fetch]
"""

import argparse
import os
import subprocess
import sys

from tools.svn2git.rewrite import rewrite_message, svn_id, svn_revision

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MIRROR = os.path.join(os.path.dirname(HERE), "CheddarCatchment-svn-mirror")
FETCHED = "refs/svn2git/mirror"


def git(repo, *args, env=None, input=None):
    return subprocess.run(
        ["git", "-C", repo, *args], check=True, capture_output=True, env=env, input=input
    ).stdout


def last_synced(repo):
    """The highest SVN revision already on HEAD, or 0."""
    log = git(repo, "log", "--format=%B%x01", "HEAD")
    revs = [svn_revision(m) for m in log.split(b"\x01")]
    return max((r for r in revs if r is not None), default=0)


def pending(repo, after):
    """[(sha, revision)] of fetched mirror commits newer than `after`, oldest first."""
    out = git(repo, "log", "--reverse", "--format=%H%x00%B%x01", FETCHED)
    found = []
    for record in out.split(b"\x01"):
        record = record.lstrip(b"\n")
        if not record:
            continue
        sha, message = record.split(b"\x00", 1)
        sid = svn_id(message)
        if sid and sid[1] > after:
            found.append((sha.decode(), sid[1]))
    return found


def apply(repo, sha):
    """Apply one mirror commit to HEAD. Returns False if it changes nothing."""
    try:
        git(repo, "cherry-pick", "--no-commit", "--allow-empty", sha)
    except subprocess.CalledProcessError as e:
        sys.exit(f"conflict applying {sha}; resolve by hand, then commit or `git cherry-pick --abort`\n"
                 + e.stderr.decode(errors="replace"))
    for line in git(repo, "diff", "--cached", "--raw", "--no-renames").decode().splitlines():
        meta, path = line.split("\t", 1)
        if meta.split()[1] == "100755":
            git(repo, "update-index", "--chmod=-x", "--", path)
            full = os.path.join(repo, path)
            os.chmod(full, os.stat(full).st_mode & 0o666)
    if not git(repo, "diff", "--cached", "--name-only"):
        _quit(repo)
        return False
    fmt = git(repo, "log", "-1", "--format=%an%x00%ae%x00%aI%x00%B", sha).decode()
    name, email, date, message = fmt.split("\x00", 3)
    env = dict(os.environ, GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=email, GIT_AUTHOR_DATE=date)
    git(repo, "commit", "--quiet", "--no-verify", "-F", "-", env=env,
        input=rewrite_message(message.encode()))
    _quit(repo)
    return True


def _quit(repo):
    """Forget the cherry-pick state, if git left any."""
    subprocess.run(["git", "-C", repo, "cherry-pick", "--quit"], capture_output=True)


def sync(repo, mirror, fetch=True):
    """Bring new revisions across; returns the revisions committed."""
    if not os.path.isdir(os.path.join(mirror, ".git")):
        sys.exit(f"no git svn mirror at {mirror}; make it with tools/svn2git/migrate.sh")
    if git(repo, "status", "--porcelain", "--untracked-files=no"):
        sys.exit("the working tree has uncommitted changes")
    if fetch:
        git(mirror, "svn", "fetch")
    git(repo, "fetch", "--quiet", "--no-tags", mirror, f"+refs/remotes/git-svn:{FETCHED}")
    done = []
    for sha, rev in pending(repo, last_synced(repo)):
        if apply(repo, sha):
            done.append(rev)
    return done


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=HERE)
    ap.add_argument("--mirror", default=MIRROR)
    ap.add_argument("--no-fetch", action="store_true", help="use what the mirror already has")
    args = ap.parse_args(argv)
    done = sync(args.repo, args.mirror, fetch=not args.no_fetch)
    print("brought across: " + (", ".join(f"r{r}" for r in done) if done else "nothing new"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
