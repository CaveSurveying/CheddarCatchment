"""tools/sketch2therion review on this cave's Plan_only.thcfg (the rest is tested in Therion-Sketching)."""

import os
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import numpy  # noqa: F401
    from tools.sketch2therion import review
except ImportError:
    review = None


@unittest.skipUnless(review, "needs shapely and numpy")
class ReviewConfigTest(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(REPO, "LongwoodValleySink", "Plan_only.thcfg"), encoding="utf-8") as f:
            self.cfg = f.read()

    def test_review_config(self):
        s = review.review_config(self.cfg, "/out/review-plan.pdf")
        exports = [l.strip() for l in s.splitlines() if l.strip().startswith("export")]
        self.assertEqual(exports, ["export map -projection plan -layout review-names -o /out/review-plan.pdf"])
        self.assertIn("layout review-names\n  copy plan\n  debug station-names\n", s)
        self.assertIn("  symbol-show group cave-centreline\n", s)
        self.assertIn("input ../common_layout.th", s)

    def test_sheet_scale_rotation(self):
        cfg = review.config_with_inputs(os.path.join(REPO, "LongwoodValleySink", "Plan_only.thcfg"))
        self.assertEqual(review.sheet_scale_rotation(cfg), (500.0, 45.0))
        self.assertEqual(review.sheet_scale_rotation("layout x\nendlayout\n"), (500.0, 0.0))

    def test_select_and_layout(self):
        s = review.review_config(self.cfg, "/o.pdf", review.survey_map("GoSouth"), names=False)
        lines = [l.strip() for l in s.splitlines()]
        self.assertEqual([l for l in lines if l.startswith("select")], ["select GoSouthMP@GoSouth.LongwoodValleySink"])
        self.assertIn("export map -projection plan -layout review-one -o /o.pdf", lines)
        self.assertIn("legend off", lines)
        self.assertIn("\\def\\maplayout{}", lines)


if __name__ == "__main__":
    unittest.main()
