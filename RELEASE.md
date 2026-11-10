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

## PyPI publication

Version 1.0.0 was published on 2026-11-10 at
https://pypi.org/project/stack2rules/1.0.0/.

The `.github/workflows/pypi.yml` workflow downloads the tested GitHub release
assets, verifies their pinned SHA-256 hashes and publishes through PyPI Trusted
Publishing. Its publisher uses owner `Shadowsama20`, repository `stack2rules`,
workflow `pypi.yml` and environment `pypi`; no manually stored API token is needed.

This workflow is scoped to version 1.0.0. For a future release, update the
version, asset filenames and verified checksums before running it. Do not rerun
it merely to replace an existing PyPI file. Check publication status after any
partial failure before retrying.
