"""Plan scraps chosen by hand ([scraps] in tools/project.toml)."""
import math
import os
import re
import subprocess
import sys
import tempfile
import unittest

from tools import project
from tools.sketch2therion import scraps

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = [str(n) for n in range(1, 30) if n != 25]


class Parse(unittest.TestCase):
    def test_ranges_take_only_existing_stations(self):
        g = scraps.parse(["1-16", "17-29"], NAMES)
        self.assertEqual(g[0], [str(n) for n in range(1, 17)])
        self.assertNotIn("25", g[1])
        self.assertEqual(len(g[1]), 12)

    def test_names_and_commas(self):
        self.assertEqual(scraps.parse(["19, 21-23 1"], NAMES), [["19", "21", "22", "23", "1"]])

    def test_unknown_station_fails(self):
        with self.assertRaisesRegex(ValueError, "no station 99"):
            scraps.parse(["99"], NAMES)

    def test_station_in_two_scraps_fails(self):
        with self.assertRaisesRegex(ValueError, "station 5 is in more than one"):
            scraps.parse(["1-5", "5-9"], NAMES)

    def test_unlisted_stations_follow_their_legs(self):
        g = scraps.complete([["1", "2"], ["5"]], ["1", "2", "3", "4", "5"], [("2", "3"), ("3", "4"), ("5", "6")])
        self.assertEqual(sorted(g[0]), ["1", "2", "3", "4"])

    def test_station_with_no_way_in_fails(self):
        with self.assertRaisesRegex(ValueError, "stations 9 are in no scrap"):
            scraps.complete([["1", "2"]], ["1", "2", "9"], [("1", "2")])


class Assign(unittest.TestCase):
    # two parallel passages 2 m apart, joined by a leg 2-3 that is in neither scrap
    pos = {"1": (0, 0), "2": (10, 0), "3": (10, -2), "4": (0, -2)}
    legs = [("1", "2"), ("2", "3"), ("3", "4")]
    groups = [["1", "2"], ["3", "4"]]

    def test_strokes_go_with_their_nearest_leg(self):
        lines = [("BLACK", [(0, 1), (10, 1)]), ("BLACK", [(0, -3), (10, -3)])]
        out = scraps.assign(lines, self.groups, self.pos, self.legs)
        self.assertEqual([k for k, _, _ in out], [0, 1])

    def test_wall_between_passages_cut_where_scrap_changes(self):
        # one stroke along the top passage, then turning down along the bottom one
        pp = [(x, 0.3) for x in range(0, 6)] + [(5, -1.0), (5, -2.3)] + [(x, -2.3) for x in range(6, 10)]
        out = scraps.assign([("BLACK", pp)], self.groups, self.pos, self.legs)
        self.assertEqual([k for k, _, _ in out], [0, 1])
        self.assertEqual(out[0][2][-1], out[1][2][0])      # the pieces meet

    def test_short_wavering_piece_not_split_off(self):
        pp = [(0, 0.5), (3, 0.5), (3.1, -1.1), (3.2, 0.5), (8, 0.5)]
        out = scraps.assign([("BLACK", pp)], self.groups, self.pos, self.legs)
        self.assertEqual(len(out), 1)

    def test_closed_loop_kept_whole(self):
        loop = [(4, 0.2), (5, 0.2), (5, -1.6), (4, -1.6), (4, 0.2)]
        out = scraps.assign([("BROWN", loop)], self.groups, self.pos, self.legs)
        self.assertEqual(len(out), 1)


