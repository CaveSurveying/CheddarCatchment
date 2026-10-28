import os
import shutil
import tempfile
import unittest

from tools.sketch2therion import project
from tools.web import make_index

LOG = """therion 6.2.0 (2023-12-21)
output coordinate system: OSGB:ST
 6> Total length of survey legs = 1682.18m (1681.18m adjusted)
 9> Vertical range = 132.19m (from 1587 at 207.00m to 2021 at 74.81m)
therion: warning -- magnetic declination calculated for dates outside of optimal model range
mpost: scrap outline intersects itself (CyclopsSP1)
mpost: scrap outline intersects itself (CyclopsSP1)
mpost: scrap outline intersects itself (CJSSP2)
"""


class StatsTest(unittest.TestCase):
    def test_from_log(self):
        stats = make_index.survey_stats(LOG)
        self.assertEqual(stats["Surveyed length"], "1682.2 m")
        self.assertEqual(stats["Vertical range"], "132.19 m")
        self.assertEqual(stats["Coordinate system"], "OSGB:ST")
        self.assertEqual(stats["Therion errors"], "0")
        self.assertEqual(stats["Scrap outlines that cross themselves"], "2")
        self.assertIn("- **Surveyed length:** 1682.2 m\n", make_index.stats_markdown(stats))

    def test_errors_counted(self):
        self.assertEqual(make_index.survey_stats("therion: error -- x\n")["Therion errors"], "1")


class CollectTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root)
        self.p = project.load(root=self.root)
        os.makedirs(os.path.join(self.root, self.p.build["outputs"]))
        self.out = os.path.join(self.root, "output")
        os.makedirs(self.out)

    def test_missing_sheet_skipped(self):
        self.assertEqual(make_index.collect(self.p, self.out), [])
        html = make_index.page(self.p, [], {}, {})
        self.assertIn("No sheets were built.", html)

    def test_sheets_from_project_toml(self):
        with open(os.path.join(self.root, self.p.build["outputs"], "LongwoodValleySinkP.pdf"), "wb") as f:
            f.write(b"%PDF-1.4\n")
        found = make_index.collect(self.p, self.out)
        self.assertEqual([s["file"] for s, _ in found], ["LongwoodValleySinkP.pdf"])
        self.assertTrue(os.path.exists(os.path.join(self.out, "LongwoodValleySinkP.pdf")))
        html = make_index.page(self.p, found, {"Surveyed length": "1 m"}, {}, "abcdef123")
        self.assertIn('href="LongwoodValleySinkP.pdf"', html)
        self.assertIn("Longwood Valley Sink", html)
        self.assertIn("CC BY-NC-SA 4.0", html)
        self.assertIn("abcdef1", html)


if __name__ == "__main__":
    unittest.main()
