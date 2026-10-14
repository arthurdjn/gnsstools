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
- `NavigationDataFrame.select` takes the system, the PRN and the date as required arguments, and raises a `ValueError`
  instead of an `AssertionError` when the satellite is not in the DataFrame or its closest ephemeris is 2 hours or more
  away from the date.
- The data sources field of the Galileo navigation records is read into a `DataSources` column instead of `GPSWeek`,
  and `GALILEO` takes a `data_sources` argument instead of `gps_week`.
- `gnsstime` carries the fractional part of the day, hour, minute and second to the smaller units, as the README
  says (only seconds were), rounded to the microsecond. It raises a `TypeError` instead of returning `None` when the
  month or the day is missing.
- `gnsstime.frommjd`, `fromjd` and `fromjd50` no longer use `datetime.utcfromtimestamp`, deprecated since Python 3.12:
  they work for dates before 1970 on Windows.
- `Trilateration` raises a `ValueError` instead of an `AssertionError` for fewer than 4 satellites or a number of
  distances that does not match, and `Trilateration.optimize` stops when the update of the parameters is smaller than
  `epsilon` (in meters) rather than when the variance factor stops changing.
- `rinex.load` accepts `os.PathLike` paths, and reads the system of a RINEX 2 navigation file (GPS, GLONASS, ...)
  from its header instead of the last letter of its name.

### Fixed

- `Trilateration.optimize` stopped after one iteration with exactly 4 satellites (the variance factor divided by
  zero), and ignored its `epsilon` argument.
- `gnsstime.sow` counted the days from the day of the year modulo 7 instead of the start of the GPS week. It was only
  right in the years that start on a Monday (like 2018), and so were the positions of `get_satellite_position`.
- Copying or unpickling a `gnsstime` returned `None`.
- `gnsstime` read the two-digit years from 80 to 99 as years 80 to 99 instead of 1980 to 1999, and floored the
  fractional seconds (`second=1.001` gave 999 microseconds).
- `gnsstime.fromdoy` dropped the fractional part of the second of the day.
- `to_gnsstime` and `gnsstime.fromdatetime64` only converted nanosecond `datetime64` values.
- `NavigationDataFrame.select` returned a satellite without ephemeris when several records share the closest epoch,
  like the F/NAV and I/NAV messages of Galileo in the merged IGS files. It uses the first record.
- `get_satellite_position` used the data sources field as the week of Galileo satellites: their positions were off by
  a week of Earth rotation.
- The RINEX 2 and RINEX 3 observation readers no longer append the loss of lock indicator and the signal strength to
  the value (`125339261.645 6` was read `125339261.64506`). The RINEX 3 reader also read the values one column late,
  which cut the first digit of values with 10 integer digits, and the number of satellites of an epoch from 2
  characters instead of 3.
- RINEX 2 navigation files are read with the RINEX 2 column positions: records with a negative clock bias raised a
  `ValueError`, and the fields of the others were shifted by one character.
- `repr()` of a `GALILEO` satellite raised an `AttributeError`. Its `sv_heath` attribute is renamed `sv_health`.
- `repr()` of a satellite read through the base `Satellite.__repr__` now includes its `toc`.
- The `georinex` fallback of `rinex.load` returned the first satellite of the file only.
- `SyntaxWarning: invalid escape sequence` on import with Python 3.12+.
