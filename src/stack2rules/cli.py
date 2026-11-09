"""Noninteractive CLI with atomic, no-clobber output publication."""

import argparse
import os
from pathlib import Path
import sys
import tempfile

from .parsers import detect_stack, forbidden
from .templates import compile_markdown


def _destination(root: Path, output: Path) -> Path:
    candidate = output if output.is_absolute() else root / output
    if forbidden(candidate) or ".." in candidate.parts:
        raise ValueError("Output must not use excluded paths or '..'.")
    parent = candidate.parent.resolve(strict=True)
    if not parent.is_relative_to(root) or forbidden(parent):
        raise ValueError("Output must stay inside the project directory.")
    if candidate.suffix.lower() != ".md":
        raise ValueError("Output must be a Markdown (.md) file.")
    return parent / candidate.name


def _publish(destination: Path, content: str) -> None:
    """Publish a complete file without replacing any existing path or symlink."""
    fd, name = tempfile.mkstemp(prefix=".stack2rules-", dir=destination.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate CLAUDE.md from local project manifests without prompts."
    )
    parser.add_argument("--dir", type=Path, default=Path.cwd(),
                        help="project directory (default: current directory)")
    parser.add_argument("--output", type=Path, default=Path("CLAUDE.md"),
                        help="new .md file inside the project (default: CLAUDE.md)")
    args = parser.parse_args(argv)
    try:
        detection = detect_stack(args.dir)
        root = args.dir.resolve(strict=True)
        destination = _destination(root, args.output)
        for warning in detection.warnings:
            print(f"stack2rules: warning: {warning}", file=sys.stderr)
        _publish(destination, compile_markdown(detection.technologies))
    except FileExistsError:
        print("stack2rules: output already exists; choose another --output or "
              "move the existing file first.", file=sys.stderr)
        return 1
    except (OSError, ValueError, RuntimeError):
        # Do not echo OS errors or supplied paths, which may contain secrets.
        print("stack2rules: cannot generate output. Check --dir, permissions and "
              "--output (a new .md file within the project, with an existing "
              "parent directory). Git/.env paths are excluded; the output "
              "filesystem must support hard links.", file=sys.stderr)
        return 1
    print("stack2rules: created Markdown context. Detected: "
          + (", ".join(detection.technologies) or "no supported technologies"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
