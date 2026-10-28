import re
import unittest

from tools.svn2git import paths


class IncludedTest(unittest.TestCase):
    def test_accepts(self):
        for p in ["LongwoodValleySink", "LongwoodValleySink/a.th", "/LongwoodValleySink/Triassic/b.th2",
                  "Symbols/Lines/l_u_rail.th", "Symbols", "Symbols.th", "common_layout.th"]:
            self.assertTrue(paths.included(p), p)

    def test_rejects(self):
        for p in ["LongwoodValleySinkOld/a.th", "Long_Vall_Sink/a.th", "Longwood/a.th",
                  "Other/Symbols/a.th", "Other/LongwoodValleySink/a.th", "common_layout.th.bak",
                  "Symbols.th.orig", "SymbolsOld/a.th", "LongwoodValley.thcfg"]:
            self.assertFalse(paths.included(p), p)

    def test_git_svn_gets_the_same_regex(self):
        # git svn uses Perl regexes; keep to syntax Python and Perl read alike.
        self.assertNotRegex(paths.INCLUDE, r"\(\?P|\\A|\\Z")
        re.compile(paths.INCLUDE)

    def test_head_and_history_paths_are_included(self):
        for p in paths.HEAD_PATHS + list(paths.EXTRA_HISTORY):
            self.assertTrue(paths.included(p), p)


if __name__ == "__main__":
    unittest.main()
