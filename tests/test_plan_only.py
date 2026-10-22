"""LongwoodValleySink/Plan_only.thcfg: the plan-only trial build."""

import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAVE = os.path.join(REPO, "LongwoodValleySink")
PLAN_ONLY = os.path.join(CAVE, "Plan_only.thcfg")
THCONFIG = os.path.join(CAVE, "thconfig")
LAYOUTS = os.path.join(CAVE, "Layouts.th")
LICENCE = "CC BY-NC-SA 4.0"


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def active(text):
    """Lines that are not # comments."""
    return [l for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]


def layout(text, name):
    m = re.search(rf"^layout {name}\n.*?^endlayout\n", text, re.S | re.M)
    return m.group(0) if m else None


class PlanOnlyTest(unittest.TestCase):
    def setUp(self):
        self.text = read(PLAN_ONLY)

    def test_one_export_the_plan(self):
        exports = [l.split() for l in active(self.text) if l.split()[0] == "export"]
        self.assertEqual(len(exports), 1)
        e = exports[0]
        self.assertEqual(e[:2], ["export", "map"])
        self.assertEqual(e[e.index("-proj") + 1], "plan")
        self.assertEqual(e[e.index("-layout") + 1], "plan")

    def test_selects_no_elevation(self):
        selects = [l for l in active(self.text) if l.split()[0] == "select"]
        self.assertEqual([s.split()[1] for s in selects], ["LongwoodValleySinkMP@LongwoodValleySink"])

    def test_no_loadpicture(self):
        # no elevation is built here, so the plan layout can't place one
        tex = "\n".join(l.split("%", 1)[0] for l in active(self.text + read(LAYOUTS)))
        self.assertNotIn("\\loadpicture", tex)

    def test_map_comment_has_the_data_licence(self):
        plan = layout(read(LAYOUTS), "plan")
        self.assertIsNotNone(plan)
        m = re.search(r'^map-comment "(.*?)"\n', plan, re.S | re.M)
        self.assertIsNotNone(m, "plan layout has a map-comment")
        self.assertIn(LICENCE, m.group(1))

    def test_style_gives_the_same_licence(self):
        self.assertIn(LICENCE, read(os.path.join(REPO, "tools", "Style.md")))

    def test_uses_common_layout(self):
        self.assertIn("input ../common_layout.th", active(self.text))

    def test_name_follows_thcfg_convention(self):
        self.assertTrue(PLAN_ONLY.endswith(".thcfg"))

    def test_layouts_shared_with_thconfig(self):
        for text in (self.text, read(THCONFIG)):
            self.assertIn("input Layouts.th", active(text))
            self.assertNotRegex(text, r"(?m)^layout ")


if __name__ == "__main__":
    unittest.main()
