import unittest

from safe_filename_sanitizer import sanitize_filename, sanitize_path_segment


class TestSanitizeFilename(unittest.TestCase):

    def test_clean_name_passes_through(self):
        self.assertEqual(sanitize_filename("hello.txt"), "hello.txt")

    def test_forward_slash_replaced(self):
        self.assertEqual(sanitize_filename("a/b/c"), "a_b_c")

    def test_backslash_replaced(self):
        self.assertEqual(sanitize_filename("a\\b\\c"), "a_b_c")

    def test_colon_replaced(self):
        self.assertEqual(sanitize_filename("a:b"), "a_b")

    def test_multiple_illegal_collapsed(self):
        self.assertEqual(sanitize_filename("a???b***c"), "a_b_c")

    def test_control_chars_replaced(self):
        self.assertEqual(sanitize_filename("a\x00b\x1fc"), "a_b_c")

    def test_trailing_dot_stripped(self):
        self.assertEqual(sanitize_filename("file.txt."), "file.txt")

    def test_trailing_space_stripped(self):
        self.assertEqual(sanitize_filename("file.txt "), "file.txt")

    def test_empty_becomes_underscore(self):
        self.assertEqual(sanitize_filename(""), "_")

    def test_only_dots_becomes_underscore(self):
        self.assertEqual(sanitize_filename("..."), "_")

    def test_only_spaces_becomes_underscore(self):
        self.assertEqual(sanitize_filename("   "), "_")

    def test_windows_reserved_con_prefixed(self):
        self.assertEqual(sanitize_filename("CON"), "_CON")

    def test_windows_reserved_con_with_extension(self):
        self.assertEqual(sanitize_filename("CON.txt"), "_CON.txt")

    def test_windows_reserved_nul_case_insensitive(self):
        self.assertEqual(sanitize_filename("nul"), "_nul")

    def test_windows_reserved_com1(self):
        self.assertEqual(sanitize_filename("COM1"), "_COM1")

    def test_not_reserved_if_substring(self):
        self.assertEqual(sanitize_filename("CONsole"), "CONsole")

    def test_custom_replacement(self):
        self.assertEqual(sanitize_filename("a/b", replacement="-"), "a-b")

    def test_custom_replacement_invalid_value_rejected(self):
        with self.assertRaises(ValueError):
            sanitize_filename("a", replacement="/")

    def test_none_rejected(self):
        with self.assertRaises(TypeError):
            sanitize_filename(None)

    def test_non_string_rejected(self):
        with self.assertRaises(TypeError):
            sanitize_filename(123)

    def test_path_segment_matches_filename(self):
        self.assertEqual(
            sanitize_path_segment("a/b/c"),
            sanitize_filename("a/b/c"),
        )


if __name__ == "__main__":
    unittest.main()
