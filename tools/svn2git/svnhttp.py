"""Read an SVN repository over plain HTTP (WebDAV), without an svn client.

Used for the read-only inventory when `svn` cannot be installed. It does
three things: list a folder with its SVN properties (PROPFIND), give the
log of a path with changed paths and copy sources (REPORT log-report),
and export files at HEAD (GET).

    python3 -m tools.svn2git.svnhttp log LongwoodValleySink
    python3 -m tools.svn2git.svnhttp export DEST LongwoodValleySink common_layout.th
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

REPO = "https://www.cave-registry.org.uk/svn/CheddarCatchment"

DAV = "{DAV:}"
SVN = "{svn:}"
# Namespaces Subversion's mod_dav_svn uses for versioned properties.
SVN_PROPS = "{http://subversion.tigris.org/xmlns/svn/}"
CUSTOM_PROPS = "{http://subversion.tigris.org/xmlns/custom/}"


@dataclass
class Entry:
    path: str           # relative to the repository root, no leading slash
    is_dir: bool
    size: int = 0
    props: dict = field(default_factory=dict)   # e.g. {"svn:ignore": "..."}


@dataclass
class ChangedPath:
    action: str         # A, M, D or R
    path: str
    kind: str = ""
    copyfrom_path: str = ""
    copyfrom_rev: int = 0


@dataclass
class LogEntry:
    revision: int
    author: str
    date: str
    message: str
    paths: list = field(default_factory=list)


def repo_root_path(repo=REPO):
    """The URL path of the repository root, e.g. /svn/CheddarCatchment."""
    return urllib.parse.urlparse(repo).path.rstrip("/")


def parse_propfind(xml_text, root_path):
    """Entries from a PROPFIND Depth:1 response."""
    entries = []
    for resp in ET.fromstring(xml_text).iter(DAV + "response"):
        href = urllib.parse.unquote(resp.findtext(DAV + "href"))
        rel = href[len(root_path):].strip("/") if href.startswith(root_path) else href.strip("/")
        prop = resp.find(f"{DAV}propstat/{DAV}prop")
        is_dir = prop.find(f"{DAV}resourcetype/{DAV}collection") is not None
        size = int(prop.findtext(DAV + "getcontentlength") or 0)
        props = {}
        for child in prop:
            if child.tag.startswith(SVN_PROPS):
                props["svn:" + child.tag[len(SVN_PROPS):]] = child.text or ""
            elif child.tag.startswith(CUSTOM_PROPS):
                props[child.tag[len(CUSTOM_PROPS):]] = child.text or ""
        entries.append(Entry(rel, is_dir, size, props))
    return entries


def parse_log_report(xml_text):
    """LogEntry list from a log-report response, newest first."""
    out = []
    for item in ET.fromstring(xml_text).iter(SVN + "log-item"):
        entry = LogEntry(
            revision=int(item.findtext(DAV + "version-name")),
            author=item.findtext(DAV + "creator-displayname") or "",
            date=item.findtext(SVN + "date") or "",
            message=item.findtext(DAV + "comment") or "",
        )
        for child in item:
            tag = child.tag[len(SVN):] if child.tag.startswith(SVN) else ""
            action = {"added-path": "A", "modified-path": "M",
                      "deleted-path": "D", "replaced-path": "R"}.get(tag)
            if action:
                entry.paths.append(ChangedPath(
                    action, child.text or "", child.get("node-kind", ""),
                    child.get("copyfrom-path", ""), int(child.get("copyfrom-rev") or 0)))
        out.append(entry)
    return out


def _request(url, method="GET", headers=None, data=None):
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=data)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def url_for(path, repo=REPO):
    return repo.rstrip("/") + "/" + urllib.parse.quote(path.strip("/"))


def propfind(path, repo=REPO):
    """The entry for `path` followed by its children (if a folder)."""
    xml_text = _request(url_for(path, repo), "PROPFIND", {"Depth": "1"})
    return parse_propfind(xml_text, repo_root_path(repo))


def walk(path, repo=REPO):
    """Every entry under `path` (a file or folder), recursively.

    Paths the server refuses (403, access-restricted) are returned as
    entries with props {"error": "403"} and not entered.
    """
    try:
        entries = propfind(path, repo)
    except urllib.error.HTTPError as e:
        yield Entry(path.strip("/"), False, 0, {"error": str(e.code)})
        return
    me, children = entries[0], entries[1:]
    yield me
    for child in children:
        if child.is_dir:
            yield from walk(child.path, repo)
        else:
            yield child


def log(path, repo=REPO, start="HEAD", end=0, limit=0):
    """The SVN log of `path`, with changed paths, newest first."""
    head = head_revision(repo) if start == "HEAD" else start
    body = (
        '<?xml version="1.0"?><S:log-report xmlns:S="svn:">'
        f"<S:start-revision>{head}</S:start-revision><S:end-revision>{end}</S:end-revision>"
        + (f"<S:limit>{limit}</S:limit>" if limit else "")
        + "<S:discover-changed-paths/><S:all-revprops/>"
        f"<S:path>{path.strip('/')}</S:path></S:log-report>"
    )
    xml_text = _request(repo.rstrip("/") + "/", "REPORT", {"Content-Type": "text/xml"}, body.encode())
    return parse_log_report(xml_text)


def head_revision(repo=REPO):
    """HEAD revision, from the etag of the root (W/"501//")."""
    req = urllib.request.Request(repo.rstrip("/") + "/", method="PROPFIND", headers={"Depth": "0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = resp.read().decode()
    root = ET.fromstring(text)
    return int(root.findtext(f".//{DAV}version-name"))


def export(dest, paths, repo=REPO):
    """Download `paths` (files or folders) at HEAD into `dest`.

    Returns the list of entries seen, so the caller can record sizes,
    properties and refused paths.
    """
    seen = []
    for top in paths:
        for entry in walk(top, repo):
            seen.append(entry)
            target = os.path.join(dest, *entry.path.split("/"))
            if entry.props.get("error"):
                continue
            if entry.is_dir:
                os.makedirs(target, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "wb") as f:
                f.write(_request(url_for(entry.path, repo)))
    return seen


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=REPO)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("log", help="log of a path as JSON")
    p.add_argument("path")
    p = sub.add_parser("ls", help="recursive listing with sizes and properties as JSON")
    p.add_argument("paths", nargs="+")
    p = sub.add_parser("export", help="download paths at HEAD")
    p.add_argument("dest")
    p.add_argument("paths", nargs="+")
    a = ap.parse_args(argv)
    if a.cmd == "log":
        json.dump([e.__dict__ | {"paths": [c.__dict__ for c in e.paths]} for e in log(a.path, a.repo)],
                  sys.stdout, indent=1)
    elif a.cmd == "ls":
        json.dump([e.__dict__ for p in a.paths for e in walk(p, a.repo)], sys.stdout, indent=1)
    else:
        seen = export(a.dest, a.paths, a.repo)
        print(f"{sum(not e.is_dir for e in seen)} files exported to {a.dest}")


if __name__ == "__main__":
    main()
