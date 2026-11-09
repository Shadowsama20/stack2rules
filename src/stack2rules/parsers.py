"""Bounded, root-only manifest inspection; never import project code."""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import stat
import tomllib

MAX_BYTES = 1_048_576
MANIFESTS = ("package.json", "requirements.txt", "pyproject.toml")
NODE_PACKAGES = {
    "react": "React", "react-dom": "React", "next": "Next.js",
    "tailwindcss": "Tailwind CSS", "typescript": "TypeScript",
    "vue": "Vue", "express": "Express", "vitest": "Vitest",
}
PYTHON_PACKAGES = {
    "fastapi": "FastAPI", "django": "Django", "pandas": "Pandas",
    "flask": "Flask", "sqlalchemy": "SQLAlchemy", "pytest": "pytest",
    "pydantic": "Pydantic", "numpy": "NumPy",
}
REQUIREMENT = re.compile(
    r"^([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)"
    r"(?=\s*(?:\[|[<>=!~;@(#]|$))"
)


@dataclass(frozen=True)
class Detection:
    technologies: tuple[str, ...]
    warnings: tuple[str, ...]


def forbidden(path: Path) -> bool:
    """Exclude secret and Git paths, including explicitly supplied roots."""
    return any(
        part.lower() == ".git" or part.lower().startswith(".env")
        for part in path.parts
    )


def _read(path: Path) -> str:
    """Reject links, devices, directories and oversized inputs before reading."""
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES:
        raise ValueError("unsafe input")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as stream:
        after = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(after.st_mode)
            or (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino)
            or after.st_size > MAX_BYTES
        ):
            raise ValueError("unsafe input")
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("oversized input")
    return raw.decode("utf-8-sig")


def _mapping(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def _names(value: object) -> set[str]:
    """Read named requirements only; URLs, options and includes are ignored."""
    found = set()
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str) and (match := REQUIREMENT.match(item.strip())):
                found.add(re.sub(r"[-_.]+", "-", match[1]).lower())
    return found


def _python_dependencies(data: dict) -> set[str]:
    project = _mapping(data.get("project"))
    names = _names(project.get("dependencies"))
    for group in _mapping(project.get("optional-dependencies")).values():
        names.update(_names(group))
    for group in _mapping(data.get("dependency-groups")).values():
        names.update(_names(group))
    poetry = _mapping(_mapping(data.get("tool")).get("poetry"))
    tables = [poetry.get("dependencies"), poetry.get("dev-dependencies")]
    for group in _mapping(poetry.get("group")).values():
        tables.append(_mapping(group).get("dependencies"))
    for table in tables:
        names.update(_names(list(_mapping(table))))
    return names


def detect_stack(directory: Path) -> Detection:
    """Detect declared technologies, including optional/dev dependencies."""
    if forbidden(directory.absolute()):
        raise ValueError("Excluded project directory.")
    root = directory.resolve(strict=True)
    if forbidden(root) or not root.is_dir():
        raise ValueError("Choose an existing, non-excluded project directory.")
    technologies: set[str] = set()
    warnings: list[str] = []
    for filename in MANIFESTS:
        try:
            source = _read(root / filename)
            if filename == "package.json":
                data = json.loads(source)
                if not isinstance(data, dict):
                    raise ValueError("expected object")
                technologies.add("Node.js")
                for key in ("dependencies", "devDependencies", "peerDependencies",
                            "optionalDependencies"):
                    technologies.update(
                        NODE_PACKAGES[name] for name in _mapping(data.get(key))
                        if name in NODE_PACKAGES
                    )
            else:
                if filename == "requirements.txt":
                    names = _names(source.splitlines())
                else:
                    names = _python_dependencies(tomllib.loads(source))
                technologies.add("Python")
                technologies.update(
                    PYTHON_PACKAGES[name] for name in names if name in PYTHON_PACKAGES
                )
        except FileNotFoundError:
            continue
        except (OSError, ValueError, RecursionError):
            # Never echo parser exceptions: they can contain source secrets.
            warnings.append(f"Skipped {filename}: unreadable, unsafe, oversized or invalid.")
    return Detection(tuple(sorted(technologies)), tuple(warnings))
