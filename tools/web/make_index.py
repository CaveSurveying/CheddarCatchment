# Adapted from caves-mendip-swildons, web/make_index.py (commit 198bf46,
# https://github.com/paperclipmonkey/caves-mendip-swildons). GPLv3: see tools/LICENSE.
"""Write output/index.html and output/stats.md for a build's sheets.

Run after Therion, from the top of the repository:

    python3 -m tools.web.make_index

The sheets are the ones listed in tools/project.toml, copied from the
cave's Outputs/ folder into output/ (CI attaches output/ to the run).
A sheet that was not built is left out. The statistics come from
output/therion.log. PNG previews need Ghostscript; without it the page
has links only. No third-party Python packages.
"""

import html
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

from tools import project as _project


def human(n):
    for unit in ("B", "kB", "MB"):
        if n < 1024 or unit == "MB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024.0


def render_preview(pdf_path, png_path):
    """First page of a PDF to PNG with Ghostscript; False if it can't."""
    gs = shutil.which("gs")
    if not gs:
        return False
    cmd = [gs, "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=png16m", "-r80",
           "-dFirstPage=1", "-dLastPage=1", "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4",
           "-sOutputFile=" + png_path, pdf_path]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
        return os.path.exists(png_path)
    except Exception:
        return False


def survey_stats(log_text):
    """Headline numbers from a therion.log, in display order."""
    stats = {}
    m = re.search(r"Total length of survey legs\s*=\s*([\d.]+)m", log_text)
    if m:
        stats["Surveyed length"] = f"{float(m.group(1)):.1f} m"
    m = re.search(r"Vertical range\s*=\s*([\d.]+)m", log_text)
    if m:
        stats["Vertical range"] = f"{float(m.group(1)):.2f} m"
    m = re.search(r"output coordinate system:\s*(\S+)", log_text)
    if m:
        stats["Coordinate system"] = m.group(1)
    stats["Therion errors"] = str(len(re.findall(r"^therion: error", log_text, re.M)))
    stats["Scrap outlines that cross themselves"] = str(len(set(
        re.findall(r"scrap outline intersects itself[^\n]*", log_text))))
    return stats


def stats_markdown(stats):
    return "".join(f"- **{k}:** {v}\n" for k, v in stats.items())


def collect(p, out):
    """Copy the built sheets into `out`: [(sheet, size)] for those that exist."""
    found = []
    for sheet in p.sheets:
        src = p.path(os.path.join(p.build["outputs"], sheet["file"]))
        if not os.path.exists(src):
            print(f"not built, left out: {sheet['file']}", file=sys.stderr)
            continue
        dst = os.path.join(out, sheet["file"])
        if os.path.abspath(src) != os.path.abspath(dst):
            shutil.copyfile(src, dst)
        found.append((sheet, os.path.getsize(dst)))
    return found


def page(p, sheets, stats, previews, commit=""):
    esc = html.escape
    when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cards = []
    for sheet, size in sheets:
        img = (f'<img src="previews/{esc(previews[sheet["file"]])}" alt="">'
               if sheet["file"] in previews else "")
        cards.append(f'<section><h2><a href="{esc(sheet["file"])}">{esc(sheet["title"])}</a></h2>'
                     f'<p>{esc(sheet["blurb"])} ({human(size)})</p>{img}</section>')
    rows = "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in stats.items())
    return f"""<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(p.cave['title'])}: survey build</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:60rem;margin:1rem auto;padding:0 1rem;color:#222;background:#fff}}
img{{max-width:100%;border:1px solid #ccc}} th{{text-align:left;padding-right:1rem}}
</style></head><body>
<h1>{esc(p.cave['title'])}</h1>
<p>Built {when}{' from ' + esc(commit[:7]) if commit else ''}. Survey data and drawings
{esc(p.drawing['licence'])}.</p>
<table>{rows}</table>
{''.join(cards) if cards else '<p>No sheets were built.</p>'}
</body></html>
"""


def main(argv=None):
    p = _project.load()
    out = p.path("output")
    os.makedirs(os.path.join(out, "previews"), exist_ok=True)
    sheets = collect(p, out)
    log = p.path(p.build["log"])
    stats = survey_stats(open(log, errors="replace").read()) if os.path.exists(log) else {}
    previews = {}
    for sheet, _ in sheets:
        png = sheet["file"].rsplit(".", 1)[0] + ".png"
        if render_preview(os.path.join(out, sheet["file"]), os.path.join(out, "previews", png)):
            previews[sheet["file"]] = png
    with open(os.path.join(out, "stats.md"), "w", encoding="utf-8") as f:
        f.write(stats_markdown(stats))
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(p, sheets, stats, previews, os.environ.get("GITHUB_SHA", "")))
    print(f"wrote {out}/index.html and stats.md: {len(sheets)} sheet(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
