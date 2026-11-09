# Release process

[v1.0.0](https://github.com/Shadowsama20/stack2rules/releases/tag/v1.0.0) was
published on 2026-11-09 with a wheel, source archive and SHA-256 checksums.
See VALIDATION.md for the tested commit and hosted results.

## Repeat the tests

From an activated source checkout:

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python scripts/check_examples.py
python -m pip wheel --no-deps --wheel-dir dist .
python scripts/check_wheel.py
```

On PowerShell, also run `& .\scripts\test-demo.ps1 -KeepProject`.

## Future releases

The release workflow is deliberately scoped to v1.0.0. It runs after successful
main-branch push CI, checks out that exact tested commit, builds and verifies
assets, and publishes only when the release does not already exist. It never
replaces existing release assets. Later successful CI runs skip publication.

For a future version, update package metadata, changelog, release notes and the
workflow's version checks, tag and concurrency group together. Review the
changes before pushing and wait for the new commit's CI. Never retag an existing
release to different source. If publication fails, inspect the workflow logs
and any draft release before retrying.

## PyPI is separate

This GitHub release does not publish to PyPI. Verify package-name availability
and configure the appropriate PyPI account or Trusted Publisher before adding
a registry publishing workflow. Do not claim `pip install stack2rules` works
until the intended package has actually been published there.
