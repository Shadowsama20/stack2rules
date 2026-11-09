"""Exercise the real module entry point in fresh, noninteractive processes."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CLIIntegrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-S", "-m", "stack2rules.cli", *args],
            cwd=self.root, env=self.env, stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=15,
        )

    def test_no_arguments_generate_in_current_directory(self):
        (self.root / "requirements.txt").write_text("fastapi\npandas\n")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        content = (self.root / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("## FastAPI\n", content)
        self.assertIn("## Pandas\n", content)

    def test_help_does_not_generate_a_file(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("--output", result.stdout)
        self.assertFalse((self.root / "CLAUDE.md").exists())

    def test_invalid_arguments_exit_two(self):
        result = self.run_cli("--unknown")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / "CLAUDE.md").exists())

    def test_rerun_preserves_existing_context(self):
        self.assertEqual(self.run_cli().returncode, 0)
        output = self.root / "CLAUDE.md"
        output.write_text("custom user instructions", encoding="utf-8")
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(output.read_text(), "custom user instructions")

    def test_directory_and_output_paths_with_spaces(self):
        project = self.root / "my project"
        project.mkdir()
        result = self.run_cli("--dir", str(project), "--output", "my rules.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((project / "my rules.md").exists())
        self.assertFalse((self.root / "CLAUDE.md").exists())

    def test_invalid_manifest_warns_without_disclosing_content(self):
        (self.root / "package.json").write_text('{"key":"PRIVATE_VALUE",')
        result = self.run_cli()
        self.assertEqual(result.returncode, 0)
        self.assertIn("warning", result.stderr)
        self.assertNotIn("PRIVATE_VALUE", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
