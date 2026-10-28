"""Rewrite a `git svn` clone for the git copy.

Each `git-svn-id: <url>@<rev> <uuid>` line becomes the trailers
`SVN-Revision: r<rev>` and `SVN-URL: <url>`, and the executable bit is
dropped (SVN had `svn:executable` on data files). `git svn` makes a
commit for every SVN revision, empty when it touches none of the
included paths; those are dropped, as are revisions that only change
SVN properties (`verify` accounts for them). Run on a copy of the
mirror, never the mirror itself: `git svn fetch` needs the git-svn-id
lines (see docs/PLAN-LongwoodValleySink.md, Phase 3).

    python3 -m tools.svn2git.rewrite REPO
"""

import os
import re
import sys

GIT_SVN_ID = re.compile(rb"^git-svn-id: (\S+)@(\d+) \S+[ \t]*\n?", re.M)


def svn_id(message):
    """(url, revision) from a git svn commit message, or None."""
    m = GIT_SVN_ID.search(message)
    return (m.group(1).decode(), int(m.group(2))) if m else None


def trailers(url, revision):
    return f"SVN-Revision: r{revision}\nSVN-URL: {url}\n".encode()


def rewrite_message(message):
    """The message with its git-svn-id line turned into trailers."""
    found = svn_id(message)
    if not found:
        return message
    body = GIT_SVN_ID.sub(b"", message).rstrip()
    lines = trailers(*found)
    return body + b"\n\n" + lines if body else lines


def svn_revision(message):
    """The revision from an `SVN-Revision: rN` trailer, or None."""
    m = re.search(rb"^SVN-Revision: r(\d+)$", message, re.M)
    return int(m.group(1)) if m else None


def drop_executable(commit, metadata=None):
    for change in commit.file_changes:
        if change.mode == b"100755":
            change.mode = b"100644"


def filter_repo(path):
    """Rewrite the repository at `path` in place with git filter-repo."""
    import git_filter_repo as fr

    args = fr.FilteringOptions.parse_args(["--force", "--quiet", "--prune-empty", "always"])
    cwd = os.getcwd()
    os.chdir(path)
    try:
        fr.RepoFilter(
            args,
            message_callback=lambda m: rewrite_message(m),
            commit_callback=drop_executable,
        ).run()
    finally:
        os.chdir(cwd)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    filter_repo(sys.argv[1])
