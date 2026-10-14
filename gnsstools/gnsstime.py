# File: time.py
# Creation: Saturday January 23rd 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


import calendar
import math
from datetime import datetime, timedelta, tzinfo

import numpy as np

__all__ = ["gnsstime"]


SECONDS_2000 = 946_728_000.0  # Seconds from 1970-01-01T00:00:00 to 2000-01-01T00:00:00 (UTC)
MJD_2000 = 51_544.5  # Modified Julian Day at 2000-01-01T00:00:00 (UTC)
JD = 2_400_000.5  # Julian Day starting at noon on Monday, January 1, 4713 BC
JD_2000 = 2_451_545.0  # Julian Day at 2000-01-01T00:00:00 (UTC)
JD_1950 = 2_433_282.50  # Julian Day at 1950-01-01T00:00:00 (UTC)
SESSIONS = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "0",
]


def to_gnsstime(element: object) -> "gnsstime":
    # `gnsstime` and `pandas.Timestamp` are both `datetime` subclasses.
    if isinstance(element, datetime):
        pass

    elif isinstance(element, np.datetime64):
        # `item` gives a datetime for microsecond values, an int for nanosecond ones, None for NaT.
        value = element.astype("datetime64[us]").item()
        if not isinstance(value, datetime):
            raise ValueError(f"The element to be converted to gnsstime is not a valid date. Got {element!r}.")
        element = value

    else:
        raise ValueError(f"The element to be converted to gnsstime is unknown. Got type {type(element)}.")

    return gnsstime(
        year=element.year,
        month=element.month,
        day=element.day,
        hour=element.hour,
        minute=element.minute,
        second=element.second,
        microsecond=element.microsecond,
        tzinfo=element.tzinfo,
        fold=element.fold,
    )


