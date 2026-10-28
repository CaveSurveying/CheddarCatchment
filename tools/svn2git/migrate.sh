#!/bin/sh
# Make the git copy of LongwoodValleySink from SVN (Phase 3 of
# docs/PLAN-LongwoodValleySink.md).
#
#   tools/svn2git/migrate.sh [MIRROR] [OUT]
#
# MIRROR (default ../CheddarCatchment-svn-mirror) is the raw `git svn`
# clone, kept because SVN stays the master copy and sync.py fetches into
# it; it is created on the first run and fetched on later ones. OUT
# (default ../CheddarCatchment-svn-filtered) is made afresh from it with
# SVN-Revision/SVN-URL trailers and no executable bits, then checked
# with verify.py. Join it to the working branch with
#   git fetch OUT master && git merge --allow-unrelated-histories FETCH_HEAD
set -eu

REPO_URL=https://www.cave-registry.org.uk/svn/CheddarCatchment
HERE=$(cd "$(dirname "$0")/../.." && pwd)
MIRROR=${1:-$HERE/../CheddarCatchment-svn-mirror}
OUT=${2:-$HERE/../CheddarCatchment-svn-filtered}
INCLUDE=$(cd "$HERE" && python3 -m tools.svn2git.paths)

if [ -d "$MIRROR/.git" ]; then
    git -C "$MIRROR" svn fetch
else
    git svn clone "$REPO_URL" "$MIRROR" \
        --include-paths="$INCLUDE" \
        --authors-file="$HERE/tools/svn2git/authors.txt"
fi
git -C "$MIRROR" update-ref refs/heads/master refs/remotes/git-svn

rm -rf "$OUT"
git clone --quiet --no-local --branch master "$MIRROR" "$OUT"
(cd "$HERE" && python3 -m tools.svn2git.rewrite "$OUT")
(cd "$HERE" && python3 -m tools.svn2git.verify "$OUT")
