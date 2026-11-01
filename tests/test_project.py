"""This cave's tools/project.toml (how it is read is tested in Therion-Sketching)."""

import os
import unittest

from tools.sketch2therion import project


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

if __name__ == "__main__":
    unittest.main()
