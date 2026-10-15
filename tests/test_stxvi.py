"""An old SexyTopo plan xvi gets its cross sections linked to the plan
(sketch2therion stxvi), so the converter finds them."""

import unittest

from tools.sketch2therion import stxvi, xvi

XVI = """set XVIgrids {1 m}
set XVIstations {
\t {0.00 0.00 1}
\t {100.00 0.00 2}
}
set XVIshots {
\t {0.00 0.00 100.00 0.00}
}
set XVIsketchlines {
\t {BLACK 0.00 10.00 100.00 10.00}
}
set XVIgrid {-100.0 -100.0 100.0 0.0 0.0 100.0 3.0 3.0}
"""
PLAN = {"x-sections": [{"station-id": "2", "location": {"x": 1.0, "y": -2.0}, "angle": 90.0}]}
DATA = {"stations": [{"name": "2", "legs": [
    {"distance": 1.0, "azimuth": 0.0, "inclination": 0.0, "destination": "-"},
    {"distance": 2.0, "azimuth": 0.0, "inclination": 90.0, "destination": "-"},
    {"distance": 5.0, "azimuth": 90.0, "inclination": 0.0, "destination": "3"}]}]}


class Relink(unittest.TestCase):
    def test_connect_station_and_splays_added(self, tmp="/tmp"):
        out, n = stxvi.relink(XVI, PLAN, DATA)
        self.assertEqual(n, 1)
        self.assertIn("{connect 100.00 0.00 100.00 200.00}", out)
        self.assertIn("{100.00 200.00 2}", out)
        # a level splay north, with the section facing east (90), is seen to its left (x -1 m);
        # one straight up is 2 m up the drawing
        self.assertIn("{100.00 200.00 0.00 200.00}", out)
        self.assertIn("{100.00 200.00 100.00 400.00}", out)

    def test_already_linked_left_alone(self):
        once, _ = stxvi.relink(XVI, PLAN, DATA)
        twice, n = stxvi.relink(once, PLAN, DATA)
        self.assertIs(twice, once)
        self.assertEqual(n, 0)


if __name__ == "__main__":
    unittest.main()
