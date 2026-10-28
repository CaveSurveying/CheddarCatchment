"""Inventory of a cave's surveys and the state of their plan drawings.

For every survey `.th` under the cave folder: its dates, team, leg
length, and whether its plan is drawn, input and in the plan map.
Writes Markdown listing the surveys of a given year whose plans are
still to be drawn.

A plan is "undrawn" if the survey has no plan `.th2`, or its plan scraps
have no `line wall` (SexyTopo's export). A drawn plan that is not
`input`, or whose scraps are in no plan map, is reported but not listed
for drawing: some inputs are commented out on purpose.

    python3 -m tools.svn2git.inventory ROOT LongwoodValleySink --year 2026 -o docs/lvs-inventory.md
"""

import argparse
import datetime
import os
import re
import sys
from dataclasses import dataclass, field

DATE = re.compile(r"(\d{4})\.(\d{1,2})(?:\.(\d{1,2}))?")
INPUT = re.compile(r'^(\s*#?\s*)input\s+(?:"([^"]+)"|(\S+))', re.IGNORECASE)
LENGTH_COLUMNS = ("length", "tape")
SPLAY_NAMES = {"-", "."}
FEET = 0.3048


@dataclass
class Scrap:
    id: str
    projection: str
    has_wall: bool


@dataclass
class Th2:
    path: str
    scraps: list = field(default_factory=list)
    images: list = field(default_factory=list)      # xvi files referenced by xTherion


@dataclass
class Survey:
    path: str
    name: str = ""
    namespace_off: bool = False     # `survey X -namespace off`
    dates: list = field(default_factory=list)       # datetime.date, centreline `date` only
    team: list = field(default_factory=list)
    length: float = 0.0
    inputs: list = field(default_factory=list)      # (target, commented)
    maps: dict = field(default_factory=dict)        # map id -> members
    th2: list = field(default_factory=list)
    status: str = ""
    note: str = ""


def strip_comment(line):
    """A Therion line without its `#` comment (quotes respected)."""
    out, quoted = [], False
    for ch in line:
        if ch == '"':
            quoted = not quoted
        if ch == "#" and not quoted:
            break
        out.append(ch)
    return "".join(out).strip()


def parse_dates(value):
    """Dates in a Therion date value: one date, a range `a - b`, or several."""
    dates = []
    for m in DATE.finditer(value):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3) or 1)
        try:
            dates.append(datetime.date(y, mo, d))
        except ValueError:
            pass
    return dates


def parse_maps(text):
    """{map id: [member ids]} from `map ... endmap` blocks; `@survey` kept."""
    maps, current = {}, None
    for raw in text.splitlines():
        line = strip_comment(raw)
        if not line:
            continue
        words = line.split()
        if words[0] == "map" and len(words) > 1:
            current = words[1]
            maps[current] = []
        elif words[0] == "endmap":
            current = None
        elif current is not None and words[0] not in ("break", "preview"):
            maps[current].append(words[0])
    return maps


def parse_th(text, path=""):
    """A Survey from the text of a `.th` file."""
    s = Survey(path)
    columns, units = [], 1.0
    for raw in text.splitlines():
        m = INPUT.match(raw)
        if m:
            s.inputs.append((m.group(2) or m.group(3), "#" in m.group(1)))
            continue
        line = strip_comment(raw)
        if not line:
            continue
        words = line.split()
        key = words[0].lower()
        if key == "survey" and len(words) > 1 and not s.name:
            s.name = words[1]
            opts = [w.lower() for w in words[2:]]
            s.namespace_off = "-namespace" in opts and opts[opts.index("-namespace") + 1:][:1] == ["off"]
        elif key == "date":
            s.dates.extend(parse_dates(line[4:]))
        elif key == "team":
            m = re.match(r'team\s+"([^"]+)"', line) or re.match(r"team\s+(\S+)", line)
            if m and m.group(1).strip() not in s.team:
                s.team.append(m.group(1).strip())
        elif key == "units":
            if any(w in ("length", "tape") for w in words) and any(w.startswith(("feet", "foot", "ft")) for w in words):
                units = FEET
            elif any(w in ("length", "tape") for w in words):
                units = 1.0
        elif key == "data":
            columns = words[2:] if len(words) > 2 and words[1] == "normal" else []
        elif key in ("centreline", "centerline", "endcentreline", "endcenterline"):
            columns = [] if key.startswith("end") else columns
        elif columns and len(words) >= len([c for c in columns if c != "ignoreall"]):
            s.length += leg_length(words, columns) * units
    s.maps = parse_maps(text)
    return s


