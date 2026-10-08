"""Converter changes from the review of Trident draft 1 (docs/lvs-phase5-log.md)."""
import math
import os
import re
import unittest

from tools.sketch2therion import marks, nodes, scale, settings, tidy

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Scale(unittest.TestCase):
    def tearDown(self):
        scale.clear()

    def test_mean_of_the_three_nearest_legs(self):
        scale.use([((0, 0), (2, 0)), ((2, 0), (4, 0)), ((4, 0), (8, 0)), ((100, 0), (200, 0))])
        self.assertAlmostEqual(scale.at((1, 1)), (2 + 2 + 4) / 3)

    def test_relative_or_absolute(self):
        scale.use([((0, 0), (3, 0))], K=1.0)
        self.assertAlmostEqual(scale.tol((0, 0), 0.05, 0.1), 0.15)
        self.assertEqual(scale.tol((0, 0), 0.0, 0.1), 0.1)
        scale.clear()
        self.assertEqual(scale.tol((0, 0), 0.05, 0.1), 0.1)


class FewerPoints(unittest.TestCase):
    def tearDown(self):
        settings.load()
        scale.clear()

    def test_longer_legs_fewer_points(self):
        settings.load()
        wobbly = [(x * 0.1, 0.25 * math.sin(x * 0.25)) for x in range(80)]   # bends 0.25 m either side
        px = lambda p: p
        scale.use([((0, -1), (2, -1))])                 # 2 m legs
        short = len(marks.smooth_rows(wobbly, px))
        scale.use([((0, -1), (8, -1))])                 # 8 m legs
        long_ = len(marks.smooth_rows(wobbly, px))
        self.assertLess(long_, short)


class WallsMeet(unittest.TestCase):
    def wall(self, pts):
        o = tidy.Obj('line', 'line wall', [])
        o.set_segments([[x, y] for x, y in pts])
        return o

    def test_ends_close_together_meet(self):
        a, b = self.wall([(0, 0), (100, 0)]), self.wall([(110, 5), (200, 5)])
        self.assertEqual(nodes.walls_meet([a, b], 100.0, 0.2), 2)
        self.assertEqual(tuple(a.segments()[-1][-2:]), tuple(b.segments()[0][-2:]))

    def test_not_across_a_survey_leg(self):
        a, b = self.wall([(0, 0), (100, 0)]), self.wall([(110, 5), (200, 5)])
        self.assertEqual(nodes.walls_meet([a, b], 100.0, 0.2, legs=[((105, -10), (105, 20))]), 0)

    def test_undone_if_the_outline_suffers(self):
        a, b = self.wall([(0, 0), (100, 0)]), self.wall([(110, 5), (200, 5)])
        before = (a.rows, b.rows)
        self.assertEqual(nodes.walls_meet([a, b], 100.0, 0.2, ok=lambda: False), 0)
        self.assertEqual((a.rows, b.rows), before)

    def test_long_segment_measured_closely(self):
        # a 12 m Bezier segment: the nearest point is found to within a few cm
        segs = [[0, 0], [400, 0, 800, 0, 1200, 0]]
        d = nodes.nearest_on(segs, (613, 5))[0]
        self.assertAlmostEqual(d, 5, delta=1.5)


class Curls(unittest.TestCase):
    def test_a_curl_is_a_closed_loop(self):
        c = [(0.3 * math.cos(a / 10), 0.3 * math.sin(a / 10)) for a in range(0, 52)]      # 300 degrees round
        self.assertTrue(marks.is_curl(c))
        self.assertFalse(marks.is_curl([(0, 0), (0.5, 0.02), (1.0, 0)]))


class SectionInPlace(unittest.TestCase):
    @unittest.skipUnless(os.path.exists(os.path.join(REPO, "output", "layout-plan.xvi")),
                         "needs the layout (therion tools/layout.thcfg)")
    def test_section_drawn_by_its_mark(self):
        import subprocess, sys, tempfile
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "t.th2")
            subprocess.run([sys.executable, "-m", "tools.sketch2therion", "plan",
                            os.path.join(REPO, "LongwoodValleySink", "Trident", "Notes", "TridentP.xvi"),
                            "--survey", "Trident", "-o", out], cwd=REPO, check=True, capture_output=True)
            text = open(out).read()
        mark = re.search(r"point (\S+) (\S+) section -scrap (\S+)", text)
        xs = re.search(r"(?ms)^scrap %s .*?^line wall -close on\n\s*(\S+) (\S+)" % mark.group(3), text)
        self.assertLess(math.dist(tuple(map(float, mark.groups()[:2])), tuple(map(float, xs.groups()))), 2 * 78.74)


if __name__ == "__main__":
    unittest.main()


