# Reproducible examples

These are small synthetic detection fixtures, not runnable applications.
Do not install their dependencies. Their versions illustrate manifest syntax,
not supported-version recommendations. Detection never installs these packages.

| Example | Input | Generated output |
| --- | --- | --- |
| Next.js frontend | [package.json](nextjs/package.json) | [CLAUDE.example.md](nextjs/CLAUDE.example.md) |
| Django + data analysis | [pyproject.toml](django/pyproject.toml) | [CLAUDE.example.md](django/CLAUDE.example.md) |
| React + FastAPI | [package.json](fullstack/package.json), [requirements.txt](fullstack/requirements.txt) | [CLAUDE.example.md](fullstack/CLAUDE.example.md) |

After installing stack2rules, try this from the repository root:

```sh
stack2rules --dir examples/nextjs --output CLAUDE.preview.md
```

The preview should match the committed `CLAUDE.example.md`. A repeat invocation
refuses to overwrite the preview: remove your generated preview or choose a new
output filename. Preview files are ignored by Git.

Check every example without modifying the repository:

```sh
python scripts/check_examples.py
```

After an intentional template change, regenerate expected output with
`python scripts/check_examples.py --write`, review the diff, and commit it
together with the change. The normal check generates files in temporary
directories and compares them with committed examples.