def leg_length(words, columns):
    """The length of one data line, or 0 for a splay or a non-leg line."""
    try:
        frm, to = words[columns.index("from")], words[columns.index("to")]
        col = next(c for c in LENGTH_COLUMNS if c in columns)
        value = float(words[columns.index(col)])
    except (ValueError, StopIteration, IndexError):
        return 0.0
    if frm in SPLAY_NAMES or to in SPLAY_NAMES:
        return 0.0
    return value


def parse_th2(text, path=""):
    """A Th2 with its scraps and whether each has a `line wall`."""
    t = Th2(path)
    current = None
    for raw in text.splitlines():
        if raw.startswith("##XTHERION## xth_me_image_insert"):
            m = re.search(r'"([^"]+\.xvi)"|\s(\S+\.xvi)\s', raw)
            if m:
                t.images.append(m.group(1) or m.group(2))
            continue
        line = strip_comment(raw)
        words = line.split()
        if not words:
            continue
        if words[0] == "scrap" and len(words) > 1:
            proj = "plan"
            if "-projection" in words:
                proj = words[words.index("-projection") + 1].strip("[]")
            current = Scrap(words[1], proj, False)
            t.scraps.append(current)
        elif words[0] == "endscrap":
            current = None
        elif current is not None and words[0] == "line" and len(words) > 1 and words[1].split(":")[0] == "wall":
            current.has_wall = True
    return t


def qualify(member, namespace):
    """`X@S` as written, else `X@namespace` (or bare `X` at the top level)."""
    if "@" in member or not namespace:
        return member
    return f"{member}@{namespace}"


def map_closure(maps, top):
    """Every id reachable from map `top`, as bare ids (namespace dropped).

    `maps` is keyed by qualified id (`CyclopsMP@Cyclops`, or `CyclopsMP`
    for a map in the master survey); members are resolved in the
    namespace of the map that lists them.
    """
    seen, out, todo = set(), set(), [top]
    while todo:
        cur = todo.pop()
        if cur in seen:
            continue
        seen.add(cur)
        out.add(cur.split("@")[0])
        namespace = cur.split("@", 1)[1] if "@" in cur else ""
        todo.extend(qualify(m, namespace) for m in maps.get(cur, []))
    return out


def classify(survey, in_plan_map):
    """Set survey.status and survey.note."""
    plan_th2 = [t for t in survey.th2 if any(sc.projection == "plan" for sc in t.scraps)]
    plan_scraps = [sc for t in plan_th2 for sc in t.scraps if sc.projection == "plan"]
    input_names = {os.path.normcase(tg): commented for tg, commented in survey.inputs}
    if not plan_scraps:
        survey.status, survey.note = "undrawn", "no plan .th2"
    elif not any(sc.has_wall for sc in plan_scraps):
        survey.status, survey.note = "undrawn", "plan scraps have no line wall"
    else:
        drawn = [t for t in plan_th2 if any(sc.has_wall for sc in t.scraps)]
        not_input = [t for t in drawn
                     if input_names.get(os.path.normcase(os.path.basename(t.path)), True)]
        unmapped = [sc.id for sc in plan_scraps if sc.has_wall and sc.id not in in_plan_map]
        notes = []
        if not_input:
            notes.append("not input: " + ", ".join(os.path.basename(t.path) for t in not_input))
        if unmapped:
            notes.append("in no plan map: " + ", ".join(unmapped))
        survey.status = "drawn" if not notes else "drawn, reported"
        survey.note = "; ".join(notes)
    return survey


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def inventory(root, cave, master=None, plan_map=None):
    """Surveys under root/cave, classified."""
    cave_dir = os.path.join(root, cave)
    master = master or f"{cave}.th"
    plan_map = plan_map or f"{cave}MP"
    all_maps = {}
    surveys = []
    for dirpath, dirnames, filenames in os.walk(cave_dir):
        dirnames.sort()
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            if fn.endswith(".th"):
                text = read(full)
                if dirpath == cave_dir:
                    all_maps.update(parse_maps(text))   # master and Maps.th
                    continue
                s = parse_th(text, os.path.relpath(full, root))
                namespace = "" if s.namespace_off else s.name
                all_maps.update({qualify(k, namespace): v for k, v in s.maps.items()})
                if s.name:
                    surveys.append(s)
    th2_by_dir = {}
    for dirpath, _, filenames in os.walk(cave_dir):
        for fn in sorted(filenames):
            if fn.endswith(".th2"):
                full = os.path.join(dirpath, fn)
                th2_by_dir.setdefault(dirpath, []).append(parse_th2(read(full), os.path.relpath(full, root)))
    in_map = map_closure(all_maps, plan_map)
    master_inputs = parse_th(read(os.path.join(cave_dir, master))).inputs if os.path.exists(os.path.join(cave_dir, master)) else []
    master_input = {os.path.normpath(t): c for t, c in master_inputs}
    for s in surveys:
        s.th2 = th2_by_dir.get(os.path.join(root, os.path.dirname(s.path)), [])
        classify(s, in_map)
        rel = os.path.relpath(os.path.join(root, s.path), cave_dir)
        if master_input.get(os.path.normpath(rel), True):
            s.note = "; ".join(filter(None, [s.note, f"not input in {master}"]))
    return surveys


