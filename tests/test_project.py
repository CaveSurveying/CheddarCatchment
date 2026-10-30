import os
import unittest

from tools.sketch2therion import project

MINIMAL = """
[cave]
name = "C"
title = "C"
folder = "C"
master = "C/C.th"
survey = "C"
thconfig = "C/Plan_only.thcfg"
plan_map = "CMP"
plan_map_file = "C/C.th"
[names]
survey_file = "{survey}/{survey}.th"
plan_file = "{survey}/{survey}.plan.th2"
scrap_prefix = "{survey}S"
survey_plan_map = "{survey}MP"
plan_sketch = '(\\\\.plan|P)\\\\.xvi$'
[drawing]
line_endings = "crlf"
map_scale = 200
licence = "CC BY-NC-SA 4.0"
[build]
outputs = "C/Outputs"
log = "output/therion.log"
layout_plan = "output/layout-plan.xvi"
layout_extended = "output/layout-extended.xvi"
sql = "output/layout.sql"
review_plan = "output/review-plan.pdf"
"""


class ProjectTest(unittest.TestCase):
    def setUp(self):
        self.p = project.load()

    def test_names(self):
        self.assertEqual(self.p.plan_file("GoSouth"), "LongwoodValleySink/GoSouth/GoSouthP.th2")
        self.assertEqual(self.p.extended_file("GoSouth"), "LongwoodValleySink/GoSouth/GoSouthEe.th2")
        self.assertEqual(self.p.survey_file("GoSouth"), "LongwoodValleySink/GoSouth/GoSouth.th")
        self.assertEqual(self.p.scrap_prefix("GoSouth") + "P1", "GoSouthSP1")
        self.assertEqual(self.p.survey_plan_map("GoSouth"), "GoSouthMP")
        self.assertEqual(self.p.qualified("GoSouthMP", "GoSouth"), "GoSouthMP@GoSouth")

    def test_drawing(self):
        self.assertEqual(self.p.newline, "\n")
        self.assertEqual(self.p.drawing["map_scale"], 500)
        self.assertIn("CC BY-NC-SA 4.0", self.p.licence_comment)

    def test_plan_sketches(self):
        for f in ["X/Notes/X.plan.xvi", "Triassic/PocketTopo/Triasic_p.xvi", "GoSouth/Notes/GoSouthP.xvi"]:
            self.assertTrue(self.p.is_plan_sketch(f), f)
        for f in ["X/Notes/X.ee.xvi", "GoSouth/Notes/GoSouthE.xvi", "TridentEe.xvi", "CyclopsE315.xvi",
                  "Triasic_e.xvi", "BoldStepEE.xvi", "NorthRiftE090.xvi"]:
            self.assertFalse(self.p.is_plan_sketch(f), f)

    def test_every_file_it_names_exists(self):
        for rel in [self.p.cave["master"], self.p.cave["thconfig"], self.p.cave["plan_map_file"],
                    self.p.cave["folder"], self.p.build["outputs"]]:
            self.assertTrue(os.path.exists(self.p.path(rel)), rel)

    def test_plan_map_is_in_its_file(self):
        with open(self.p.path(self.p.cave["plan_map_file"]), encoding="utf-8") as f:
            self.assertRegex(f.read(), rf"(?m)^map {self.p.cave['plan_map']}\b")

    def test_licence_matches_style(self):
        with open(self.p.path("tools/sketch2therion/Style.md"), encoding="utf-8") as f:
            self.assertIn(self.p.drawing["licence"], f.read())

    def test_sheets(self):
        self.assertEqual([s["file"] for s in self.p.sheets], ["LongwoodValleySinkP.pdf"])

    def test_parse_minimal(self):
        p = project.parse(MINIMAL)
        self.assertEqual(p.newline, "\r\n")
        self.assertEqual(p.sheets, [])

    def test_missing_key_named(self):
        with self.assertRaisesRegex(project.ConfigError, "missing build.sql"):
            project.parse(MINIMAL.replace('sql = "output/layout.sql"\n', ""))
        with self.assertRaisesRegex(project.ConfigError, "missing cave.master"):
            project.parse(MINIMAL.replace('master = "C/C.th"\n', ""))

    def test_bad_values(self):
        with self.assertRaisesRegex(project.ConfigError, "line_endings"):
            project.parse(MINIMAL.replace('"crlf"', '"cr"'))
        with self.assertRaisesRegex(project.ConfigError, r"sheets\[0\].blurb"):
            project.parse(MINIMAL + '[[sheets]]\nfile = "a.pdf"\ntitle = "A"\n')


if __name__ == "__main__":
    unittest.main()
