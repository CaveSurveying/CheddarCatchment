"""The layout config, the trip template, the CI workflow and the pointer docs."""

import os
import re
import unittest

from tools import project
from tools.svn2git import deps, inventory

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return f.read()


def active(text):
    return [l.strip() for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]


class LayoutTest(unittest.TestCase):
    def test_reaches_only_files_that_exist(self):
        result = deps.walk(REPO, "tools/layout.thcfg")
        self.assertEqual(result.problems, [])
        self.assertIn("LongwoodValleySink/LongwoodValleySink.th", result.files)

    def test_exports_what_project_toml_says(self):
        p = project.load()
        exports = [l for l in active(read("tools/layout.thcfg")) if l.startswith("export")]
        outs = [os.path.normpath(os.path.join("tools", l.split("-o ")[1])) for l in exports]
        self.assertEqual(outs, [p.build["layout_plan"], p.build["layout_extended"], p.build["sql"]])
        self.assertIn("-fmt sql", exports[2])

    def test_name_follows_thcfg_convention(self):
        self.assertFalse(os.path.exists(os.path.join(REPO, "tools", "layout.thconfig")))


class TemplateTest(unittest.TestCase):
    def test_house_style(self):
        text = read("tools/new-trip-template.th")
        s = inventory.parse_th(text, "tools/new-trip-template.th")
        self.assertEqual(s.name, "NewTrip")
        self.assertTrue(s.dates)
        self.assertGreater(s.length, 0)
        self.assertIn('copyright 2026 "CC BY-NC-SA 4.0"', text)
        self.assertIn('NewTrip.plan.th2', text)
        self.assertIn("NewTripSP1", text)
        self.assertIn("map NewTripMP", text)
        # Nothing it inputs is live until the drawing exists.
        self.assertEqual([i for i, commented in s.inputs if not commented], [])


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.text = read(".github/workflows/build.yml")

    def test_builds_plan_only(self):
        runs = re.findall(r"therion (\S+) -l (\S+) (\S+\.thcfg)", self.text)
        self.assertEqual(runs, [("LongwoodValleySink", "../output/therion.log", "Plan_only.thcfg"),
                                (".", "output/therion-layout.log", "tools/layout.thcfg")])
        self.assertNotRegex(self.text, r"(?m)^\s*therion [^\n]*\bthconfig\b")

    def test_image_pinned_by_digest(self):
        self.assertRegex(self.text, r"THERION_IMAGE: ghcr\.io/paperclipmonkey/therion@sha256:[0-9a-f]{64}\n")
        self.assertNotRegex(self.text, r"therion:\d")

    def test_nothing_published(self):
        for word in ("pages:", "deploy-pages", "upload-pages-artifact", "id-token"):
            self.assertNotIn(word, self.text)

    def test_error_gate_reads_the_logs_written(self):
        self.assertIn("for log in output/therion.log output/therion-layout.log", self.text)
        self.assertIn('grep -qE "^therion: error|invalid scrap outline"', self.text)

    def test_runs_tests_and_lint(self):
        self.assertIn("python -m pytest -q tests", self.text)
        self.assertIn("tools/th2lint.py --from LongwoodValleySink/Plan_only.thcfg", self.text)


class PointerDocsTest(unittest.TestCase):
    def test_paths_they_name_exist(self):
        for doc in ["AGENTS.md", ".claude/skills/therion-drawing/SKILL.md", "README.md", "tools/README.md"]:
            text = read(doc)
            for path in re.findall(r"`((?:tools|docs|LongwoodValleySink|tests|\.github|\.claude)/[^`\s*]+)`", text):
                path = path.rstrip("/")
                if re.search(r"(^|/)X(/|$)", path) or "<" in path:
                    continue        # placeholders such as LongwoodValleySink/X/X.th
                self.assertTrue(os.path.exists(os.path.join(REPO, path)), f"{doc}: {path}")

    def test_skill_does_not_copy_style(self):
        skill = read(".claude/skills/therion-drawing/SKILL.md")
        self.assertIn("tools/Style.md", skill)
        self.assertNotIn("[lint", skill)
        self.assertLess(len(skill.splitlines()), 40)


if __name__ == "__main__":
    unittest.main()
