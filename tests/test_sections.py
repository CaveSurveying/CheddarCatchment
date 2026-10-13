"""Cross-sections keep the shape they were sketched (TridentLeft PX1, PX6,
PX10): an open stroke closed by a floor across its ends, small sections
not despiked to a sliver, and no section joined to another scrap."""

import math
import os
import unittest

try:
    from shapely.geometry import Polygon
    from tools.sketch2therion import settings, convert, smooth, scraps
    from tools.sketch2therion.tidy import bezier_points
except ImportError:          # shapely missing
    settings = None

K = 78.74016


def u_stroke(w=0.5, h=0.9, n=30):
    """Walls and roof of a small section, open at the bottom."""
    left = [(0.0, h * i / n) for i in range(n)]
    roof = [(w * i / n, h + 0.05 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    right = [(w, h * (n - i) / n) for i in range(1, n + 1)]
    return left + roof + right


def pebble(x, y, r=0.03):
    pts = [(x + r * math.cos(2 * math.pi * i / 10), y + r * math.sin(2 * math.pi * i / 10)) for i in range(10)]
    return pts + [pts[0]]


@unittest.skipUnless(settings, "needs shapely")
class SectionShape(unittest.TestCase):
    def setUp(self):
        settings.load()

    def tearDown(self):
        settings.load()

    def test_open_stroke_closed_by_a_floor(self):
        u = u_stroke()
        floor = convert.drawn_floor([u] + [pebble(0.1 * k, 0.0) for k in range(1, 5)], (0.25, 0.45))
        self.assertIsNotNone(floor)
        poly, (a, b), sub = floor
        self.assertEqual((a, b), (u[0], u[-1]))
        self.assertEqual(sub, 'debris')                     # pebbles on it
        self.assertGreater(poly.area, 0.4)                  # the whole section, about 0.5 x 0.9 m

    def test_floor_without_marks_is_plain_wall(self):
        self.assertIsNone(convert.drawn_floor([u_stroke()], (0.25, 0.45))[2])

    def test_closed_or_wide_open_strokes_not_floored(self):
        u = u_stroke()
        self.assertIsNone(convert.drawn_floor([u + [u[0]]], (0.25, 0.45)))     # closed already
        self.assertIsNone(convert.drawn_floor([u[20:-20]], (0.25, 0.45)))      # an arch, not a section

    def test_section_written_with_its_floor(self):
        lines = [('BLACK', u_stroke())] + [('BROWN', pebble(0.1 * k, 0.0)) for k in range(1, 5)]
        o = convert.section_th2('XPX1', '', lines, (0.25, 0.45), K, '# test')[0]
        heads = [l for l in o if l.startswith('line ')]
        self.assertEqual(heads, ['line wall', 'line wall -subtype debris'])

    def test_small_section_not_despiked_to_a_sliver(self):
        lines = [('BLACK', u_stroke())] + [('BROWN', pebble(0.1 * k, 0.0)) for k in range(1, 5)]
        o = convert.section_th2('XPX1', '', lines, (0.25, 0.45), K, '# test')[0]
        header = 'scrap XPX1 -projection none -scale [0 0 787.40 787.40 0.0 0.0 10 10 m]'
        objs = smooth._redo_scrap(header, '\n'.join(o[1:o.index('endscrap')]) + '\n', 'x.th2')[0]
        before, _ = smooth._shape(smooth.parse_scrap('\n'.join(o[1:o.index('endscrap')]) + '\n'), True)
        after, _ = smooth._shape(objs, True)
        self.assertGreater(after['outline'], 0.9 * before['outline'])

    def test_section_joins_no_other_scrap(self):
        text = "\n".join([
            "scrap XSP1 -projection plan", "line wall", "  0 0", "  100 0", "endline", "endscrap",
            "scrap XPX1 -projection none", "line wall", "  50 3", "  50 60", "  80 60", "endline", "endscrap", ""])
        self.assertEqual(scraps.meet_on_walls(text, 10), text)
        self.assertEqual(scraps.meet_ends(text, 10), text)


if __name__ == "__main__":
    unittest.main()
