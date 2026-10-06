import unittest

from tools.svn2git import svnhttp

PROPFIND = """<?xml version="1.0" encoding="utf-8"?>
<D:multistatus xmlns:D="DAV:">
<D:response xmlns:S="http://subversion.tigris.org/xmlns/svn/" xmlns:lp1="DAV:">
<D:href>/svn/Repo/Cave/</D:href>
<D:propstat><D:prop>
<S:global-ignores>Old
</S:global-ignores>
<lp1:resourcetype><D:collection/></lp1:resourcetype>
</D:prop><D:status>HTTP/1.1 200 OK</D:status></D:propstat>
</D:response>
<D:response xmlns:S="http://subversion.tigris.org/xmlns/svn/" xmlns:lp1="DAV:">
<D:href>/svn/Repo/Cave/Big%20Hole.th</D:href>
<D:propstat><D:prop>
<S:executable>*</S:executable>
<lp1:resourcetype/>
<lp1:getcontentlength>4134</lp1:getcontentlength>
</D:prop><D:status>HTTP/1.1 200 OK</D:status></D:propstat>
</D:response>
</D:multistatus>
"""

LOG = """<?xml version="1.0" encoding="utf-8"?>
<S:log-report xmlns:S="svn:" xmlns:D="DAV:">
<S:log-item>
<S:added-path node-kind="dir" copyfrom-path="/Old" copyfrom-rev="4">/Cave</S:added-path>
<S:modified-path node-kind="file" text-mods="true" prop-mods="false">/Cave/a.th</S:modified-path>
<D:version-name>5</D:version-name>
<D:creator-displayname>andrew</D:creator-displayname>
<S:date>2026-09-13T07:25:22.190459Z</S:date>
<D:comment>Added data
</D:comment>
</S:log-item>
<S:log-item>
<D:version-name>3</D:version-name>
<S:date>2013-11-19T10:00:00.000000Z</S:date>
</S:log-item>
</S:log-report>
"""


class PropfindTest(unittest.TestCase):
    def test_folder_and_file(self):
        folder, file = svnhttp.parse_propfind(PROPFIND, "/svn/Repo")
        self.assertEqual(folder.path, "Cave")
        self.assertTrue(folder.is_dir)
        self.assertEqual(folder.props, {"svn:global-ignores": "Old\n"})
        self.assertEqual(file.path, "Cave/Big Hole.th")     # %20 decoded
        self.assertFalse(file.is_dir)
        self.assertEqual(file.size, 4134)
        self.assertEqual(file.props, {"svn:executable": "*"})


class LogTest(unittest.TestCase):
    def test_entries_paths_and_copies(self):
        new, old = svnhttp.parse_log_report(LOG)
        self.assertEqual((new.revision, new.author, new.message), (5, "andrew", "Added data\n"))
        self.assertEqual(new.date[:10], "2026-09-13")
        self.assertEqual([(c.action, c.path) for c in new.paths], [("A", "/Cave"), ("M", "/Cave/a.th")])
        self.assertEqual((new.paths[0].copyfrom_path, new.paths[0].copyfrom_rev), ("/Old", 4))
        self.assertEqual(new.paths[1].copyfrom_path, "")

    def test_missing_author_and_message(self):
        old = svnhttp.parse_log_report(LOG)[1]
        self.assertEqual((old.revision, old.author, old.message, old.paths), (3, "", "", []))


class UrlTest(unittest.TestCase):
    def test_quoting(self):
        self.assertEqual(svnhttp.url_for("/Great Swallet/a.th", "https://h/svn/R/"),
                         "https://h/svn/R/Great%20Swallet/a.th")
        self.assertEqual(svnhttp.repo_root_path("https://h/svn/R/"), "/svn/R")


if __name__ == "__main__":
    unittest.main()