class MeetEnds(unittest.TestCase):
    TEXT = """scrap A -projection plan
line wall
  0.00 0.00
  100.00 0.00
endline
line wall -subtype invisible -close on
  0 0
  1 1
endline
endscrap
scrap B -projection plan
line wall
  110.00 4.00
  200.00 0.00 210.00 0.00 300.00 0.00
endline
line wall
  0.00 50.00
  500.00 50.00
endline
endscrap
"""

    def test_walls_in_two_scraps_meet_at_the_midpoint(self):
        out = scraps.meet_ends(self.TEXT, 20)
        self.assertEqual(out.count("105.00 2.00"), 2)
        self.assertIn("  0.00 50.00", out)          # too far from any other scrap's wall end
        self.assertIn("  0.00 0.00", out)

    def test_walls_in_one_scrap_left_alone(self):
        text = self.TEXT.replace("endscrap\nscrap B -projection plan\n", "")
        self.assertEqual(scraps.meet_ends(text, 20), text)


class GoSouth(unittest.TestCase):
    def test_config(self):
        self.assertEqual(project.load().scraps.get("GoSouth"), ["1-16", "17-29"])

    @unittest.skipUnless(os.path.exists(os.path.join(REPO, "output", "layout-plan.xvi")),
                         "needs the layout (therion tools/layout.thcfg)")
    def test_two_scraps_and_no_leg_15_17(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "GoSouth.plan.th2")
            subprocess.run([sys.executable, "-m", "tools.sketch2therion", "plan",
                            os.path.join(REPO, "LongwoodValleySink", "GoSouth", "Notes", "GoSouthP.xvi"),
                            "--survey", "GoSouth", "-o", out], cwd=REPO, check=True, capture_output=True)
            text = open(out).read()
        bodies = dict(re.findall(r"(?ms)^scrap (\S+)[^\n]*\n(.*?)^endscrap", text))
        self.assertEqual(sorted(bodies), ["GoSouthSP1", "GoSouthSP2"])
        st = {k: set(re.findall(r"station -name (\S+)", b)) for k, b in bodies.items()}
        self.assertTrue({"9", "10", "11", "12", "15", "16"} <= st["GoSouthSP1"])
        self.assertTrue({"17", "18", "19", "20", "21"} <= st["GoSouthSP2"])
        self.assertFalse(st["GoSouthSP1"] & st["GoSouthSP2"])
        # the north wall by 21 is one wall across the two scraps: its pieces meet
        def ends(body):
            out = []
            for m in re.finditer(r"(?ms)^line wall(?! -subtype)[^\n]*\n(.*?)^endline", body):
                rows = [r.split() for r in m.group(1).strip().splitlines() if re.match(r"\s*-?\d", r)]
                out += [tuple(rows[0][-2:]), tuple(rows[-1][-2:])]
            return set(out)
        self.assertTrue(ends(bodies["GoSouthSP1"]) & ends(bodies["GoSouthSP2"]))


if __name__ == "__main__":
    unittest.main()


class Areas(unittest.TestCase):
    """Areas: few nodes, splines, run out over the walls (Style.md)."""

    def tearDown(self):
        from tools.sketch2therion import settings
        settings.load()

    def test_area_over_the_wall_as_a_spline(self):
        from shapely.geometry import box
        from tools.sketch2therion import marks, settings
        settings.load()
        passage = box(0, 0, 6, 2)
        loops = []
        for k in range(8):                    # boulders along the wall at y = 0
            x = 0.5 + 0.6 * k
            loops.append(("BROWN", [(x, 0.05), (x + 0.4, 0.05), (x + 0.4, 0.45), (x, 0.45), (x, 0.05)]))
        o = marks.th2(loops, passage, lambda p: (100 * p[0], 100 * p[1]), "XSP1", ["BLACK"], 0.3)
        text = "\n".join(o)
        m = re.search(r"(?ms)^line border -subtype invisible -id (\S+) -close on\n(.*?)^endline", text)
        self.assertIsNotNone(m, text)
        rows = m.group(2).strip().splitlines()
        self.assertLessEqual(len(rows), 10)
        self.assertTrue(all(len(r.split()) == 6 for r in rows[1:]))        # Bezier segments
        ys = [float(r.split()[-1]) for r in rows]
        self.assertLess(min(ys), 0)                                         # over the wall
