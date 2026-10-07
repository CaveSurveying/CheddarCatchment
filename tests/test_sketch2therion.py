"""tools/sketch2therion, as ported from the Swildons survey."""

import contextlib
import glob
import io
import os
import re
import shutil
import tempfile
import unittest

from tools import project
from tools import th2lint

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAVE = os.path.join(REPO, "LongwoodValleySink")
FIXTURES = os.path.join(REPO, "tests", "fixtures", "sketch2therion", "upstream-198bf46")

try:
    import shapely  # noqa: F401
    HAVE_SHAPELY = True
except ImportError:
    HAVE_SHAPELY = False


def normalise(text):
    """What may differ from upstream: line endings, licence line, backdrop path."""
    text = text.replace("\r\n", "\n")
    text = re.sub(r"^# Licence: .*\n", "", text, flags=re.M)
    return re.sub(r"^##XTHERION## xth_me_image_insert .*\n", "", text, flags=re.M)


@unittest.skipUnless(HAVE_SHAPELY, "needs shapely")
class ConverterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def run_cli(self, *args):
        from tools.sketch2therion.__main__ import main
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            main(list(args) + ["--layout", os.path.join(self.tmp, "no-layout.xvi")])
        return out.getvalue()

    def sketch(self, survey, name):
        return os.path.join(CAVE, survey, "Notes", name)

    def read(self, path):
        with open(path, "rb") as f:
            return f.read().decode("utf-8")

    def upstream(self):
        """The Swildons converter's settings, for comparing with its output."""
        from tools.sketch2therion import settings
        settings.use({})
        self.addCleanup(settings.load)

    def compare(self, fixture, output):
        self.assertEqual(normalise(self.read(output)), normalise(self.read(os.path.join(FIXTURES, fixture))))

    def test_plan_same_as_upstream(self):
        self.upstream()
        out = os.path.join(self.tmp, "GoSouth-plan.th2")
        self.run_cli("plan", self.sketch("GoSouth", "GoSouthP.xvi"), "--floor", self.sketch("GoSouth", "GoSouthE.xvi"),
                     "-o", out, "--survey", "GoSouth", "--name", "GoSouthS",
                     "--author", "2026.04.25", "Andrew Atkinson", "--copyright", "2026", "CC BY-NC-SA 4.0")
        self.compare("GoSouth-plan.th2", out)

    def test_plan_with_cross_section_same_as_upstream(self):
        self.upstream()
        out = os.path.join(self.tmp, "Trident-plan.th2")
        self.run_cli("plan", self.sketch("Trident", "TridentP.xvi"), "-o", out, "--survey", "Trident",
                     "--name", "TridentS", "--author", "2026.06.13", "Andrew Atkinson",
                     "--copyright", "2026", "CC BY-NC-SA 4.0")
        self.compare("Trident-plan.th2", out)

    def test_extended_same_as_upstream(self):
        self.upstream()
        out = os.path.join(self.tmp, "GoSouth-ext.th2")
        self.run_cli("extended", self.sketch("GoSouth", "GoSouthE.xvi"), "-o", out, "--survey", "GoSouth",
                     "--name", "GoSouthS")
        self.compare("GoSouth-ext.th2", out)

    def test_house_style_defaults(self):
        out = os.path.join(self.tmp, "GoSouth.plan.th2")
        printed = self.run_cli("plan", self.sketch("GoSouth", "GoSouthP.xvi"), "-o", out, "--survey", "GoSouth",
                               "--author", "2026.04.25", "Andrew Atkinson", "--copyright", "2026", "CC BY-NC-SA 4.0")
        raw = open(out, "rb").read()
        self.assertNotIn(b"\r\n", raw)                                  # project.toml: lf
        text = raw.decode()
        self.assertIn("# Licence: CC BY-NC-SA 4.0", text)
        self.assertNotIn("General Public License", text)
        self.assertRegex(text, r"(?m)^scrap GoSouthSP1 -projection plan -author 2026.04.25 \"Andrew Atkinson\" "
                               r"-copyright 2026 \"CC BY-NC-SA 4.0\"")
        self.assertIn("Add to `map GoSouthMP` in LongwoodValleySink/GoSouth/GoSouth.th", printed)
        self.assertIn("GoSouthMP@GoSouth to LongwoodValleySinkMP in LongwoodValleySink/LongwoodValleySink.th", printed)

    def test_output_rules_th2lint_checks(self):
        # plan then smooth (which puts line ends on wall nodes): every rule
        # but wall-outline-none, an open question (docs/lvs-phase5-log.md).
        from tools.sketch2therion import smooth
        out = os.path.join(self.tmp, "t.th2")
        self.run_cli("plan", self.sketch("Trident", "TridentP.xvi"), "-o", out, "--survey", "Trident",
                     "--author", "2026.06.13", "Andrew Atkinson", "--copyright", "2026", "CC BY-NC-SA 4.0")
        smooth.redo_file(out)
        findings = [f for f in th2lint.lint_text(self.read(out), "t.th2") if f.rule != "wall-outline-none"]
        self.assertEqual(findings, [])

    def test_outline_valid_with_passage_on_left(self):
        # The walls joined as Therion joins them: a valid outline, going
        # anticlockwise round the passage (positive area), so the passage
        # is on the walls' left.
        from tools.sketch2therion import review, tidy
        out = os.path.join(self.tmp, "t.th2")
        self.run_cli("plan", self.sketch("GoSouth", "GoSouthP.xvi"), "-o", out, "--survey", "GoSouth")
        results = review.check(out)
        self.assertTrue(results)
        self.assertTrue(all(ok for _, _, ok, _ in results))
        text = self.read(out)
        body = re.search(r"(?ms)^scrap GoSouthSP1[^\n]*\n(.*?)^endscrap", text).group(1)
        lines = review.outline_lines(tidy.parse_scrap(body))
        pts_of = [tidy.bezier_points(o.segments(), 20) for o in lines]
        for ring in tidy.therion_rings(pts_of):
            pts = [p for i, r in ring for p in (pts_of[i][::-1] if r else pts_of[i])]
            area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1])) / 2
            self.assertGreater(area, 0)


