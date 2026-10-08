"""Elevation features read from the sketch by shape (tools/sketch2therion/elevation.py)."""
import math
import unittest

from tools.sketch2therion import elevation as el, settings
from tools.sketch2therion.tidy import parse_scrap


class Shapes(unittest.TestCase):
    def test_pool_surface_is_straight_and_level(self):
        self.assertTrue(el.is_pool_surface([(0, 0), (0.6, 0.01), (1.2, 0.02)]))
        self.assertFalse(el.is_pool_surface([(0, 0), (0.6, 0.3), (1.2, 0.6)]))      # sloping
        self.assertFalse(el.is_pool_surface([(0, 0), (0.6, 0.3), (1.2, 0)]))        # bent

    def test_curl_is_rubble_floor_line_is_not(self):
        curl = [(0.3 + 0.25 * math.cos(t / 5), 0.25 * math.sin(t / 5)) for t in range(40)]
        self.assertTrue(el.is_curl(curl))
        self.assertFalse(el.is_curl([(x * 0.5, 0) for x in range(10)]))

    def test_curtain_hangs_and_is_long(self):
        self.assertTrue(el.is_curtain([(0, 0), (0.05, -0.6), (0, -1.3)]))
        self.assertFalse(el.is_curtain([(0, 0), (0, -0.6)]))                      # a stalactite's stroke
        self.assertFalse(el.is_curtain([(0, 0), (1.3, -0.2)]))

    def test_blocks_humpy_and_gentle_flowstone_smooth_or_steep(self):
        hump = [(x * 0.1, 0.5 * math.sin(math.pi * x / 12)) for x in range(13)]
        self.assertTrue(el.is_blocks(hump))
        self.assertFalse(el.is_blocks([(0, 0), (0.6, 0.02), (1.2, 0.03)]))
        steep = [(0, 0), (0.2, 0.9), (1.2, 1.5)]
        self.assertFalse(el.is_blocks(steep))


class Features(unittest.TestCase):
    def setUp(self):
        settings.load()

    def test_sorted_out(self):
        lines = [('BLUE', [(0, 0), (0.6, 0.0), (1.2, 0.01)]),                 # pool surface
                 ('BLUE', [(5, 1), (5.2, 1.1), (5.4, 0.95), (5.6, 1.05)]),     # flow
                 ('BLACK', [(8, 0), (8.6, 0), (8.6, 0.6), (8, 0.6), (8, 0.02)]),   # rock
                 ('BLACK', [(-5, -1), (15, -1)])]
        f = el.features(lines, [(3, 0.5)])
        self.assertEqual(len(f.pools), 1)
        self.assertEqual(len(f.flows), 1)
        self.assertEqual(len(f.rocks), 1)
        self.assertEqual([c for c, _ in f.lines], ['BLACK'])

    def test_flow_goes_under_the_floor_pointing_downhill(self):
        floor = [(0, 0), (10, -2)]
        (x, y), ori = el._floor_below([floor], (5, -0.5))
        self.assertAlmostEqual(y, -1.0, places=2)
        self.assertTrue(90 < ori < 180)                                       # right and down

    def test_bowl_only_where_no_floor(self):
        f = el.Features()
        f.pools = [(0, 2, 0)]
        self.assertEqual(len(el.bowls(f, [[(-1, -0.4), (3, -0.4)]])), 0)
        self.assertEqual(len(el.bowls(f, [])), 1)


class Adjusted(unittest.TestCase):
    def test_line_with_adjust_is_left_as_drawn(self):
        body = "line border -id p -close on -subtype invisible\n  0 0\n  10 0\n  adjust horizontal\n  5 -3\nendline\n"
        objs = parse_scrap(body)
        self.assertEqual([o.kind for o in objs if o.kind != 'text' or 'adjust' in o.raw][0], 'text')
        self.assertIn('adjust horizontal', ''.join(o.text() for o in objs))


if __name__ == '__main__':
    unittest.main()


class WallSubtypes(unittest.TestCase):
    def setUp(self):
        settings.load()

    def test_one_line_per_subtype_never_a_point_subtype(self):
        from tools.sketch2therion.smooth import wall_subtypes
        K = 100.0
        body = ("# wall-subtype clay: 500 0 1000 0\n\n"
                "line wall\n  0 0\n  250 0\n  500 0\n  750 0\n  1000 0\nendline\n")
        objs = parse_scrap(body)
        wall_subtypes(objs, K)
        text = '\n'.join(o.text() for o in objs)
        self.assertNotIn('  subtype', text)
        heads = [o.head for o in objs if o.kind == 'line']
        self.assertEqual(heads, ['line wall', 'line wall -subtype clay'])
        a, b = [o for o in objs if o.kind == 'line']
        self.assertEqual(a.segments()[-1][-2:], b.segments()[0][-2:])        # they meet

    def test_short_stretch_goes_with_its_neighbour(self):
        from tools.sketch2therion.smooth import wall_subtypes
        body = ("# wall-subtype clay: 0 0 400 0\n\n"
                "line wall\n  0 0\n  200 0\n  400 0\n  420 0\nendline\n")
        objs = parse_scrap(body)
        wall_subtypes(objs, 100.0)
        self.assertEqual([o.head for o in objs if o.kind == 'line'], ['line wall -subtype clay'])


class Scraps(unittest.TestCase):
    def test_stroke_drawn_on_goes_with_the_bigger_scrap(self):
        from tools.sketch2therion.convert import drawn_on
        a = [(0, 0), (5, 0)]
        b = [(5.1, 0), (12, 1)]
        lines = [('BLACK', a), ('BLACK', b)]
        out = drawn_on([(0, 'BLACK', list(a)), (1, 'BLACK', list(b))], lines, [20, 2])
        self.assertEqual([k for k, _, _ in out], [0, 0])     # the longer stroke joins the main scrap

    def test_glitch_cut_out(self):
        from tools.sketch2therion.convert import cut_glitches
        pp = [(0, 0), (1, 0), (1.5, 3), (2, 0), (3, 0)]
        out = cut_glitches([('BLACK', pp)], [[1.2, 1, 1.8, 4]])
        self.assertEqual([len(p) for _, p in out], [2, 2])
