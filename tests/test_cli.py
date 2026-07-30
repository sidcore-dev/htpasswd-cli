import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from htpasswd_cli.cli import main


class TestCli(unittest.TestCase):
    def test_prints_entry_with_password_flag(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["alice", "--password", "hunter2"])
        self.assertEqual(code, 0)
        self.assertIn("alice:{SHA256}", out.getvalue())

    def test_rejects_empty_username(self) -> None:
        code = main(["", "--password", "hunter2"])
        self.assertEqual(code, 2)

    def test_append_creates_file(self) -> None:
        with TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "htpasswd")
            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["alice", "--password", "hunter2", "--append", path])
            self.assertEqual(code, 0)
            self.assertIn("added", out.getvalue())
            content = Path(path).read_text()
            self.assertIn("alice:{SHA256}", content)

    def test_append_updates_existing_entry(self) -> None:
        with TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "htpasswd")
            main(["alice", "--password", "hunter2", "--append", path])
            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["alice", "--password", "newpass", "--append", path])
            self.assertEqual(code, 0)
            self.assertIn("updated", out.getvalue())
            content = Path(path).read_text()
            alice_lines = [line for line in content.splitlines() if line.startswith("alice:")]
            self.assertEqual(len(alice_lines), 1)


if __name__ == "__main__":
    unittest.main()
