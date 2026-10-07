import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import th2lint  # noqa: E402

HEAD = 'scrap ASP1 -projection plan -author 2026 "A N Other" -copyright 2026 "CC BY-NC-SA 4.0"\n'


def rules(body, head=HEAD):
    return [f.rule for f in th2lint.lint_text(head + body + "endscrap\n", "a.th2")]


# rule id -> (failing body, passing body), one tiny scrap each
CASES = {
    "scrap-author-copyright": None,     # tested on the scrap line below
    "end-on-node": None,                # needs a -scale: tested in EndOnNodeTest
    "wall-invisible": ("line wall -subtype invisible\n0 0\n1 1\nendline\n",
                       "line wall\n0 0\n1 1\nendline\n"),
    "wall-outline-none": ("line wall -outline none\n0 0\n1 1\nendline\n",
                          "line wall -outline in\n0 0\n1 1\nendline\n"),
    "clip-off-reason": ("line overhang -clip off\n0 0\n1 1\nendline\n",
                        "# overhang runs over the wall to the next scrap\nline overhang -clip off\n0 0\n1 1\nendline\n"),
    "climb-units": ("point 0 0 label -text [P5m] -scale s\n",
                    "point 0 0 label -text P5 -scale s\n"),
    "draught-date": ("point 0 0 air-draught -orientation 90\n",
                     "point 0 0 air-draught -orientation 90\npoint 5 0 date -value 2026.07.25\n"),
    "label-scale": ("point 0 0 label -text Tunnel -scale huge\n",
                    "point 0 0 label -text Tunnel -scale l\n"),
    "rock-closed": ("line rock-border\n0 0\n1 0\n0 1\nendline\n",
                    "line rock-border -close on\n0 0\n1 0\n0 1\n0 0\nendline\n"),
    "close-on-first-point": ("line rock-border -close on\n0 0\n1 0\n0 1\nendline\n",
                             "line rock-border -close on\n0 0\n1 0\n0 1\n0 0\nendline\n"),
    "rock-not-smooth": ("line rock-border -close on\n0 0\n0.3 0 0.7 0 1 0\n0 1\n0 0\nendline\n",
                        "line rock-border -close on\n0 0\n1 0\n0 1\n0 0\nendline\n"),
    "ceiling-step": ("line ceiling-step\n0 0\n1 1\nendline\n",
                     "line overhang\n0 0\n1 1\nendline\n"),
    "water-border": ("line border -id w1 -close on -subtype invisible\n0 0\n1 0\n0 1\n0 0\nendline\n"
                     "area water\nw2\nendarea\n",
                     "line border -id w1 -close on -subtype invisible\n0 0\n1 0\n0 1\n0 0\nendline\n"
                     "area water\nw1\nendarea\n"),
}


class RuleTest(unittest.TestCase):
    def test_each_rule_fails_and_passes(self):
        for rule, case in CASES.items():
            if case is None:
                continue
            bad, good = case
            with self.subTest(rule=rule):
                self.assertIn(rule, rules(bad))
                self.assertEqual(rules(good), [])

    def test_scrap_author_copyright(self):
        self.assertEqual(rules("", "scrap ASP1 -projection plan\n"), ["scrap-author-copyright"])
        self.assertEqual(rules("", 'scrap ASP1 -author 2026 "X"\n'), ["scrap-author-copyright"])
        self.assertEqual(rules(""), [])

    def test_empty_water_area(self):
        self.assertEqual(rules("area water\nendarea\n"), ["water-border"])

    def test_wall_subtype_written_with_colon(self):
        self.assertEqual(rules("line wall:invisible\n0 0\n1 1\nendline\n"), ["wall-invisible"])

    def test_every_check_has_a_case(self):
        self.assertEqual(set(CASES), set(th2lint.CHECKS))


class EndOnNodeTest(unittest.TestCase):
    # 100 units per metre
    SCALED = HEAD.replace("-projection plan", "-projection plan -scale [0 0 100 0 0.0 0.0 1 0 m]")
    WALL = "line wall\n0 0\n200 0\n400 0\nendline\n"

    def test_end_near_wall_not_on_node(self):
        self.assertEqual(rules(self.WALL + "line border\n150 100\n150 8\nendline\n", self.SCALED), ["end-on-node"])

    def test_end_on_node_passes(self):
        self.assertEqual(rules(self.WALL + "line border\n200 100\n200 0\nendline\n", self.SCALED), [])

    def test_far_from_wall_passes(self):
        self.assertEqual(rules(self.WALL + "line floor-step\n150 100\n150 50\nendline\n", self.SCALED), [])

    def test_no_scale_skipped(self):
        self.assertEqual(rules(self.WALL + "line border\n150 100\n150 10\nendline\n"), [])

    def test_scale(self):
        scrap = th2lint.parse(self.SCALED + "endscrap\n")[0]
        self.assertAlmostEqual(th2lint.scrap_scale(scrap), 100.0)


class StyleInStepTest(unittest.TestCase):
    def test_style_tags_match_checks(self):
        with open(th2lint.STYLE, encoding="utf-8") as f:
            tagged = th2lint.style_rules(f.read())
        self.assertEqual(tagged, set(th2lint.CHECKS),
                         "every [lint: id] in tools/Style.md needs a check in th2lint, and the reverse")


class BaselineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.baseline = os.path.join(self.root, "baseline.txt")
        self.write("old.th2", "scrap OldSP1\nline ceiling-step\n0 0\n1 1\nendline\nendscrap\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        with open(os.path.join(self.root, name), "w", encoding="utf-8") as f:
            f.write(text)

    def run_lint(self, *files, update=False):
        argv = list(files) + ["--root", self.root, "--baseline", self.baseline]
        return th2lint.main(argv + (["--update-baseline"] if update else []))

    def test_baselined_finding_does_not_fail(self):
        self.assertEqual(self.run_lint("old.th2"), 1)
        self.run_lint("old.th2", update=True)
        self.assertEqual(self.run_lint("old.th2"), 0)

    def test_new_finding_fails(self):
        self.run_lint("old.th2", update=True)
        self.write("new.th2", "scrap NewSP1\nendscrap\n")
        self.assertEqual(self.run_lint("old.th2", "new.th2"), 1)

    def test_baseline_survives_edits_elsewhere_in_the_file(self):
        self.run_lint("old.th2", update=True)
        self.write("old.th2", "\n\n# moved down\nscrap OldSP1\nline ceiling-step\n0 0\n1 1\nendline\nendscrap\n")
        self.assertEqual(self.run_lint("old.th2"), 0)

    def test_fixed_finding_reports_stale_entry(self):
        self.run_lint("old.th2", update=True)
        self.write("old.th2", 'scrap OldSP1 -author 2026 "X" -copyright 2026 "CC BY-NC-SA 4.0"\n'
                              "line overhang\n0 0\n1 1\nendline\nendscrap\n")
        from io import StringIO
        from contextlib import redirect_stdout
        out = StringIO()
        with redirect_stdout(out):
            self.assertEqual(self.run_lint("old.th2"), 0)
        self.assertIn("fixed, remove from baseline", out.getvalue())


if __name__ == "__main__":
    unittest.main()
