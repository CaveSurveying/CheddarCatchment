"""Style.md rules the converter keeps: section arrows, no `-outline none`,
and the legs and splays check against the fill (log rows 121 to 123)."""
import math
import os
import tempfile
import unittest

from tools.sketch2therion import convert, fillcheck, settings, smooth
from tools.sketch2therion.tidy import parse_scrap


class Geo:
    """Two legs north from 1, splays 1 m either side."""
    def __init__(self):
        self.pos = {'1': (0.0, 0.0), '2': (0.0, 5.0), '3': (0.0, 10.0)}
        self.legs = [('1', '2'), ('2', '3')]
        self.splays = {n: [(1.0, 0.0), (-1.0, 0.0)] for n in self.pos}

    def half_width(self, n, perp):
        return 1.0


class SectionArrows(unittest.TestCase):
    def setUp(self):
        settings.load()

    def tearDown(self):
        settings.load()

    def lines(self, n):
        g = Geo()
        g.direction = lambda m: (0.0, -1.0)          # the passage's direction, either way round
        rows, _, _ = convert.section_line(g, n, lambda p: p)
        a = tuple(map(float, rows[1].split()))
        b = tuple(map(float, rows[2].split()))
        return rows[0], a, b

    def test_arrows_both_with_the_view_on_the_left(self):
        settings.SETTINGS['section_arrows'] = True
        for n in ('1', '2', '3'):                  # 3 has no next station: on from 2
            head, a, b = self.lines(n)
            self.assertEqual(head, "line section -direction both")
            d = (b[0] - a[0], b[1] - a[1])
            left = (-d[1], d[0])
            self.assertGreater(left[1], 0, n)      # the view (north, along the survey) on the line's left
            self.assertAlmostEqual(math.dist(a, b), 2 * (1.0 + convert.SECTION_MARGIN))

    def test_upstream_has_no_arrows(self):
        settings.SETTINGS['section_arrows'] = False
        head, a, b = self.lines('2')
        self.assertEqual(head, "line section")


SCRAP = """scrap s -projection plan -scale [0 0 100 0 0 0 1 0 m]
line wall
  0 0
  1000 0
endline
line wall
  1000 0
  1000 500
endline
line wall
  1000 500
  0 500
endline
line wall
  0 500
  0 0
endline
line wall -outline none
  200 250
  800 250
endline
endscrap
"""


class NoOutlineNone(unittest.TestCase):
    def test_none_left(self):
        objs = parse_scrap(SCRAP.split('\n', 1)[1].rsplit('endscrap', 1)[0])
        n = smooth.no_outline_none(objs, 100)
        self.assertEqual(n, 1)
        heads = [o.head for o in objs if o.kind == 'line']
        self.assertFalse(any('-outline none' in h for h in heads))
        self.assertEqual(sum(h.startswith('line wall') for h in heads), 4)
        self.assertEqual(heads.count('line border'), 1)      # inside the passage: the edge of something


class FillCheck(unittest.TestCase):
    def test_xvi_read_and_survey_names(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'x.xvi')
            open(p, 'w').write("set XVIgrids {1.0 m}\nset XVIstations {\n  {   0.00   0.00 1@A.Cave}\n"
                               "  {  19.69   0.00 2@A.Cave}\n}\nset XVIshots {\n"
                               "  {   0.00   0.00  19.69   0.00}\n  {   0.00   0.00   0.00  39.37}\n}\n"
                               "set XVIgrid  {-10 -10 19.685 0.0 0.0 19.685 2 2}\n")
            scale, st, shots = fillcheck.read_xvi(p)
        self.assertAlmostEqual(scale, 19.685)
        self.assertEqual(st['2@A.Cave'], (19.69, 0.0))
        self.assertEqual(len(shots), 2)
        self.assertEqual(fillcheck._survey('2@A.Cave'), 'A')


if __name__ == '__main__':
    unittest.main()


class AutoScraps(unittest.TestCase):
    """autoscraps.choose: cuts on simple passage, balanced, at least two stations."""

    def setUp(self):
        from collections import defaultdict
        from tools.sketch2therion import autoscraps
        self.a = autoscraps
        # a passage 1..9 with a side branch at 5 (5-10, 10-11)
        self.legs = [(str(i), str(i + 1)) for i in range(1, 9)] + [('5', '10'), ('10', '11')]
        self.length = {l: 1.0 for l in self.legs}
        self.degree = defaultdict(int)
        for x, y in self.legs:
            self.degree[x] += 1
            self.degree[y] += 1

    def test_cut_not_at_a_junction_and_balanced(self):
        clash = [(('1', '2'), ('8', '9'), 0.9)]
        cut, comps, left = self.a.choose(self.legs, clash, self.length, self.degree, 'plan')
        self.assertFalse(left)
        self.assertEqual(len(cut), 1)
        (x, y), = cut
        self.assertTrue(self.degree[x] <= 2 and self.degree[y] <= 2)      # plans: never at the junction at 5
        self.assertTrue(all(len({n for l in c for n in l}) >= 2 for c in comps))

    def test_elevation_cut_by_the_junction(self):
        clash = [(('1', '2'), ('8', '9'), 0.9)]
        cut, comps, left = self.a.choose(self.legs, clash, self.length, self.degree, 'extended')
        self.assertFalse(left)
        (x, y), = cut
        self.assertTrue(self.degree[x] > 2 or self.degree[y] > 2
                        or any(self.degree[n] > 2 for l in self.legs if set(l) & {x, y} for n in l))

    def test_no_clash_one_scrap(self):
        cut, comps, left = self.a.choose(self.legs, [], self.length, self.degree)
        self.assertEqual((cut, len(comps)), (set(), 1))
