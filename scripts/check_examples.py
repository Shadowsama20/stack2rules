"""Check or intentionally refresh synthetic, committed example output."""

import argparse
from contextlib import redirect_stdout
import io
from pathlib import Path
import shutil
import tempfile

from stack2rules.cli import main as generate
from stack2rules.parsers import MANIFESTS


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="refresh expected output")
    args = parser.parse_args()
    examples = Path(__file__).resolve().parents[1] / "examples"
    failed = False
    for name in ("nextjs", "django", "fullstack"):
        fixture = examples / name
        expected = fixture / "CLAUDE.example.md"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for filename in MANIFESTS:
                source = fixture / filename
                if source.is_file():
                    shutil.copyfile(source, root / filename)
            with redirect_stdout(io.StringIO()):
                code = generate(["--dir", str(root)])
            if code:
                raise RuntimeError(f"Generation failed for {name}")
            actual = (root / "CLAUDE.md").read_text(encoding="utf-8")
        if args.write:
            expected.write_text(actual, encoding="utf-8", newline="\n")
            print(f"Updated {name}")
        elif not expected.is_file() or expected.read_text(encoding="utf-8") != actual:
            print(f"FAIL: {name}; inspect changes before using --write")
            failed = True
        else:
            print(f"OK: {name}")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
