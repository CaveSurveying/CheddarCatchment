import os
import shutil
import subprocess
import tempfile
import unittest

from tools.svn2git import rewrite

URL = "https://www.cave-registry.org.uk/svn/CheddarCatchment"
ID = f"git-svn-id: {URL}@270 7b6a2b4e-1c2d-4e5f-8a9b-0c1d2e3f4a5b\n".encode()


class RewriteMessageTest(unittest.TestCase):
    def test_id_becomes_trailers(self):
        got = rewrite.rewrite_message(b"Added Entrance\n\nSecond paragraph\n\n" + ID)
        self.assertEqual(got, b"Added Entrance\n\nSecond paragraph\n\n"
                              b"SVN-Revision: r270\nSVN-URL: " + URL.encode() + b"\n")

    def test_message_without_id_unchanged(self):
        self.assertEqual(rewrite.rewrite_message(b"Plain\n"), b"Plain\n")

    def test_empty_svn_message(self):
        self.assertEqual(rewrite.rewrite_message(b"\n" + ID), b"SVN-Revision: r270\nSVN-URL: " + URL.encode() + b"\n")

    def test_id_without_final_newline(self):
        self.assertEqual(rewrite.rewrite_message(b"Msg\n\n" + ID.rstrip()),
                         b"Msg\n\nSVN-Revision: r270\nSVN-URL: " + URL.encode() + b"\n")

    def test_escaped_url_kept_as_is(self):
        msg = b"x\n\ngit-svn-id: https://h/svn/My%20Repo@5 uuid\n"
        self.assertIn(b"SVN-URL: https://h/svn/My%20Repo\n", rewrite.rewrite_message(msg))

    def test_svn_id_and_revision(self):
        self.assertEqual(rewrite.svn_id(b"m\n\n" + ID), (URL, 270))
        self.assertIsNone(rewrite.svn_id(b"m\n"))
        self.assertEqual(rewrite.svn_revision(rewrite.rewrite_message(b"m\n\n" + ID)), 270)
        self.assertIsNone(rewrite.svn_revision(b"m\n"))


def _git(repo, *args, **kw):
    return subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True, **kw).stdout


GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="A", GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_NAME="A",
               GIT_COMMITTER_EMAIL="a@x")


@unittest.skipUnless(shutil.which("git"), "needs git")
class FilterRepoTest(unittest.TestCase):
    def setUp(self):
        try:
            import git_filter_repo  # noqa: F401
        except ImportError:
            self.skipTest("needs git-filter-repo")
        self.repo = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.repo)
        _git(self.repo, "init", "-q", "-b", "master")
        path = os.path.join(self.repo, "a.th")
        with open(path, "w") as f:
            f.write("survey a\nendsurvey\n")
        os.chmod(path, 0o755)
        _git(self.repo, "add", "a.th")
        self._commit(b"Added a\n\n" + ID)
        self._commit(b"\n" + ID.replace(b"@270", b"@271"), "--allow-empty")
        rewrite.filter_repo(self.repo)

    def _commit(self, message, *extra):
        subprocess.run(["git", "-C", self.repo, "commit", "-q", *extra, "-F", "-"], input=message,
                       env=GIT_ENV, check=True, capture_output=True)

    def test_message_rewritten(self):
        msg = _git(self.repo, "log", "-1", "--format=%B")
        self.assertIn(b"SVN-Revision: r270\nSVN-URL: ", msg)
        self.assertNotIn(b"git-svn-id", msg)

    def test_empty_commit_dropped(self):
        self.assertEqual(_git(self.repo, "rev-list", "--count", "HEAD").strip(), b"1")

    def test_executable_bit_dropped(self):
        self.assertTrue(_git(self.repo, "ls-tree", "HEAD", "a.th").startswith(b"100644 "))


if __name__ == "__main__":
    unittest.main()
