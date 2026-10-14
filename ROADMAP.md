# Roadmap

What `gnsstools` does today: read RINEX 2/3 observation, RINEX 3 navigation and SP3 files into pandas DataFrames,
convert dates between GNSS time representations (`gnsstime`), select a broadcast ephemeris, compute a GPS satellite
position from it, and solve a receiver position by least squares (`Trilateration`).

This page lists what is broken and what is missing, in the order we think it should be tackled. Pick anything, and
open an issue first for the larger items.

## Known bugs

Each bug below has a test marked `xfail` with the reason in the marker. The markers are strict: fixing a bug makes its
test pass, pytest then fails on the unexpected pass, and the fix removes the marker.

### Wrong or lost data (fix first)

| Bug | Where | Test |
| --- | --- | --- |
| RINEX 2 navigation records are sliced with the RINEX 3 column offsets, which are one character wider. Any record with a negative clock bias raises a `ValueError` (the sign lands in the date), and the other fields shift by one character. | `rinex/nav.py`, `RinexNavReader._extract_*_fields` and `read` | `test_rinex2_navigation_matches_rinex3` |
| The observation readers splice the loss of lock indicator and the signal strength digits into the value: `125339261.645 6` reads `125339261.64506`. The RINEX 3 reader also starts each value one column late, so values with 10 integer digits lose their first one. | `rinex/obs2.py` and `rinex/obs3.py`, `_read_obs` | `test_rinex2_observation_ignores_flags`, `test_rinex3_observation_ignores_flags` |
| `NavigationDataFrame.select` returns a satellite with an empty ephemeris (every field `None`) when the epoch has several records. Merged files such as the IGS `BRDC` ones have two for every Galileo epoch: the F/NAV and I/NAV messages. | `rinex/datasets.py`, `select` | `test_select_an_epoch_with_several_records` |
| `gnsstime.sow` counts days from the day of year modulo 7, not from the start of the GPS week (Sunday). It is only right in the years that start on a Monday (2018, 2024, ...). `get_satellite_position` rotates the orbit to ECEF with it, so positions outside those years are wrong. | `gnsstime.py`, `sow` | `test_second_of_week_counts_from_sunday` |
| The Galileo "data sources" field (258 for F/NAV, 517 for I/NAV) is read into the `GPSWeek` column, and `get_satellite_position` compares it to the GPS week, so it shifts Galileo positions by a week of Earth rotation. | `rinex/nav.py`, `_extract_e_fields` | `test_navigation_galileo_data_sources` |
| `camel2snake` maps `IODnav` and `BGDe5a`/`BGDe5b` to `io_dnav` and `bg_de5a`/`bg_de5b`, which `GALILEO` does not accept: `select` will raise a `TypeError` for Galileo once the duplicate epoch bug above is fixed. An explicit column to argument mapping would be sturdier than the regex. | `utils.py`, `camel2snake` | `test_camel2snake`, `test_every_navigation_field_is_a_satellite_argument` |

### `gnsstime`

| Bug | Test |
| --- | --- |
| Two-digit years from 80 to 99 stay in the first century: `gnsstime(98, 1, 1).year == 98` (the `else: 1900 + year` branch is a no-op). | `test_two_digit_years_of_the_previous_century` |
| Fractional seconds are floored, not rounded: `second=1.001` gives 999 microseconds. | `test_fractional_seconds_are_rounded` |
| Fractional days, hours and minutes are truncated, while the README says they are carried to the smaller units. | `test_fractional_hours_are_carried` |
| `fromdoy` drops the fractional part of the second of day. | `test_from_day_of_year_keeps_microseconds` |
| `to_gnsstime` and `fromdatetime64` only convert nanosecond `datetime64` values. | `test_to_gnsstime_from_microsecond_datetime64` |
| `frommjd` (and so `fromjd`, `fromjd50`) goes through `datetime.utcfromtimestamp`, deprecated since Python 3.12 and unable to handle dates before 1970 on Windows. Adding a `timedelta` to the 1970 epoch fixes both. | `test_from_julian_day_before_1970` (Windows) |

### Other

- `Trilateration` divides by zero with exactly 4 satellites (no redundancy): σ₀² is NaN and the iteration stops after
  one step (`test_recovers_position_and_clock[4]`).
- `NavigationDataFrame.select` validates its arguments with `assert`, which `python -O` removes. It should raise a
  `ValueError`.
- `gnsstime(2018)` returns `None` instead of raising, because `month` and `day` default to `None`.
- The RINEX 3 observation reader reads the number of satellites of an epoch from 2 characters instead of 3: epochs with
  100 satellites or more are misread.