def of_year(surveys, year):
    return [s for s in surveys if any(d.year == year for d in s.dates)]


def xvi_status(root, survey):
    """'present', 'missing: …' or '' for the plan sketches."""
    images = [(t, img) for t in survey.th2 for img in t.images
              if any(sc.projection == "plan" for sc in t.scraps)]
    if not images:
        return "none referenced"
    missing = [img for t, img in images
               if not os.path.exists(os.path.join(root, os.path.dirname(t.path), img))]
    return "missing: " + ", ".join(missing) if missing else "present"


def markdown(root, cave, surveys, year, revision=""):
    def dates(s):
        return ", ".join(sorted({d.isoformat() for d in s.dates})) or "–"

    out = [f"# {cave} inventory", ""]
    if revision:
        out += [f"From SVN revision {revision}. Generated by `tools/svn2git/inventory.py`; "
                "do not edit by hand.", ""]
    todo = [s for s in of_year(surveys, year) if s.status == "undrawn"]
    out += [f"## {year} surveys with undrawn plans", ""]
    if todo:
        out += ["| Survey | Date | Team | Legs (m) | Why | Plan sketch (.xvi) |", "|---|---|---|---|---|---|"]
        for s in todo:
            out.append(f"| {s.name} (`{s.path}`) | {dates(s)} | {', '.join(s.team)} | {s.length:.1f} "
                       f"| {s.note} | {xvi_status(root, s)} |")
    else:
        out.append("None.")
    reported = [s for s in surveys if s.status == "drawn, reported" or "not input in" in s.note]
    out += ["", "## Reported, not for drawing", "",
            "Drawn plans that are not input or in no plan map, and surveys the master file "
            "does not input. Some are deliberate.", ""]
    out += [f"- {s.name} (`{s.path}`): {s.note}" for s in reported] or ["None."]
    out += ["", "## All surveys", "",
            "| Survey | Dates | Legs (m) | Plan | Notes |", "|---|---|---|---|---|"]
    for s in sorted(surveys, key=lambda s: (min(s.dates) if s.dates else datetime.date.min, s.name)):
        out.append(f"| {s.name} | {dates(s)} | {s.length:.1f} | {s.status} | {s.note} |")
    out.append("")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", help="checkout or export of the repository")
    ap.add_argument("cave", help="cave folder, e.g. LongwoodValleySink")
    ap.add_argument("--year", type=int, default=datetime.date.today().year)
    ap.add_argument("--revision", default="")
    ap.add_argument("-o", "--output")
    a = ap.parse_args(argv)
    text = markdown(a.root, a.cave, inventory(a.root, a.cave), a.year, a.revision)
    if a.output:
        with open(a.output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
