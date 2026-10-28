import datetime
import os
import tempfile
import unittest

from tools.svn2git import inventory as inv


def write(root, rel, text=""):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


SEXYTOPO_TH = """encoding utf-8
survey BoldStep
# Created with SexyTopo 1.12.2 on 2026-07-25

input "BoldStepP.th2"
input "BoldStepEE.th2"

centreline
date 2026.07.25
team "Alison Moody" instruments
team "Andrew Atkinson " notes
explo-date 2025.01.01

data dimensions station left right up down ignoreall
0 1.0 2.0 3.0 4.0

data normal from to tape compass clino ignoreall
#0\t1\t1.185\t219.12\t6.70
0\t1\t1.180\t219.08\t7.14
0\t-\t0.950\t100.00\t0.00
1\t2\t1.760\t309.05\t14.17
endcentreline
endsurvey
"""

EMPTY_PLAN_TH2 = """encoding utf-8
##XTHERION## xth_me_image_insert {0.0 1 1.0} {0.0 0} "Notes/BoldStepP.xvi" 0 {}
scrap BoldStepP1 -projection plan
point 0.0 0.0 station -name 0
endscrap
"""

DRAWN_PLAN_TH2 = """encoding utf-8
scrap TickleWestSP1 -projection plan -scale [0 0 1 0 0 0 1 0 m]
line wall
  0 0
  10 0
endline
endscrap
"""


class ParseThTest(unittest.TestCase):
    def test_sexytopo_survey(self):
        s = inv.parse_th(SEXYTOPO_TH)
        self.assertEqual(s.name, "BoldStep")
        self.assertEqual(s.dates, [datetime.date(2026, 7, 25)])     # explo-date not counted
        self.assertEqual(s.team, ["Alison Moody", "Andrew Atkinson"])
        self.assertAlmostEqual(s.length, 1.18 + 1.76)                # commented shot, splay, LRUD skipped
        self.assertEqual(s.inputs, [("BoldStepP.th2", False), ("BoldStepEE.th2", False)])

    def test_dates(self):
        self.assertEqual(inv.parse_dates(" 2026.03.14"), [datetime.date(2026, 3, 14)])
        self.assertEqual(inv.parse_dates(" 2025.12.30 - 2026.01.02"),
                         [datetime.date(2025, 12, 30), datetime.date(2026, 1, 2)])
        self.assertEqual(inv.parse_dates(" 2026.02"), [datetime.date(2026, 2, 1)])
        self.assertEqual(inv.parse_dates(" 2026.13.40"), [])

    def test_commented_and_several_dates(self):
        s = inv.parse_th("survey A\ncentreline\n#date 2026.01.01\ndate 2022.09.19\n"
                         "date 2023.10.27 # resurvey\nendcentreline\n"
                         "centreline\ndate 2024.01.01\nendcentreline\nendsurvey\n")
        self.assertEqual([d.year for d in s.dates], [2022, 2023, 2024])

    def test_feet_and_other_column_order(self):
        s = inv.parse_th("survey A\ncentreline\nunits length feet\n"
                         "data normal from to compass clino tape\n1 2 10 0 10\nendcentreline\n")
        self.assertAlmostEqual(s.length, 3.048)

    def test_commented_input(self):
        s = inv.parse_th('survey A\n#input "AP.th2"\n  input AE.th2\n')
        self.assertEqual(s.inputs, [("AP.th2", True), ("AE.th2", False)])

    def test_hash_inside_quotes_is_not_a_comment(self):
        self.assertEqual(inv.strip_comment('team "No #1" notes # x'), 'team "No #1" notes')


class YearFilterTest(unittest.TestCase):
    def test_boundaries(self):
        a = inv.Survey("a", "A", dates=[datetime.date(2025, 12, 31)])
        b = inv.Survey("b", "B", dates=[datetime.date(2026, 1, 1)])
        c = inv.Survey("c", "C", dates=inv.parse_dates("2025.12.30 - 2026.01.02"))
        self.assertEqual([s.name for s in inv.of_year([a, b, c], 2026)], ["B", "C"])


class Th2Test(unittest.TestCase):
    def test_empty_sexytopo_scrap(self):
        t = inv.parse_th2(EMPTY_PLAN_TH2)
        self.assertEqual([(s.id, s.projection, s.has_wall) for s in t.scraps], [("BoldStepP1", "plan", False)])
        self.assertEqual(t.images, ["Notes/BoldStepP.xvi"])

    def test_drawn_scrap(self):
        t = inv.parse_th2(DRAWN_PLAN_TH2)
        self.assertEqual([(s.id, s.has_wall) for s in t.scraps], [("TickleWestSP1", True)])

    def test_wall_subtype_counts(self):
        t = inv.parse_th2("scrap A -projection plan\nline wall:presumed\n0 0\nendline\nendscrap\n")
        self.assertTrue(t.scraps[0].has_wall)

    def test_elevation_scrap(self):
        t = inv.parse_th2("scrap AE1 -projection extended\nline wall\nendline\nendscrap\n")
        self.assertEqual(t.scraps[0].projection, "extended")