@unittest.skipUnless(HAVE_SHAPELY, "needs shapely")
class XviTest(unittest.TestCase):
    def test_reads_sexytopo_sketch(self):
        from tools.sketch2therion import xvi
        sk = xvi.read(os.path.join(CAVE, "GoSouth", "Notes", "GoSouthP.xvi"))
        self.assertEqual(len(sk.positions()), 28)
        self.assertEqual(len(sk.legs()), 27)
        self.assertEqual(len(sk.splays()), 205)
        colours = {c for c, _ in sk.lines}
        self.assertTrue({"BLACK", "BROWN", "GRAY", "GREEN", "BLUE"} <= colours)


class SurveyTest(unittest.TestCase):
    def test_survey_of(self):
        from tools.sketch2therion.survey import survey_of
        self.assertEqual(survey_of(os.path.join(CAVE, "Cyclops", "Cyclops.plan.th2")), "Cyclops")   # quoted input
        self.assertEqual(survey_of(os.path.join(CAVE, "Cyclops", "CyclopsE315.th2")), "Cyclops")    # bare input
        self.assertEqual(survey_of(os.path.join(CAVE, "BoldStep", "BoldStepP.th2")), "BoldStep")
        self.assertIsNone(survey_of(os.path.join(CAVE, "GoSouth", "Nothing.th2")))

    def test_fit(self):
        from tools.sketch2therion.survey import fit
        f = fit([((0, 0), (10, 10)), ((1, 0), (10, 12)), ((0, 1), (8, 10))])   # x2, turned 90°
        self.assertEqual(tuple(round(v, 6) for v in f((1, 1))), (8.0, 12.0))
        self.assertIsNone(fit([((1, 1), (0, 0)), ((1, 1), (2, 2))]))


class SqlTest(unittest.TestCase):
    def test_nan_becomes_null(self):
        try:
            from tools.sketch2therion.roofs import sql_text
        except ImportError:
            self.skipTest("needs shapely")
        self.assertEqual(sql_text("insert into MAPS values (1, 2, 'XME090', NULL, 5, 0.000, nan);"),
                         "insert into MAPS values (1, 2, 'XME090', NULL, 5, 0.000, NULL);")
        self.assertEqual(sql_text("insert into SURVEY values (3, 'nancy');"), "insert into SURVEY values (3, 'nancy');")


class NoSwildonsNamesTest(unittest.TestCase):
    def test_no_swildons_names_left(self):
        files = glob.glob(os.path.join(REPO, "tools", "sketch2therion", "*.py")) + \
            glob.glob(os.path.join(REPO, "tools", "web", "*.py"))
        for path in files:
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
            for n, line in enumerate(lines, 1):
                if "caves-mendip-swildons" in line or "Swildons version" in line or "Swildons survey" in line:
                    continue        # origin notes
                self.assertNotRegex(line, r"(?i)swil|sump1|stanton|footleg|waterworth", f"{path}:{n}")

    def test_sections_not_ported(self):
        self.assertFalse(os.path.exists(os.path.join(REPO, "tools", "sketch2therion", "sections.py")))

    def test_files_say_where_from(self):
        for path in glob.glob(os.path.join(REPO, "tools", "sketch2therion", "*.py")):
            with open(path, encoding="utf-8") as f:
                head = f.read(300)
            self.assertTrue("caves-mendip-swildons" in head or "new for the Cheddar Catchment survey" in head, path)
            self.assertIn("GPLv3", head, path)


if __name__ == "__main__":
    unittest.main()