class NodeGap(unittest.TestCase):
    """No two nodes too close to pick apart when editing (nodes.thin)."""

    def test_close_nodes_go_ends_stay(self):
        out = nodes.thin([[0, 0], [10, 0], [11, 0], [20, 0], [30, 0], [30.5, 0]], 3)
        self.assertEqual([tuple(s[-2:]) for s in out], [(0, 0), (10, 0), (20, 0), (30.5, 0)])

    def test_merged_segment_follows_the_shape(self):
        # a sweep sampled with an extra node: the node goes and the curve barely moves
        import math as m
        arc = [(10 * m.cos(a), 10 * m.sin(a)) for a in (0, 0.5, 0.55, 1.1)]
        segs = [[*arc[0]]] + [[*p] for p in arc[1:]]
        out = nodes.thin(segs, 1.0, maxerr=0.5)
        self.assertEqual(len(out), 3)

    def test_s_bend_keeps_its_node_a_sweep_does_not(self):
        # the user's point: sweeps need few nodes, S bends more
        s_bend = [[0, 0], [0.2, 0.8, 0.8, 0.8, 1, 0], [1.2, -0.8, 1.8, -0.8, 2, 0]]
        sweep = [[0, 0], [0.2, 0.3, 0.8, 0.5, 1, 0.55], [1.2, 0.6, 1.8, 0.5, 2, 0.2]]
        self.assertEqual(len(nodes.thin(s_bend, 1.5, maxerr=0.1)), 3)
        self.assertEqual(len(nodes.thin(s_bend, 1.5)), 2)              # with no limit it would go
        self.assertEqual(len(nodes.thin(sweep, 1.5, maxerr=0.05)), 2)

    def test_nothing_to_thin(self):
        segs = [[0, 0], [10, 0], [20, 0]]
        self.assertEqual(nodes.thin(segs, 3), segs)

    def test_closed_line_stays_closed(self):
        o = tidy.Obj('line', 'line border -close on', [])
        o.set_segments([[0, 0], [10, 0], [10.5, 0], [10, 10], [0, 10], [0, 0]])
        nodes.thin_scrap([o], 1.0, lambda o: 2.0)
        s = o.segments()
        self.assertEqual(tuple(s[0][-2:]), tuple(s[-1][-2:]))
        self.assertEqual(len(s), 5)


class RelativeJoin(unittest.TestCase):
    def wall(self, pts):
        o = tidy.Obj('line', 'line wall', [])
        o.set_segments([[x, y] for x, y in pts])
        return o

    def test_reach_can_depend_on_where(self):
        a, b = self.wall([(0, 0), (100, 0)]), self.wall([(130, 0), (200, 0)])     # 0.3 m apart (K = 100)
        self.assertEqual(nodes.walls_meet([a, b], 100.0, lambda p: 0.2), 0)
        self.assertEqual(nodes.walls_meet([a, b], 100.0, lambda p: 0.4), 2)


class RockFaces(unittest.TestCase):
    """The fill without the rock its closing-up took in (convert.drop_rock_faces)."""

    def test_face_with_no_leg_across_bridged_edge_goes(self):
        from shapely.geometry import box
        from tools.sketch2therion.convert import drop_rock_faces
        fill = box(0, 0, 10, 4)                     # closed up across rock above y = 2.5
        wall = [(0, 2.5), (10, 2.5)]
        out = drop_rock_faces(fill, [wall], [[(0, 1), (10, 1)]], [(0, 1), (10, 1)])
        self.assertAlmostEqual(out.area, 25.0, delta=0.5)

    def test_pillar_stays(self):
        from shapely.geometry import box
        from tools.sketch2therion.convert import drop_rock_faces
        fill = box(0, 0, 10, 4)
        pillar = [(4, 1.5), (6, 1.5), (6, 2.5), (4, 2.5), (4, 1.5)]
        out = drop_rock_faces(fill, [pillar], [[(0, 0.5), (10, 0.5)], [(0, 3.5), (10, 3.5)]], [(0, 0.5)])
        self.assertAlmostEqual(out.area, 40.0, delta=0.5)

    def test_alcove_along_a_sketched_wall_stays(self):
        # a ledge line cuts off a side with no leg, but its edge there is the sketched wall
        from shapely.geometry import box
        from tools.sketch2therion.convert import drop_rock_faces
        fill = box(0, 0, 10, 4)
        outer = [(0, 4), (10, 4)]
        ledge = [(1, 4), (1, 3), (9, 3), (9, 4)]       # from the wall round and back to it
        out = drop_rock_faces(fill, [outer, ledge], [[(0, 1), (10, 1)]], [(0, 1)])
        self.assertAlmostEqual(out.area, 40.0, delta=0.5)


class WallHooks(unittest.TestCase):
    def tearDown(self):
        settings.load()

    def test_open_loop_at_a_wall_is_wall(self):
        from tools.sketch2therion.convert import wall_strokes
        settings.load()
        wall = [(0, 0), (3, 0)]
        hook = [(3.05, 0), (3.3, 0.25), (3.3, 0.5), (3.0, 0.55), (2.8, 0.35), (2.9, 0.15)]   # open, starts at the wall
        walls, boulders, _ = wall_strokes([('BLACK', wall), ('BLACK', hook)])
        self.assertEqual(len(boulders), 0)
        self.assertEqual(len(walls), 2)
        settings.use(dict(settings.SETTINGS, wall_hooks=False))
        walls, boulders, _ = wall_strokes([('BLACK', wall), ('BLACK', hook)])
        self.assertEqual(len(boulders), 1)