class MapsTest(unittest.TestCase):
    def test_namespaces_do_not_collide(self):
        # Maps.th and Cyclops.th both define a map called CyclopsMP
        maps = {
            "TopMP": ["CyclopsMP"],
            "CyclopsMP": ["CyclopsSP1@Cyclops", "CyclopsEyeSP1@CyclopsEye"],
            "CyclopsMP@Cyclops": ["CyclopsSP1"],
            "TickleMP@Tickle": ["TickleSP1"],
        }
        reach = inv.map_closure(maps, "TopMP")
        self.assertIn("CyclopsEyeSP1", reach)
        self.assertNotIn("TickleSP1", reach)

    def test_member_resolved_in_its_map_namespace(self):
        maps = {"TopMP": ["TickleMP@Tickle"], "TickleMP@Tickle": ["TickleSP1"]}
        self.assertIn("TickleSP1", inv.map_closure(maps, "TopMP"))

    def test_parse_maps_skips_break_and_comments(self):
        maps = inv.parse_maps("map M\n  A\n break\n  #B\n  C@S # note\nendmap\n")
        self.assertEqual(maps, {"M": ["A", "C@S"]})


class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        r = self.root = self.tmp.name
        write(r, "Cave/Cave.th", "survey Cave\ninput New/New.th\ninput Old/Old.th\n#input Hidden/Hidden.th\n"
                                 "input Maps.th\nendsurvey\n")
        write(r, "Cave/Maps.th", "map CaveMP\n  OldMP@Old\nendmap\n")
        # 2026, SexyTopo empty scrap, sketch present
        write(r, "Cave/New/New.th", SEXYTOPO_TH.replace("BoldStep", "New"))
        write(r, "Cave/New/NewP.th2", EMPTY_PLAN_TH2.replace("BoldStep", "New"))
        write(r, "Cave/New/Notes/NewP.xvi", "")
        # drawn, input and in the plan map
        write(r, "Cave/Old/Old.th", 'survey Old\ninput "Old.plan.th2"\nmap OldMP\n  OldSP1\nendmap\n'
                                    "centreline\ndate 2024.10.26\nendcentreline\nendsurvey\n")
        write(r, "Cave/Old/Old.plan.th2", DRAWN_PLAN_TH2.replace("TickleWestSP1", "OldSP1"))
        # drawn, input commented out on purpose, in no map
        write(r, "Cave/Hidden/Hidden.th", '#input Hidden.plan.th2\nsurvey Hidden\n'
                                          "centreline\ndate 2026.02.01\nendcentreline\nendsurvey\n")
        write(r, "Cave/Hidden/Hidden.plan.th2", DRAWN_PLAN_TH2.replace("TickleWestSP1", "HiddenSP1"))
        # 2026, no plan .th2 at all; input file name in different case
        write(r, "Cave/Bare/Bare.th", "survey Bare\ninput bareP.th2\ncentreline\ndate 2026.05.05\nendcentreline\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_classification(self):
        by = {s.name: s for s in inv.inventory(self.root, "Cave")}
        self.assertEqual(by["New"].status, "undrawn")
        self.assertEqual(by["Old"].status, "drawn")
        self.assertEqual(by["Old"].note, "")
        self.assertEqual(by["Hidden"].status, "drawn, reported")
        self.assertIn("not input: Hidden.plan.th2", by["Hidden"].note)
        self.assertIn("in no plan map: HiddenSP1", by["Hidden"].note)
        self.assertIn("not input in Cave.th", by["Hidden"].note)
        self.assertEqual((by["Bare"].status, by["Bare"].note.split(";")[0]), ("undrawn", "no plan .th2"))
        self.assertIn("not input in Cave.th", by["Bare"].note)

    def test_markdown_lists_only_undrawn_of_year(self):
        text = inv.markdown(self.root, "Cave", inv.inventory(self.root, "Cave"), 2026, "501")
        todo = text.split("## Reported")[0]
        self.assertIn("| New (", todo)
        self.assertIn("| Bare (", todo)
        self.assertNotIn("Hidden (", todo)       # drawn: reported, not for drawing
        self.assertNotIn("| Old (", todo)        # 2024
        self.assertIn("| present |", todo)       # New's sketch
        self.assertIn("From SVN revision 501", text)


if __name__ == "__main__":
    unittest.main()
