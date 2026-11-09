# stack2rules

Generate a stack-specific `CLAUDE.md` by running one command in a project root.
No prompts, accounts, API calls, telemetry, or runtime dependencies.

**Release status:** [v1.0.0 is available](https://github.com/Shadowsama20/stack2rules/releases/tag/v1.0.0)
with an installable wheel and source archive. PyPI publication is pending.
This is an independent community tool, not an Anthropic product.
See the [validation record](VALIDATION.md) for checks actually run.

Start with the [examples](examples/README.md), [contribution guide](CONTRIBUTING.md)
or [release instructions](RELEASE.md).

Requires **Python 3.11+**. Parsing uses standard-library `json`, `re` and
`tomllib`. Setuptools is a **build-time** dependency only, as required by the
`setuptools.build_meta` packaging backend.

## Install and run

From this tool's source directory, preferably inside a virtual environment:

```sh
python -m venv .venv
# Activate: source .venv/bin/activate (macOS/Linux)
# Or: .venv\Scripts\Activate.ps1 (Windows PowerShell)
python -m pip install -e .
cd /path/to/your/project
stack2rules
```

This creates `CLAUDE.md` in the current directory. Nothing is executed from the
scanned project. The tool never asks questions.

```sh
stack2rules --dir /path/to/project
stack2rules --dir /path/to/project --output CLAUDE.generated.md
python -m stack2rules.cli --help
```

Relative output paths resolve against `--dir`, not the invoking directory.
Absolute output paths are accepted inside the project. The parent must already
exist, the extension must be `.md`, and `..` components are rejected. Existing
files and symlinks are never overwritten, even on repeat runs. Generate a new
filename to review changes or move the previous file before regeneration.

## See the result

For the mixed-stack PowerShell test (13 technology sections plus overwrite
protection), run `& .\scripts\test-demo.ps1 -KeepProject` from your source
checkout after installing stack2rules. It prints the temporary output path
for inspection. Omit `-KeepProject` to clean up its temporary files afterward.

The [Next.js example](examples/nextjs/CLAUDE.example.md) includes dedicated
Next.js, React, Tailwind CSS and TypeScript guidance. For example:

```markdown
## Next.js

- Inspect the installed Next.js version and router before editing: preserve App Router or Pages Router conventions.
- For App Router, keep components on the server by default and use 'use client' only at interactive boundaries; never expose server secrets to clients.
```

There are also complete [Django](examples/django/CLAUDE.example.md) and
[React + FastAPI](examples/fullstack/CLAUDE.example.md) examples. These use
synthetic manifests; no example dependencies need to be installed.

```sh
stack2rules --dir examples/nextjs --output CLAUDE.preview.md
python scripts/check_examples.py
```

## Detection

| Root file | Fields inspected for dependencies |
| --- | --- |
| `package.json` | dependencies, devDependencies, peerDependencies, optionalDependencies |
| `requirements.txt` | Named requirements, extras, version constraints and named direct references |
| `pyproject.toml` | PEP 621 dependencies/extras, dependency-groups, Poetry dependencies and groups |

Supported rules: Python, Node.js, FastAPI, Django, Pandas, React, Next.js,
Tailwind CSS, TypeScript, Vue, Express, Vitest, Flask, SQLAlchemy, pytest,
Pydantic and NumPy. Python dependency names are normalized case-insensitively,
with dots, underscores and hyphens treated equivalently.

Detection reports declared packages, including optional and development groups;
environment markers are not evaluated. Framework versions are not inferred.
Rules explicitly direct assistants to inspect installed versions before using
version-specific APIs. Unknown packages and sensitive metadata are ignored.
An empty project still receives general engineering and privacy guidance.

## Safety and limitations

- Reads only the three exact filenames above in the chosen root; never walks
  directories, `.git`, `node_modules`, virtual environments or monorepo children.
  Run separately in each workspace/package to detect its stack.
- Explicitly excludes `.git` and `.env*` path components. Manifest symlinks,
  devices, directories and files over 1 MiB are skipped.
- Does not inspect `.env`, lockfiles, scripts, credentials or private-key files.
  JSON/TOML manifests are parsed in memory, but only allowlisted dependency
  names are used. Secret keys/values, URLs and arbitrary text are never rendered
  or echoed in parser diagnostics.
- Malformed JSON/TOML, invalid UTF-8, unavailable files and excessive nesting
  are skipped with sanitized warnings; missing manifests are normal.
- Never follows requirements `-r`/`-c` includes, editable paths or bare URLs,
  evaluates dynamic Python metadata, or fetches remote dependencies.
- Writes to a temporary file, flushes it, then atomically publishes using a
  no-clobber hard link. Existing destinations are preserved. Local filesystems
  supporting hard links are required; there is no unsafe overwrite fallback.
  Temporary files are removed after success or handled errors.
- Assumes the project directory is not concurrently modified by an adversarial
  process. This is a local developer utility, not a filesystem security sandbox.

Exit codes: `0` generated; `1` unsafe/unavailable path, existing output or write
failure; `2` invalid command-line arguments. Skipped manifests alone do not fail
generation. Output is deterministic, UTF-8 Markdown without timestamps or paths.

## Architecture and testing

- `cli.py`: arguments, output validation and safe publication.
- `parsers.py`: bounded reads and dependency-name detection.
- `templates.py`: curated rules and deterministic Markdown compilation.
- `tests/test_stack2rules.py`: standard-library regression tests.

After installation:

```sh
python -m unittest discover -s tests -v
python scripts/check_examples.py
```

To add a framework, register its exact package name in the appropriate parser
mapping, add the corresponding `RULES` entry, and cover detection in tests.

Offline installation is possible when a compatible setuptools is already
available in the active environment:

```sh
python -m pip install --no-index --no-build-isolation --no-deps -e .
```

The included [GitHub Actions workflow](.github/workflows/ci.yml) is configured
for Python 3.11–3.14 on Linux, macOS and Windows. It runs tests with and without
site packages, checks examples, builds a wheel and tests an isolated install.
See the [Actions page](https://github.com/Shadowsama20/stack2rules/actions) for
the current results. Actions are pinned to commit SHAs, use a read-only
token and do not publish packages.

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, testing and framework additions.
Distributed under the [MIT license](LICENSE). See [CHANGELOG.md](CHANGELOG.md)
for release notes and [RELEASE.md](RELEASE.md) for the first-publication steps.
