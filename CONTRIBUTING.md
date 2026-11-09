# Contributing to stack2rules

Useful contributions include reproducible bug reports, missing dependency
mappings, clearer rules, documentation and portability fixes. Small, focused
pull requests are welcome. Be respectful and explain technical disagreements.

## Set up locally

Use Python 3.11 or later. From an extracted source archive or your fork:

```sh
python -m venv .venv
```

Activate with `source .venv/bin/activate` on macOS/Linux, or
`.venv\Scripts\Activate.ps1` in Windows PowerShell. Then run:

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python scripts/check_examples.py
```

The runtime and tests use only the Python standard library. Pip/setuptools
are installation/build tools. Do not add runtime dependencies.

## Propose a change

1. Check existing issues and pull requests. For a large change, discuss the
   problem in an issue before implementing it.
2. Fork the repository and create a descriptive branch.
3. Keep the change focused; update documentation for any changed behavior.
4. Add regression coverage for behavioral fixes. Use temporary directories
   and sanitized fixtures; never commit real project credentials.
5. Run the test suite and example verification, then open a pull request
   explaining the problem, change, tests and remaining limitations.

AI-assisted contributions are welcome. Contributors remain responsible for
understanding, reviewing and testing submitted code. Describe material AI
assistance in the pull request; do not claim checks you did not run.

## Add a supported technology

- Add the exact dependency name and display label to `NODE_PACKAGES` or
  `PYTHON_PACKAGES` in `src/stack2rules/parsers.py`.
- Add concise, practical rules under that label in `templates.py`. Make advice
  conditional where framework major versions differ.
- Test detection from an appropriate manifest, including false-positive cases.
- Update the supported list in `README.md`. If expected example output changes,
  run `python scripts/check_examples.py --write` and review every changed line.

Do not infer frameworks from descriptions, scripts, arbitrary metadata or
secret-bearing values. Do not execute project code or follow requirements
includes. Preserve deterministic output and existing files.

## Report a bug

Include the Python version, operating system, command, expected result and a
minimal sanitized manifest. Remove tokens, private URLs, usernames and project
paths from reports. If the issue exposes credentials, avoid public reproduction
details; use GitHub's private vulnerability reporting if the repository has
enabled it. Never post actual credentials.

## License

Contributions are distributed under this project's [MIT license](LICENSE).
