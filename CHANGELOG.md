# Changelog

All notable changes to this project are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Removed

- The `Orbit` and `GNSSProcess` classes, with the `gnsstools.orbits` and `gnsstools.process` modules: they were written
  for a school assignment and need the private `gnsstoolbox` package, so `import gnsstools` failed without it (#1).
- The `gnsstools.logger` module, and `requirements.txt` (the dependencies are declared in `pyproject.toml`).

### Changed

- `import gnsstools` no longer writes a `gnss_toolbox.log` file in the working directory, and `rinex.load` no longer
  prints the header of the file (nor the navigation reader a line counter).
- `rinex.load` imports `georinex` only for the files that need it, and raises an `ImportError` with the install
  command when it is missing, instead of a `NameError`.
- The package is built from `pyproject.toml` and requires Python 3.10+, numpy 1.24+, pandas 2.0+ and shapely 2.0+.
  `georinex` is an optional extra: `pip install "gnsstools[georinex]"`.
- The package ships its type hints (`py.typed`), checked with `mypy --strict`.
- `ABCReader.read` and `Satellite.system` are abstract.
- `NavigationDataFrame.select` raises a `ValueError` when no date is given, instead of a `TypeError`.

### Fixed

- `repr()` of a `GALILEO` satellite raised an `AttributeError`. Its `sv_heath` attribute is renamed `sv_health`.
- `repr()` of a satellite read through the base `Satellite.__repr__` now includes its `toc`.
- The `georinex` fallback of `rinex.load` returned the first satellite of the file only.
- `SyntaxWarning: invalid escape sequence` on import with Python 3.12+.