class gnsstime(datetime):
    r"""Defines GNSS time, providing built-in functions to fasten date conversion.

    The year, month and day arguments are required. tzinfo may be None, or an
    instance of a tzinfo subclass. The other arguments may be ints, floats or strings (as read from RINEX files):
    two-digit years from 00 to 79 are in the 2000s and from 80 to 99 in the 1900s, and the fractional part of the
    day, hour, minute and second is carried to the smaller units, rounded to the microsecond.

    .. note::
        This class inherits from ``datetime`` class.

    .. seealso::
        See the `datetime documentation <https://docs.python.org/fr/3/library/datetime.html>`__
        for more details.

    * :attr:`year` (int): The year of the gnss' clock.

    * :attr:`month` (int, optional): The month of the gnss' clock. Values must be between :math:`[1, 12]`.
        Defaults to ``1``.

    * :attr:`day` (int, optional): The day of the gnss' clock. Values must be between :math:`[1, 31]`, depending on the month.
        Defaults to ``1``.

    * :attr:`hour` (int, optional): The hour of the gnss' clock. Values must be between :math:`[0, 23]`.
        Defaults to ``0``.

    * :attr:`minute` (int, optional): The minute of the gnss' clock. Values must be between :math:`[0, 59]`.
        Defaults to ``0``.

    * :attr:`second` (int, optional): The second of the gnss' clock. Values must be between :math:`[0, 59]`.
        Defaults to ``0``.

    * :attr:`microsecond` (int, optional): The microsecond of the gnss' clock. Values must be between :math:`[0, 999999]`.
        Defaults to ``0``.

    """

    def __new__(
        cls,
        year: int | float | str | bytes,
        month: int | float | str | None = None,
        day: int | float | str | None = None,
        hour: int | float | str = 0,
        minute: int | float | str = 0,
        second: int | float | str = 0,
        microsecond: int | float = 0,
        tzinfo: tzinfo | None = None,
        *,
        fold: int = 0,
    ) -> "gnsstime":
        # `pickle` and `copy` rebuild a datetime from its packed state, followed by its tzinfo in place of the month.
        if isinstance(year, bytes):
            return datetime.__new__(cls, year, month)  # type: ignore[call-arg,arg-type]
        if month is None or day is None:
            raise TypeError("gnsstime needs a year, a month and a day.")

        # Format the year, in case its a two digit number, as in RINEX files.
        year = int(year)
        if year < 80:
            year += 2000
        elif year < 100:
            year += 1900

        # Validate the whole part of each argument like datetime does, then carry their fractional parts
        # (i.e. second=1.9 -> second=1, microsecond=900000).
        day, hour, minute, second, microsecond = (
            float(day),
            float(hour),
            float(minute),
            float(second),
            float(microsecond),
        )
        whole = datetime(
            year,
            int(month),
            math.floor(day),
            math.floor(hour),
            math.floor(minute),
            math.floor(second),
            math.floor(microsecond),
        )
        date = whole + timedelta(
            days=day % 1, hours=hour % 1, minutes=minute % 1, seconds=second % 1, microseconds=microsecond % 1
        )
        return datetime.__new__(
            cls,
            date.year,
            date.month,
            date.day,
            date.hour,
            date.minute,
            date.second,
            date.microsecond,
            tzinfo,
            fold=fold,
        )

    @property
    def session(self) -> str:
        return SESSIONS[int(round(self.hour))]

    @property
    def mjd(self) -> float:
        r"""Get the Modified Julian Day (MJD) relative to 2000-01-01T00:00:00 (UTC).

        Returns:
            float
        """
        delta = self - DATETIME_1970
        seconds = delta.total_seconds()
        return (seconds - SECONDS_2000) / 86_400 + MJD_2000

    @property
    def jd(self) -> float:
        r"""Get the Julian Day (JD) from a UTC datetime.

        Returns:
            float
        """
        return self.mjd + JD

    @property
    def jd50(self) -> float:
        r"""Get the Julian Day (JD) relative to 1950-01-01T00:00:00 (UTC).

        Returns:
            float
        """
        return self.jd - JD_1950

    @property
    def seconds0(self) -> float:
        r"""Get the number of seconds from :math:`GPS_{origin}`,
        defined at 1980-01-06T00:00:00 (UTC).

        Returns:
            float
        """
        return (self - DATETIME_GPS0).total_seconds()

    @property
    def days0(self) -> int:
        r"""Get the number of days from :math:`GPS_{origin}`,
        defined at 1980-01-06T00:00:00 (UTC).

        Returns:
            int
        """
        seconds = self.seconds0
        return math.floor(seconds / 86_400.0)

    @property
    def weeks0(self) -> int:
        r"""Get the number of weeks from :math:`GPS_{origin}`,
        defined at 1980-01-06T00:00:00 (UTC).

        Returns:
            int
        """
        seconds = self.seconds0
        return math.floor(seconds / (86_400.0 * 7))

    @property
    def sow(self) -> float:
        r"""Get the second of the current week.

        Returns:
            float
        """
        return self.seconds0 - self.weeks0 * 604_800.0

    @property
    def sod(self) -> float:
        r"""Get the second of the current day.

        Returns:
            float
        """
        seconds = (self.hour * 60 + self.minute) * 60 + self.second + self.microsecond / 1e6
        return seconds

    @property
    def doy(self) -> int:
        r"""Get the day of the current year.

        Returns:
            int
        """
        days = self.day
        year = self.year
        for month in range(1, self.month):
            days += calendar.monthrange(year, month)[1]
        return math.floor(days)

    @property
    def woy(self) -> int:
        r"""Get the week of the current year.

        Returns:
            float
        """
        days = self.doy
        weeks, _ = divmod(days, 7)
        return math.floor(weeks)

    @classmethod
    def fromdoy(cls, year: int, doy: int = 1, sod: float = 0) -> "gnsstime":
        """Generate a ``gnsstime`` object from a year, the day of year, and optionally second of day.

        Args:
            year (int): The year of the date.
            doy (int, optional): Day of year. Values must be between :math:`[1, 356]` depending on the year.
                Defaults to ``1``.
            sod (int, optional): Seconds of the day. Values must be between :math:`[0, 86399]`.
                Defaults to 0.

        Returns:
            gnsstime
        """
        return gnsstime(year, 1, 1) + timedelta(days=doy - 1, seconds=sod)

    @classmethod
    def frommjd(cls, mjd: float) -> "gnsstime":
        """Generate a ``gnsstime`` object from a Modified Julian Day.

        Args:
            mjd (float): The Modified Julian Day (MJD).

        Returns:
            gnsstime
        """
        return gnsstime(2000, 1, 1, 12) + timedelta(days=mjd - MJD_2000)

    @classmethod
    def fromjd(cls, jd: float) -> "gnsstime":
        """Generate a ``gnsstime`` object from a Julian Day.

        Args:
            mjd (float): The Julian Day (JD).

        Returns:
            gnsstime
        """
        return gnsstime.frommjd(jd - JD)

    @classmethod
    def fromjd50(cls, jd50: float) -> "gnsstime":
        """Generate a ``gnsstime`` object from a Julian Day at 1950.

        Args:
            mjd (float): The Julian Day at 1950 (JD50).

        Returns:
            gnsstime
        """
        jd = jd50 + JD_1950
        return gnsstime.fromjd(jd)

    @classmethod
    def fromdatetime64(cls, datetime64: np.datetime64) -> "gnsstime":
        """Generate a ``gnsstime`` object from a numpy datetime64.

        Args:
            mjd (float): The numpy datetime.

        Returns:
            gnsstime
        """
        return to_gnsstime(datetime64)


# Reference epochs, as gnsstime so that they can be subtracted from one.
DATETIME_1970 = gnsstime(1970, 1, 1, 0, 0, 0, 0)
DATETIME_GPS0 = gnsstime(1980, 1, 6, 0, 0, 0, 0)
DATETIME_2000 = gnsstime(2000, 1, 1, 0, 0, 0, 0)
