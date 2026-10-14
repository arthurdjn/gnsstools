# Contributing to gnsstools

If you are interested in contributing to `gnsstools`, your contributions will likely fall into one of the following
two categories:

1. You want to implement a new feature:
   - In general, we accept any feature that fits the scope of this package: reading and processing GNSS files and data.
     If you are unsure about the design of your feature, post about it in an issue first.
1. You want to fix a bug:
   - Feel free to send a Pull Request (PR) any time you encounter a bug. Please provide a clear and concise description
     of what the bug was. If you are unsure whether it is a bug at all, or how to fix it, post about it in an issue.

Once you finish implementing a feature or a bug fix, please send a PR to https://github.com/arthurdjn/gnsstools.

## Developing gnsstools

1. Fork and clone the repository:

   ```bash
   git clone https://github.com/<your_username>/gnsstools
   cd gnsstools
   ```

1. Install the package in editable mode together with its extras and the development tools, using
   [`uv`](https://docs.astral.sh/uv/):

   ```bash
   make install  # or: uv sync --all-extras
   ```

   `uv` creates the environment in `.venv` with the Python version of `.python-version` (the oldest one we support),
   and installs the exact versions pinned in `uv.lock`. If you change the dependencies in `pyproject.toml`, run
   `make lock` and commit `uv.lock`.

1. Ensure that you have a working installation by running the entire test suite:

   ```bash
   make test
   ```

Run `make help` to list every command.

## Unit Testing

The test suite is located under `tests/`, with small excerpts of real RINEX and SP3 files under `tests/data/` (see its
README for where they come from). Run the entire test suite with

```bash
make test
```

or a single file with, *e.g.*, `uv run --no-sync pytest tests/test_rinex.py`.

Known bugs have a test marked `xfail`, with the reason in the marker. The markers are strict: once you fix a bug, its
test passes, pytest reports it as an unexpected pass, and you should remove the marker in the same PR.

## Continuous Integration

`gnsstools` uses [GitHub Actions](https://github.com/arthurdjn/gnsstools/actions) for continuous integration.
Every pull request is checked against the project guidelines:

1. Ensure that your code is formatted, linted and typed correctly. We use [`ruff`](https://docs.astral.sh/ruff/) and
   [`mypy`](https://mypy-lang.org/) in strict mode, on the source code and the tests:

   ```bash
   make format
   make lint
   make type
   ```

1. Ensure that the entire test suite passes, on every supported Python version (3.10 to 3.14) and with the lowest
   versions of the dependencies declared in `pyproject.toml`.
   Please feel encouraged to provide a test with your submitted code.

1. Give your PR a [Conventional Commits](https://www.conventionalcommits.org/) title, *e.g.*,
   `fix: read the RINEX 2 navigation records with their own column offsets`. The allowed types are `feat`, `fix`,
   `docs`, `chore`, `refactor`, `perf`, `test`, `build`, `ci` and `revert`, and the subject starts with a lowercase
   character.

1. Add your feature / bug fix to the [`CHANGELOG.md`](CHANGELOG.md), under the `Unreleased` section.
   If multiple PRs move towards integrating a single feature, it is advised to group them together into one bullet
   point. Changes that do not affect users (CI, refactoring) can skip it with the `skip-changelog` label.

## Releasing

1. Bump the version in `pyproject.toml` (`uv version --bump patch`, `minor` or `major`) and move the `Unreleased`
   section of the changelog under the new version.
1. Merge, then tag the commit and push the tag:

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

The `Publish` workflow checks that the tag matches the version, publishes the distributions to PyPI with
[trusted publishing](https://docs.pypi.org/trusted-publishers/) and creates the GitHub release.

*This guide is adapted from the [PyG contributing guide](https://github.com/pyg-team/pytorch_geometric/blob/master/.github/CONTRIBUTING.md) (MIT License).*
