import unittest

from tools.svn2git import authors


class AuthorsTest(unittest.TestCase):
    def test_parse(self):
        got = authors.parse("# note\n\nandrew = Andrew Atkinson <a@x.invalid>\n(no author) = (no author) <n@x.invalid>\n")
        self.assertEqual(got, {"andrew": ("Andrew Atkinson", "a@x.invalid"),
                               "(no author)": ("(no author)", "n@x.invalid")})

    def test_bad_line_names_the_line(self):
        with self.assertRaisesRegex(ValueError, "authors.txt:2"):
            authors.parse("a = A <a@x>\nb = no email\n")

    def test_missing_lists_unmapped_names(self):
        mapping = {"andrew": ("A", "a"), "graham": ("G", "g")}
        self.assertEqual(authors.missing(mapping, ["andrew", "zed", "bob", "zed"]), ["bob", "zed"])
        self.assertEqual(authors.missing(mapping, ["andrew", "graham"]), [])

    def test_empty_author_is_no_author(self):
        self.assertEqual(authors.missing({}, [""]), ["(no author)"])
        self.assertEqual(authors.missing({"(no author)": ("n", "n")}, [""]), [])

    def test_main_fails_on_unmapped(self):
        self.assertEqual(authors.main(["andrew", "JohnCooper", "graham"]), 0)
        self.assertEqual(authors.main(["andrew", "nobody"]), 1)


class AuthorsFileTest(unittest.TestCase):
    def setUp(self):
        self.authors = authors.load()

    def test_the_three_surveyors(self):
        self.assertEqual(self.authors["andrew"][0], "Andrew Atkinson")
        self.assertEqual(self.authors["JohnCooper"][0], "John Cooper")
        self.assertEqual(self.authors["graham"][0], "Graham Mullan")

    def test_every_repository_author_is_mapped(self):
        # From `svn log` of the whole repository at r501.
        seen = ["andrew", "JohnCooper", "graham", "ben", "cavereg", "wookey", ""]
        self.assertEqual(authors.missing(self.authors, seen), [])

    def test_emails_are_placeholders(self):
        # Remove this test when real emails go into a .mailmap.
        for user, (_, email) in self.authors.items():
            self.assertTrue(email.endswith("@cave-registry.invalid"), user)


if __name__ == "__main__":
    unittest.main()
