"""sync against a local SVN repository made with svnadmin (no network)."""

import os
import shutil
import subprocess
import tempfile
import unittest

from tools.svn2git import paths, rewrite, sync

TOOLS = all(shutil.which(t) for t in ("svn", "svnadmin", "git"))


def run(*args, cwd=None, env=None):
    return subprocess.run(args, cwd=cwd, env=env, check=True, capture_output=True, text=True).stdout


def git_svn_available():
    return TOOLS and subprocess.run(["git", "svn", "--version"], capture_output=True).returncode == 0


@unittest.skipUnless(git_svn_available(), "needs svn, svnadmin and git svn")
class SyncTest(unittest.TestCase):
    def setUp(self):
        try:
            import git_filter_repo  # noqa: F401
        except ImportError:
            self.skipTest("needs git-filter-repo")
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.env = dict(os.environ, GIT_COMMITTER_NAME="T", GIT_COMMITTER_EMAIL="t@x", HOME=self.tmp)
        svnrepo = os.path.join(self.tmp, "svnrepo")
        run("svnadmin", "create", svnrepo)
        self.url = "file://" + svnrepo
        self.wc = os.path.join(self.tmp, "wc")
        run("svn", "checkout", "-q", self.url, self.wc)
        authors = os.path.join(self.tmp, "authors.txt")
        with open(authors, "w") as f:
            f.write("andrew = Andrew Atkinson <andrew@x.invalid>\n")

        self.write("LongwoodValleySink/a.th", "one\n")
        self.write("Other/b.th", "b\n")
        run("svn", "add", "-q", "LongwoodValleySink", "Other", cwd=self.wc)
        run("svn", "propset", "-q", "svn:executable", "*", "LongwoodValleySink/a.th", cwd=self.wc)
        self.commit("r1")

        self.mirror = os.path.join(self.tmp, "mirror")
        run("git", "svn", "clone", "-q", self.url, self.mirror, f"--include-paths={paths.INCLUDE}",
            f"--authors-file={authors}", env=self.env)
        self.repo = os.path.join(self.tmp, "repo")
        run("git", "clone", "-q", "--no-local", "-b", "master", self.mirror, self.repo)
        rewrite.filter_repo(self.repo)

    def write(self, path, text):
        full = os.path.join(self.wc, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text)

    def commit(self, message):
        run("svn", "commit", "-q", "--username", "andrew", "-m", message, cwd=self.wc)

    def sync(self):
        old = os.environ.copy()
        os.environ.update(self.env)
        try:
            return sync.sync(self.repo, self.mirror)
        finally:
            os.environ.clear()
            os.environ.update(old)

    def log(self, fmt="%s"):
        return run("git", "-C", self.repo, "log", f"--format={fmt}").splitlines()

    def test_nothing_new(self):
        before = self.log("%H")
        self.assertEqual(self.sync(), [])
        self.assertEqual(self.log("%H"), before)

    def test_new_revision_arrives_with_trailers(self):
        self.write("LongwoodValleySink/a.th", "two\n")
        self.write("LongwoodValleySink/c.th", "c\n")
        run("svn", "add", "-q", "LongwoodValleySink/c.th", cwd=self.wc)
        run("svn", "propset", "-q", "svn:executable", "*", "LongwoodValleySink/c.th", cwd=self.wc)
        self.write("Other/b.th", "b2\n")
        self.commit("Second survey")
        self.write("Other/b.th", "b3\n")
        self.commit("Other cave only")

        self.assertEqual(self.sync(), [2])
        msg = run("git", "-C", self.repo, "log", "-1", "--format=%an <%ae>%n%B")
        self.assertTrue(msg.startswith("Andrew Atkinson <andrew@x.invalid>\nSecond survey\n\nSVN-Revision: r2\n"), msg)
        self.assertIn(f"SVN-URL: {self.url}\n", msg)
        self.assertNotIn("git-svn-id", msg)
        tree = run("git", "-C", self.repo, "ls-tree", "-r", "HEAD")
        self.assertNotIn("Other/", tree)
        self.assertNotIn("100755", tree)
        self.assertEqual(run("git", "-C", self.repo, "show", "HEAD:LongwoodValleySink/a.th"), "two\n")
        self.assertEqual(run("git", "-C", self.repo, "status", "--porcelain"), "")
        # And a second run brings nothing more.
        self.assertEqual(self.sync(), [])

    def test_keeps_git_only_work(self):
        with open(os.path.join(self.repo, "Plan_only.thcfg"), "w") as f:
            f.write("x\n")
        run("git", "-C", self.repo, "add", "Plan_only.thcfg")
        run("git", "-C", self.repo, "commit", "-q", "-m", "git only",
            env=dict(self.env, GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@x"))
        self.write("LongwoodValleySink/a.th", "three\n")
        self.commit("Third")
        self.assertEqual(self.sync(), [2])
        self.assertIn("Plan_only.thcfg", run("git", "-C", self.repo, "ls-files"))


if __name__ == "__main__":
    unittest.main()
