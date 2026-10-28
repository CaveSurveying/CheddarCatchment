import os
import shutil
import tempfile
import unittest

from tools.svn2git import verify

LOG = """<?xml version="1.0" encoding="UTF-8"?>
<log>
<logentry revision="270"><author>andrew</author><date>2013-11-19T10:00:00.123456Z</date>
<paths>
<path action="A" kind="dir" text-mods="false" prop-mods="false">/LongwoodValleySink</path>
<path action="A" kind="file" text-mods="true" prop-mods="true">/LongwoodValleySink/a.th</path>
</paths><msg>Added</msg></logentry>
<logentry revision="300"><author>graham</author><date>2015-01-01T00:00:00.000000Z</date>
<paths>
<path action="M" kind="dir" text-mods="false" prop-mods="true">/LongwoodValleySink</path>
</paths><msg>ignores</msg></logentry>
<logentry revision="301"><date>2015-01-02T00:00:00.000000Z</date>
<paths>
<path action="A" kind="dir" text-mods="false" prop-mods="false">/LongwoodValleySink/Outputs</path>
<path action="M" kind="file" text-mods="true" prop-mods="false">/Other/b.th</path>
</paths><msg></msg></logentry>
<logentry revision="302"><author>andrew</author><date>2015-01-03T00:00:00.000000Z</date>
<paths>
<path action="A" kind="dir" copyfrom-path="/Old" copyfrom-rev="1" text-mods="false" prop-mods="false">/LongwoodValleySink/New</path>
</paths><msg>copy</msg></logentry>
</log>
"""

AUTHORS = {"andrew": ("Andrew Atkinson", "andrew@x.invalid"), "graham": ("Graham Mullan", "graham@x.invalid"),
           "(no author)": ("(no author)", "n@x.invalid")}


def git_log(*entries):
    return "".join(f"{n}\x00{e}\x00{d}\x00msg\n\nSVN-Revision: r{r}\nSVN-URL: u\n\x01\n" for r, n, e, d in entries)


class SvnLogTest(unittest.TestCase):
    def setUp(self):
        self.revs = verify.parse_svn_log(LOG)

    def test_parse(self):
        r = self.revs[270]
        self.assertEqual((r.author, r.date), ("andrew", "2013-11-19T10:00:00.123456Z"))
        self.assertEqual([(c.action, c.path, c.kind, c.text_mods) for c in r.changed],
                         [("A", "LongwoodValleySink", "dir", False), ("A", "LongwoodValleySink/a.th", "file", True)])
        self.assertEqual(self.revs[301].author, "")
        self.assertEqual(self.revs[302].changed[0].copyfrom, "Old")

    def test_needs_commit(self):
        self.assertTrue(verify.needs_commit(self.revs[270]))    # adds a file
        self.assertFalse(verify.needs_commit(self.revs[300]))   # properties only
        self.assertFalse(verify.needs_commit(self.revs[301]))   # empty folder; other change excluded
        self.assertTrue(verify.needs_commit(self.revs[302]))    # folder copied with its files


class CompareRevisionsTest(unittest.TestCase):
    def setUp(self):
        self.svn = verify.parse_svn_log(LOG)

    def compare(self, *entries):
        return verify.compare_revisions(self.svn, verify.parse_git_log(git_log(*entries)), AUTHORS)

    def test_all_match(self):
        problems, skipped = self.compare(
            (270, "Andrew Atkinson", "andrew@x.invalid", "2013-11-19T10:00:00+00:00"),
            (302, "Andrew Atkinson", "andrew@x.invalid", "2015-01-03T01:00:00+01:00"))
        self.assertEqual(problems, [])
        self.assertEqual(skipped, [300, 301])

    def test_missing_commit(self):
        problems, _ = self.compare((270, "Andrew Atkinson", "andrew@x.invalid", "2013-11-19T10:00:00Z"))
        self.assertEqual(problems, ["r302: no git commit"])

    def test_wrong_author_and_date(self):
        problems, _ = self.compare(
            (270, "andrew", "andrew@x.invalid", "2013-11-19T10:00:01Z"),
            (302, "Andrew Atkinson", "andrew@x.invalid", "2015-01-03T00:00:00Z"))
        self.assertEqual(len(problems), 2)
        self.assertIn("r270: author andrew", problems[0])
        self.assertIn("r270: date", problems[1])

    def test_extra_commit(self):
        problems, _ = self.compare(
            (270, "Andrew Atkinson", "andrew@x.invalid", "2013-11-19T10:00:00Z"),
            (302, "Andrew Atkinson", "andrew@x.invalid", "2015-01-03T00:00:00Z"),
            (999, "Andrew Atkinson", "andrew@x.invalid", "2015-01-03T00:00:00Z"))
        self.assertEqual(problems, ["r999: git commit for a revision that touches no included path"])

    def test_commits_without_trailer_ignored(self):
        self.assertEqual(verify.parse_git_log("A\x00a\x002020-01-01T00:00:00Z\x00Plan\n\x01"), {})


class CompareTreesTest(unittest.TestCase):
    def setUp(self):
        self.a, self.b = tempfile.mkdtemp(), tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.a)
        self.addCleanup(shutil.rmtree, self.b)

    def put(self, root, path, text):
        full = os.path.join(root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text)

    def test_equal(self):
        for root in (self.a, self.b):
            self.put(root, "Cave/a.th", "x\n")
        self.put(self.b, "Cave/Plan_only.thcfg", "y\n")
        self.assertEqual(verify.compare_trees(self.a, self.b, {"Cave/Plan_only.thcfg"}), [])

    def test_differences(self):
        self.put(self.a, "Cave/a.th", "x\n")
        self.put(self.b, "Cave/a.th", "x\r\n")
        self.put(self.a, "Cave/only_svn.th", "")
        self.put(self.b, "Cave/only_git.th", "")
        self.assertEqual(verify.compare_trees(self.a, self.b),
                         ["only in SVN: Cave/only_svn.th", "only in git: Cave/only_git.th", "differs: Cave/a.th"])


class ExecutableTest(unittest.TestCase):
    def test_executable_files(self):
        ls = ("100644 blob 1\tLongwoodValleySink/a.th\n100755 blob 2\tLongwoodValleySink/b c.th\n"
              "120000 blob 3\tLongwoodValleySink/link\n100755 blob 4\ttools/svn2git/migrate.sh\n")
        self.assertEqual(verify.executable_files(ls), ["LongwoodValleySink/b c.th"])


if __name__ == "__main__":
    unittest.main()
