# First public release

The source repository is [Shadowsama20/stack2rules](https://github.com/Shadowsama20/stack2rules).
The first tagged release and PyPI publication are still pending. A local test
pass is not a GitHub CI result, and a built wheel is not a PyPI publication.

## Work from the published source

```sh
git clone https://github.com/Shadowsama20/stack2rules.git
cd stack2rules
python -m venv .venv
```

Activate the environment as described in CONTRIBUTING.md, then install with
`python -m pip install -e .`. Follow the repository's existing history when
pushing updates; do not force-push to replace it.

## Validate before tagging

1. Wait for the `CI` workflow to finish successfully on GitHub. It targets
   Python 3.11–3.14 on Linux, macOS and Windows; skipped platform-specific
   symlink tests are reported by unittest.
2. Inspect the generated examples and verify the MIT license attribution.
3. Build and test the distributable in an activated environment:

```sh
python -m unittest discover -s tests -v
python scripts/check_examples.py
python -m pip wheel --no-deps --wheel-dir dist .
python scripts/check_wheel.py
```

4. Replace the pending status in `CHANGELOG.md` with the actual release date.
   Confirm that the repository/issue URLs in `pyproject.toml` are correct.
5. Commit those release metadata changes and wait for CI on that exact commit.
6. Create a GitHub release tagged `v1.0.0` from that commit. Attach the tested
   wheel and use the changelog for release notes. Do not mark it released before
   the release is actually published.

## Registry publication is separate

Do not claim `pip install stack2rules` works until the intended package has
actually been published. Check PyPI name availability and account ownership
before configuring a publishing workflow. The included workflow tests/builds;
it has no publication credentials or automatic release action.
