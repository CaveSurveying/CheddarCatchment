"""The .gitignore and .gitattributes rules."""

import os
import shutil
import subprocess
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*args, check=True):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True, check=check)


@unittest.skipUnless(shutil.which("git") and os.path.isdir(os.path.join(REPO, ".git")), "needs a git checkout")
class GitFilesTest(unittest.TestCase):
    def ignored(self, path):
        return git("check-ignore", "--no-index", "-q", path, check=False).returncode == 0

    def test_build_outputs_ignored(self):
        for p in ["LongwoodValleySink/Outputs/LongwoodValleySinkP.pdf", "LongwoodValleySink/GoWest/Outputs/a.pdf",
                  "output/index.html", "proj/a.tif", "LongwoodValleySink/therion.log",
                  "LongwoodValleySink/a.3d", "LongwoodValleySink/a.lox", "tools/__pycache__/x.pyc"]:
            self.assertTrue(self.ignored(p), p)

    def test_survey_data_not_ignored(self):
        for p in ["LongwoodValleySink/Outputs/.gitkeep", "LongwoodValleySink/Plan_only.thcfg",
                  "LongwoodValleySink/Triassic/Triassic.th", "LongwoodValleySink/Triasic/x.th",
                  "LongwoodValleySink/GoSouth/GoSouth.plan.json", "Symbols/Symbols.th"]:
            self.assertFalse(self.ignored(p), p)

    def test_no_tracked_file_is_ignored(self):
        self.assertEqual(git("ls-files", "-ci", "--exclude-standard").stdout, "")

    def test_outputs_folder_kept(self):
        self.assertTrue(os.path.exists(os.path.join(REPO, "LongwoodValleySink", "Outputs", ".gitkeep")))

    def test_pockettopo_is_binary(self):
        out = git("check-attr", "diff", "merge", "text", "--", "LongwoodValleySink/Triassic/PocketTopo/Triasic.top").stdout
        self.assertIn("diff: unset", out)
        self.assertIn("merge: unset", out)
        self.assertIn("text: unset", out)


if __name__ == "__main__":
    unittest.main()
