"""Profile runs joined end to end (sketch2therion unfold --ee)."""

import unittest

try:
    from tools.sketch2therion import unfold
except ImportError:          # shapely missing
    unfold = None


@unittest.skipUnless(unfold, "needs shapely")
class Joined(unittest.TestCase):
    def test_runs_meeting_become_one_line(self):
        runs = [[(0, 0), (1, 0)], [(1.2, 0), (2, 0)], [(5, 5), (6, 5)]]
        out = unfold._joined(runs, ['a', 'b', 'c'])
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0], ('a', [(0, 0), (1, 0), (2, 0)]))

    def test_a_run_reversed_to_join(self):
        out = unfold._joined([[(0, 0), (1, 0)], [(2, 0), (1.1, 0)]], ['a', 'b'])
        self.assertEqual(out, [('a', [(0, 0), (1, 0), (2, 0)])])


if __name__ == "__main__":
    unittest.main()
