import copy
import pickle
from collections.abc import Callable
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


def test_two_digit_years_of_the_previous_century() -> None:
    assert gnsstime(98, 1, 1).year == 1998


def test_fractional_seconds_become_microseconds() -> None:
    assert gnsstime(2018, 1, 1, 0, 0, 5.5) == datetime(2018, 1, 1, 0, 0, 5, 500_000)


def test_fractional_seconds_are_rounded() -> None:
    assert gnsstime(2018, 1, 1, 0, 0, 1.001).microsecond == 1_000


def test_fractional_hours_are_carried() -> None:
    assert gnsstime(2018, 1, 1, 12.5) == datetime(2018, 1, 1, 12, 30)
    assert gnsstime(2018, 1, 2.5) == datetime(2018, 1, 2, 12)
    assert gnsstime(2018, 1, 1, 5.933, 4.36, 33.231) == datetime(2018, 1, 1, 6, 0, 53, 631_000)


def test_rounding_carries_to_the_next_day() -> None:
    assert gnsstime(2018, 12, 31, 23, 59, "59.9999999") == datetime(2019, 1, 1)


def test_invalid_dates() -> None:
    with pytest.raises(TypeError, match="year, a month and a day"):
        gnsstime(2018)
    with pytest.raises(ValueError, match="hour"):
        gnsstime(2018, 1, 1, 24)
    with pytest.raises(ValueError, match="day"):
        gnsstime(2018, 2, 29)


@pytest.mark.parametrize("copy_", [copy.copy, copy.deepcopy, lambda date: pickle.loads(pickle.dumps(date))])
def test_copy_and_pickle(copy_: Callable[[gnsstime], gnsstime]) -> None:
    date = gnsstime(2018, 10, 12, 1, 0, 15.25)
    copied = copy_(date)
    assert type(copied) is gnsstime
    assert copied == date


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


def test_from_julian_day_before_1970() -> None:
    assert gnsstime.fromjd50(0.0) == datetime(1950, 1, 1)


def test_gps_time() -> None:
    date = gnsstime(2018, 10, 12)
    assert date.weeks0 == GPS_WEEK
    assert date.days0 == GPS_WEEK * 7 + 5
    assert date.seconds0 == GPS_WEEK * 604_800 + GPS_SOW


def test_second_of_week_matches_sp3_header() -> None:
    assert gnsstime(2018, 10, 12).sow == GPS_SOW


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


def test_to_gnsstime_from_microsecond_datetime64() -> None:
    assert to_gnsstime(np.datetime64("2018-10-12T01:00:15.000000")) == datetime(2018, 10, 12, 1, 0, 15)


def test_to_gnsstime_rejects_unknown_types() -> None:
    with pytest.raises(ValueError, match="unknown"):
        to_gnsstime("2018-10-12")
    with pytest.raises(ValueError, match="not a valid date"):
        to_gnsstime(np.datetime64("NaT", "ns"))
