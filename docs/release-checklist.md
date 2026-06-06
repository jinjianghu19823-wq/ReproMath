# Release Checklist

Use this checklist before tagging or publishing a ReproMath release.

## Version

- Confirm `pyproject.toml` has the intended version.
- Confirm `src/repromath/__init__.py` has the same `__version__`.
- Confirm `repromath --version` prints the same version.
- Confirm `CHANGELOG.md` has an entry for the release.

## Tests

- Run the full test suite:

```bash
python -m pytest
```

- Check that any warnings are understood and documented if relevant.

## CLI Smoke Tests

Run:

```bash
repromath --help
repromath init --help
repromath qa --help
repromath scaffold --help
repromath --version
```

Run the showcase QA:

```bash
cd examples/low-rank-tensor-pde
repromath qa project
```

## Documentation

- Check the README quickstart and 60-second demo.
- Check docs links in `README.md`.
- Check the showcase documentation.
- Confirm the project still states the non-goals clearly.

## GitHub

- Confirm the working tree is clean.
- Push the release branch.
- Open a small PR-sized change set.
- After merge, create a tag or release only when the milestone is ready.

