import sys
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from gnsstools import gnsstime
from gnsstools.gnsstime import to_gnsstime

# 2018-10-12 is GPS week 2022, second of week 432000 (see the header of tests/data/COM20225_15M.SP3).
GPS_WEEK = 2022
GPS_SOW = 432_000.0

# Year, month, day, hour, minute and second.
DateArgs = tuple[int | str, int | str, int | str, int | str, int | str, int | str]


def test_is_a_datetime() -> None:
    date = gnsstime(2018, 10, 12, 1, 0, 15)
    assert isinstance(date, datetime)
    assert date == datetime(2018, 10, 12, 1, 0, 15)


@pytest.mark.parametrize(
    "args",
    [
        (2018, 10, 12, 1, 0, 15),
        (18, 10, 12, 1, 0, 15),
        ("18", "10", "12", "1", "0", "15.0"),
        ("2018", "10", "12", "01", "00", "15.0000000"),
    ],
)
def test_parses_strings_and_two_digit_years(args: DateArgs) -> None:
    assert gnsstime(*args) == datetime(2018, 10, 12, 1, 0, 15)


@pytest.mark.xfail(reason="Two-digit years from 80 to 99 are not mapped to 1980-1999")
def test_two_digit_years_of_the_previous_century() -> None:
    assert gnsstime(98, 1, 1).year == 1998


def test_fractional_seconds_become_microseconds() -> None:
    assert gnsstime(2018, 1, 1, 0, 0, 5.5) == datetime(2018, 1, 1, 0, 0, 5, 500_000)


@pytest.mark.xfail(reason="Fractional seconds are floored: 1.001 s gives 999 microseconds")
def test_fractional_seconds_are_rounded() -> None:
    assert gnsstime(2018, 1, 1, 0, 0, 1.001).microsecond == 1_000


@pytest.mark.xfail(reason="Fractional days, hours and minutes are truncated instead of carried, unlike the README says")
def test_fractional_hours_are_carried() -> None:
    assert gnsstime(2018, 1, 1, 12.5) == datetime(2018, 1, 1, 12, 30)


def test_julian_days_of_reference_epochs() -> None:
    j2000 = gnsstime(2000, 1, 1, 12)
    assert j2000.mjd == 51_544.5
    assert j2000.jd == 2_451_545.0
    assert gnsstime(1950, 1, 1).jd50 == 0.0


@pytest.mark.parametrize("date", [gnsstime(2000, 1, 1, 12), gnsstime(2018, 10, 12, 1, 0, 15, 250_000)])
def test_round_trips_through_julian_days(date: gnsstime) -> None:
    assert abs((gnsstime.frommjd(date.mjd) - date).total_seconds()) < 1e-3
    assert abs((gnsstime.fromjd(date.jd) - date).total_seconds()) < 1e-3
    assert isinstance(gnsstime.frommjd(date.mjd), gnsstime)


@pytest.mark.xfail(
    sys.platform == "win32",
    raises=OSError,
    reason="frommjd goes through utcfromtimestamp, which rejects dates before 1970 on Windows",
    strict=False,
)
def test_from_julian_day_before_1970() -> None:
    assert gnsstime.fromjd50(0.0) == datetime(1950, 1, 1)


def test_gps_time() -> None:
    date = gnsstime(2018, 10, 12)
    assert date.weeks0 == GPS_WEEK
    assert date.days0 == GPS_WEEK * 7 + 5
    assert date.seconds0 == GPS_WEEK * 604_800 + GPS_SOW


def test_second_of_week_matches_sp3_header() -> None:
    assert gnsstime(2018, 10, 12).sow == GPS_SOW


@pytest.mark.xfail(reason="sow is derived from the day of year modulo 7, not from the start of the GPS week (Sunday)")
@pytest.mark.parametrize(
    ("date", "sow"),
    [(gnsstime(2021, 1, 1), 5 * 86_400.0), (gnsstime(2025, 6, 1, 0, 0, 30), 30.0)],
)
def test_second_of_week_counts_from_sunday(date: gnsstime, sow: float) -> None:
    assert date.sow == sow


def test_day_and_week_of_year() -> None:
    date = gnsstime(2018, 10, 12, 1, 0, 15.5)
    assert date.doy == 285
    assert date.woy == 40
    assert date.sod == 3_615.5
    # Hourly RINEX sessions are named from "a" (00h) to "x" (23h), e.g. edf1285b.18o starts at 01h.
    assert date.session == "b"


def test_from_day_of_year() -> None:
    assert gnsstime.fromdoy(2018, 285) == datetime(2018, 10, 12)
    assert gnsstime.fromdoy(2018, 285, 3_615) == datetime(2018, 10, 12, 1, 0, 15)
    assert gnsstime.fromdoy(2020, 366) == datetime(2020, 12, 31)


@pytest.mark.xfail(reason="fromdoy drops the fractional part of the second of day")
def test_from_day_of_year_keeps_microseconds() -> None:
    assert gnsstime.fromdoy(2018, 285, 3_615.5) == datetime(2018, 10, 12, 1, 0, 15, 500_000)


@pytest.mark.parametrize(
    "value",
    [
        datetime(2018, 10, 12, 1, 0, 15),
        pd.Timestamp("2018-10-12T01:00:15"),
        np.datetime64("2018-10-12T01:00:15.000000000"),
    ],
)
def test_to_gnsstime(value: object) -> None:
    date = to_gnsstime(value)
    assert isinstance(date, gnsstime)
    assert date == datetime(2018, 10, 12, 1, 0, 15)


@pytest.mark.xfail(raises=TypeError, reason="Only nanosecond datetime64 values are converted")
def test_to_gnsstime_from_microsecond_datetime64() -> None:
    assert to_gnsstime(np.datetime64("2018-10-12T01:00:15.000000")) == datetime(2018, 10, 12, 1, 0, 15)


def test_to_gnsstime_rejects_unknown_types() -> None:
    with pytest.raises(ValueError, match="unknown"):
        to_gnsstime("2018-10-12")
