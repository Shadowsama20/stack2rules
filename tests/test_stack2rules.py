"""Run with: python -m unittest discover -s tests -v."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from stack2rules.cli import main
from stack2rules.parsers import MAX_BYTES, detect_stack
from stack2rules.templates import RULES, compile_markdown


class Stack2RulesTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def write(self, name, content):
        (self.root / name).write_text(content, encoding="utf-8")

    def run_cli(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(["--dir", str(self.root), *args])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_node_dependency_sections(self):
        self.write("package.json", json.dumps({
            "dependencies": {"next": "*", "react": "*"},
            "devDependencies": {"tailwindcss": "*", "typescript": "*"},
            "peerDependencies": {"vue": "*"},
            "optionalDependencies": {"express": "*", "vitest": "*"},
        }))
        self.assertEqual(set(detect_stack(self.root).technologies), {
            "Node.js", "Next.js", "React", "Tailwind CSS", "TypeScript",
            "Vue", "Express", "Vitest",
        })

    def test_requirements_names_extras_markers_and_direct_reference(self):
        self.write("requirements.txt", """# comment
FASTAPI[standard]>=0.100
Django~=5.0 ; python_version >= '3.11'
pandas @ https://example.invalid/private.whl
SQLAlchemy==2.0
numpy
pytest
pydantic
flask
-r .env
-e ./react
https://example.invalid/secret
""")
        self.assertEqual(set(detect_stack(self.root).technologies), {
            "Python", "FastAPI", "Django", "Pandas", "SQLAlchemy",
            "NumPy", "pytest", "Pydantic", "Flask",
        })

    def test_pyproject_groups_and_poetry(self):
        self.write("pyproject.toml", '''
[project]
dependencies = ["fastapi", "pydantic"]
[project.optional-dependencies]
analysis = ["pandas"]
[dependency-groups]
test = ["pytest", {include-group = "more"}]
more = ["numpy"]
[tool.poetry.dependencies]
python = "^3.11"
Django = {version = "*", optional = true}
[tool.poetry.dev-dependencies]
flask = "*"
[tool.poetry.group.db.dependencies]
sqlalchemy = "*"
''')
        self.assertEqual(set(detect_stack(self.root).technologies), {
            "Python", "FastAPI", "Pydantic", "Pandas", "pytest", "NumPy",
            "Django", "Flask", "SQLAlchemy",
        })

    def test_malformed_manifests_do_not_block_valid_input(self):
        self.write("package.json", '{"secret": "DO_NOT_PRINT",')
        self.write("pyproject.toml", 'invalid = ["DO_NOT_PRINT"')
        self.write("requirements.txt", "fastapi")
        result = detect_stack(self.root)
        self.assertEqual(result.technologies, ("FastAPI", "Python"))
        self.assertEqual(len(result.warnings), 2)
        code, stdout, stderr = self.run_cli()
        self.assertEqual(code, 0)
        self.assertNotIn("DO_NOT_PRINT", stdout + stderr)

    def test_wrong_field_types_are_ignored(self):
        self.write("package.json", '{"dependencies": ["react"], "devDependencies": null}')
        self.write("pyproject.toml", '[project]\ndependencies = "django"')
        self.assertEqual(detect_stack(self.root).technologies, ("Node.js", "Python"))

    def test_non_object_json_is_skipped(self):
        self.write("package.json", '["react"]')
        self.assertEqual(detect_stack(self.root).technologies, ())
        self.assertEqual(len(detect_stack(self.root).warnings), 1)

    def test_unknown_packages_scripts_and_secret_metadata_never_render(self):
        self.write("package.json", json.dumps({
            "dependencies": {"react": "SECRET_TOKEN", "arbitrary-secret": "value"},
            "scripts": {"next": "DO_NOT_EXECUTE"},
            "api_key": "DO_NOT_PRINT", "description": "# Injected instructions",
        }))
        self.assertEqual(self.run_cli()[0], 0)
        content = (self.root / "CLAUDE.md").read_text()
        for secret in ("SECRET_TOKEN", "arbitrary-secret", "DO_NOT_EXECUTE",
                       "DO_NOT_PRINT", "Injected instructions", "## Next.js"):
            self.assertNotIn(secret, content)

    def test_scan_does_not_walk_or_open_env(self):
        for directory in (".git", "child", "node_modules"):
            (self.root / directory).mkdir()
            (self.root / directory / "package.json").write_text('{"dependencies":{"react":"*"}}')
        self.write(".env", "secret")
        with patch("stack2rules.parsers.os.open", wraps=os.open) as opened:
            self.assertEqual(detect_stack(self.root).technologies, ())
            opened.assert_not_called()

    def test_excluded_explicit_root(self):
        for name in (".git", ".env.private"):
            excluded = self.root / name
            excluded.mkdir()
            with self.assertRaises(ValueError):
                detect_stack(excluded)

    def test_symlink_manifest_is_not_read(self):
        self.write(".env", '{"dependencies":{"react":"*"}}')
        try:
            (self.root / "package.json").symlink_to(self.root / ".env")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with patch("stack2rules.parsers.os.open", wraps=os.open) as opened:
            result = detect_stack(self.root)
            opened.assert_not_called()
        self.assertEqual(result.technologies, ())
        self.assertEqual(len(result.warnings), 1)

    def test_oversized_and_invalid_utf8_inputs(self):
        self.write("requirements.txt", "x" * (MAX_BYTES + 1))
        (self.root / "package.json").write_bytes(b"\xff")
        result = detect_stack(self.root)
        self.assertEqual(result.technologies, ())
        self.assertEqual(len(result.warnings), 2)

    def test_deeply_nested_json_is_skipped(self):
        self.write("package.json", "[" * 2000 + "0" + "]" * 2000)
        self.assertEqual(len(detect_stack(self.root).warnings), 1)

    def test_directory_and_fifo_manifests_are_skipped(self):
        (self.root / "package.json").mkdir()
        if hasattr(os, "mkfifo"):
            os.mkfifo(self.root / "requirements.txt")
        self.assertEqual(detect_stack(self.root).technologies, ())
        self.assertTrue(detect_stack(self.root).warnings)

    def test_empty_project_generates_general_rules(self):
        self.assertEqual(self.run_cli()[0], 0)
        self.assertIn("No supported technologies detected", (self.root / "CLAUDE.md").read_text())

    def test_output_relative_to_selected_root(self):
        (self.root / "docs").mkdir()
        self.assertEqual(self.run_cli("--output", "docs/rules.md")[0], 0)
        self.assertTrue((self.root / "docs/rules.md").is_file())

    def test_existing_output_preserved(self):
        self.write("CLAUDE.md", "handwritten rules")
        self.assertEqual(self.run_cli()[0], 1)
        self.assertEqual((self.root / "CLAUDE.md").read_text(), "handwritten rules")
        self.assertFalse(list(self.root.glob(".stack2rules-*")))

    def test_existing_symlink_output_preserved(self):
        self.write("original.md", "handwritten rules")
        try:
            (self.root / "CLAUDE.md").symlink_to(self.root / "original.md")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        self.assertEqual(self.run_cli()[0], 1)
        self.assertEqual((self.root / "original.md").read_text(), "handwritten rules")

    def test_unsafe_output_paths_rejected(self):
        for output in ("../escape.md", "package.json", ".env.md", ".git/rules.md",
                       "missing/rules.md", str(self.root.parent / "escape.md")):
            with self.subTest(output=output):
                self.assertEqual(self.run_cli("--output", output)[0], 1)

    def test_parent_symlink_cannot_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            try:
                (self.root / "docs").symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            self.assertEqual(self.run_cli("--output", "docs/rules.md")[0], 1)
            self.assertFalse((Path(outside) / "rules.md").exists())

    def test_failed_publication_cleans_up(self):
        with patch("stack2rules.cli.os.link", side_effect=OSError("SECRET")):
            code, stdout, stderr = self.run_cli()
        self.assertEqual(code, 1)
        self.assertNotIn("SECRET", stdout + stderr)
        self.assertFalse((self.root / "CLAUDE.md").exists())
        self.assertFalse(list(self.root.glob(".stack2rules-*")))

    def test_missing_root_fails_cleanly(self):
        self.assertEqual(self.run_cli("--dir", str(self.root / "absent"))[0], 1)

    def test_deterministic_and_allowlisted_templates(self):
        first = compile_markdown(("React", "FastAPI", "React", "# injected"))
        self.assertEqual(first, compile_markdown(("FastAPI", "React")))
        self.assertEqual(first.count("## React\n"), 1)
        self.assertNotIn("injected", first)
        self.assertTrue(first.endswith("\n"))

    def test_every_detection_label_has_rules(self):
        from stack2rules.parsers import NODE_PACKAGES, PYTHON_PACKAGES
        self.assertTrue(set(NODE_PACKAGES.values()) <= RULES.keys())
        self.assertTrue(set(PYTHON_PACKAGES.values()) <= RULES.keys())


if __name__ == "__main__":
    unittest.main()