- SP3 velocity records (`V`) become rows of their own, with the same index as the position rows, and their clock rate
  lands in the `Clock` column (`SP3Reader.read`).
- `rinex.load` accepts a `str` only (it calls `filename.endswith`), not a `pathlib.Path`, and tells GPS and GLONASS
  RINEX 2 navigation files apart by the last letter of the file name.

## Missing features

### Positions and clocks

The README lists satellite position, clock offset and pseudo-distance as in progress.

- **Satellite positions**: `Satellite.position` raises `NotImplementedError`. `satellites/funtional.py` (sic) already
  computes GPS positions from the broadcast ephemeris to about 1.5 m of the SP3 orbits (see
  `test_broadcast_orbit_matches_precise_orbit`). Wire it into `GPS.position`, then add Galileo (its own time scale and
  week), BeiDou (with the rotation of the GEO satellites) and GLONASS (numerical integration of the state vector, e.g.
  Runge-Kutta 4).
- **Precise positions from SP3**: Lagrange interpolation of the SP3 positions and clocks at any epoch.
- **Satellite clocks**: clock polynomial, relativistic correction and group delays (TGD, BGD).
- **Single point positioning**: the removed `GNSSProcess` class did it with the private `gnsstoolbox` package. Rebuild
  it on `Trilateration` and the satellite positions: emission time, Earth rotation during the signal travel time,
  ionosphere (Klobuchar, with the coefficients of the navigation header), troposphere (Saastamoinen), elevation mask and
  weights.
- **Coordinates**: ECEF to geodetic (WGS84) and back, local ENU frame, azimuth and elevation of a satellite.

### Time

- Time scales: GPS time, UTC (leap seconds, from the `LEAP SECONDS` header record), Galileo, BeiDou and GLONASS time.
  `gnsstime` is a naive `datetime` today and does not say which scale it is in.

### File formats

- Hatanaka-compressed RINEX (`.crx`, `.YYd`) and gzip / Unix compressed files. They currently go through the optional
  `georinex` fallback.
- RINEX 3 navigation records of BeiDou, QZSS, IRNSS and SBAS, which are skipped today.
- RINEX 4 navigation (new record types: ephemerides, system time offsets, Earth orientation, ionosphere).
- SP3-d, and the correlation records (`EP`, `EV`) of SP3.
- Clock RINEX, ANTEX, IONEX and SINEX.
- Writing RINEX and SP3 files.

### Readers and DataFrames

- Parse the rest of the RINEX headers into `df.attrs`: approximate position, antenna offsets, interval, time of first
  and last observation, leap seconds, ionospheric and time system corrections. Only the version, type, system and
  program records are read today, and nothing from the SP3 header (`SP3Reader._read_header` is never used).
- `ObservationDataFrame.select` and `PositionDataFrame.select` raise `NotImplementedError`.
- Store SP3 positions as `X`, `Y`, `Z` float columns in meters, rather than `shapely` points in kilometers. It would
  drop the `shapely` dependency and make the columns vectorizable.
- Parse the fixed-width records with NumPy or `pandas.read_fwf` instead of a Python loop with regular expressions: a
  day of 1 Hz observations is large.

## API cleanup

Each of these breaks the API, so they are best grouped in one release, with deprecated aliases for a while.

- PEP 8 names: `gnsstime` to `GNSSTime`, `GALILEO` and `GLONASS` to `Galileo` and `Glonass`, `satellites/funtional.py`
  to `functional.py`.
- Consistent DataFrame columns (`SVClockBias`) and satellite attributes (`sv_clock_bias`).
- One docstring style (Google, checked by ruff), in English (some are in French), with examples that run against
  `tests/data`.

## Project

- **First PyPI release**: the `gnsstools` name is free on PyPI. Add a trusted publisher for the `Publish` workflow (and
  a `pypi` environment on GitHub), bump the version and push a tag. Then switch the install instructions of the README
  to `pip install gnsstools`.
- **Documentation site**: the README used to link a Read the Docs site that never existed. An API reference generated
  from the docstrings and a few tutorials (reading files, orbits, positioning) would do.
- **Python 3.10** reaches its end of life in October 2026. Requiring 3.11 lets everyone get pandas 3 and the latest
  NumPy.
- Turn warnings into errors in pytest (`filterwarnings = ["error"]`) once `utcfromtimestamp` is gone.
- Clarify the copyright: `LICENSE` names the author, while several modules carry a `Copyright (c) 2021, Makina Corpus`
  header.
