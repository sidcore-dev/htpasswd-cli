import unittest

from htpasswd_cli.core import format_entry, hash_password, merge_entry, validate_username


class TestHashPassword(unittest.TestCase):
    def test_hash_has_prefix(self) -> None:
        self.assertTrue(hash_password("hunter2").startswith("{SHA256}"))

    def test_hash_is_deterministic(self) -> None:
        self.assertEqual(hash_password("hunter2"), hash_password("hunter2"))

    def test_different_passwords_differ(self) -> None:
        self.assertNotEqual(hash_password("hunter2"), hash_password("hunter3"))


class TestValidateUsername(unittest.TestCase):
    def test_empty_username_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_username("")

    def test_colon_in_username_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_username("al:ice")

    def test_ok_username_passes(self) -> None:
        validate_username("alice")  # should not raise


class TestFormatEntry(unittest.TestCase):
    def test_entry_shape(self) -> None:
        entry = format_entry("alice", "hunter2")
        self.assertTrue(entry.startswith("alice:{SHA256}"))
        self.assertEqual(entry.count(":"), 1)


class TestMergeEntry(unittest.TestCase):
    def test_adds_new_entry_to_empty_file(self) -> None:
        content, action = merge_entry("", "alice", "hunter2")
        self.assertEqual(action, "added")
        self.assertIn("alice:{SHA256}", content)

    def test_adds_new_entry_alongside_existing(self) -> None:
        existing = "bob:{SHA256}xxx\n"
        content, action = merge_entry(existing, "alice", "hunter2")
        self.assertEqual(action, "added")
        self.assertIn("bob:{SHA256}xxx", content)
        self.assertIn("alice:{SHA256}", content)

    def test_updates_existing_entry_in_place(self) -> None:
        existing = "alice:{SHA256}oldhash\nbob:{SHA256}yyy\n"
        content, action = merge_entry(existing, "alice", "hunter2")
        self.assertEqual(action, "updated")
        self.assertNotIn("oldhash", content)
        self.assertIn("bob:{SHA256}yyy", content)
        # only one line for alice
        alice_lines = [line for line in content.splitlines() if line.startswith("alice:")]
        self.assertEqual(len(alice_lines), 1)

    def test_preserves_comments_and_blank_lines(self) -> None:
        existing = "# a comment\n\nbob:{SHA256}yyy\n"
        content, _action = merge_entry(existing, "alice", "hunter2")
        self.assertIn("# a comment", content)


if __name__ == "__main__":
    unittest.main()
