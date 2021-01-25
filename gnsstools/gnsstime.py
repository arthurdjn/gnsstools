# File: time.py
# Creation: Saturday January 23rd 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


# Basic imports
from datetime import datetime
import calendar
import math


__all__ = [
    "gnsstime"
]


DATETIME_1970 = datetime(1970, 1, 1, 0, 0, 0, 0)
DATETIME_GPS0 = datetime(1980, 1, 6, 0, 0, 0, 0)
DATETIME_2000 = datetime(2000, 1, 1, 0, 0, 0, 0)
SECONDS_2000 = 946_728_000.0  # Seconds from 1970-01-01T00:00:00 to 2000-01-01T00:00:00 (UTC)
MJD_2000 = 51_544.5   # Modified Julian Day at 2000-01-01T00:00:00 (UTC)
JD = 2_400_000.5  # Julian Day
JD_2000 = 2_451_545.0  # Julian Day at 2000-01-01T00:00:00 (UTC)
JD_1950 = 2_433_282.50  # Julian Day at 1950-01-01T00:00:00 (UTC)
SESSIONS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', '0']


class gnsstime(datetime):
    r"""Defines GNSS time, providing built-in functions to fasten date conversion.

    The year, month and day arguments are required. tzinfo may be None, or an
    instance of a tzinfo subclass. The remaining arguments may be ints.

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

    def __new__(cls, *args, **kwargs):
        return datetime.__new__(cls, *args, **kwargs)

    @property
    def session(self):
        return SESSIONS[int(round(self.hour))]

    @property
    def mjd(self):
        r"""Get the Modified Julian Date (MJD) relative to 2000-01-01T00:00:00 (UTC).

        Returns:
            float
        """
        delta = self - DATETIME_1970
        seconds = delta.total_seconds()
        return (seconds - SECONDS_2000) / 86_400 + MJD_2000

    @property
    def jd(self):
        r"""Get the Julian Date (JD) from a UTC datetime.

        Returns:
            float
        """
        return self.mjd + JD

    @property
    def jd50(self):
        r"""Get the Julian Date (JD) relative to 1950-01-01T00:00:00 (UTC).

        Returns:
            float
        """
        return self.jd - JD_1950

    @property
    def second0(self):
        r"""Get the number of seconds from :math:`GPS_{origin}`, 
        defined at 1980-01-06T00:00:00 (UTC).

        Returns:
            float
        """
        return (self - DATETIME_GPS0).total_seconds()

    @property
    def day0(self):
        r"""Get the number of days from :math:`GPS_{origin}`, 
        defined at 1980-01-06T00:00:00 (UTC).

        Returns:
            int
        """
        seconds = self.second0
        return math.floor(seconds / 86_400.0)

    @property
    def week0(self):
        r"""Get the number of weeks from :math:`GPS_{origin}`, 
        defined at 1980-01-06T00:00:00 (UTC).

        Returns:
            int
        """
        seconds = self.second0
        return math.floor(seconds / (86_400.0 * 7))

    @property
    def sow(self):
        r"""Get the second of the current week. 

        Returns:
            float
        """
        days = self.doy
        _, days = divmod(days, 7)
        seconds = ((days * 24 + self.hour) * 60 + self.minute) * 60 + self.second + self.microsecond / 1e6
        return seconds

    @property
    def sod(self):
        r"""Get the second of the current day. 

        Returns:
            float
        """
        seconds = (self.hour * 60 + self.minute) * 60 + self.second + self.microsecond / 1e6
        return seconds

    @property
    def doy(self):
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
    def woy(self):
        r"""Get the week of the current year. 

        Returns:
            float
        """
        days = self.doy
        weeks, _ = divmod(days, 7)
        return math.floor(weeks)

    @classmethod
    def fromdoy(cls, year, doy=1, sod=0):
        """Generate a ``gnsstime`` object from a year, the day of year, and optionally second of day.

        Args:
            year (int): The year of the date.
            doy (int, optional): Day of year. Values must be between :math:`[1, 356]` depending on the year. 
                Defaults to ``1``.
            sod (int, optional): [description]. Values must be between :math:`[0, 86399]`.
                Defaults to 0.

        Returns:
            gnsstime
        """
        # Find the day and month
        month = 1
        while month <= 12 and doy - calendar.monthrange(year, month)[1] > 0:
            doy -= calendar.monthrange(year, month)[1]
            month += 1
        day = doy

        # Find the hour, minute, second, microsecond (if `sod` was a float)
        hour, rest = divmod(sod, 3600)
        minute, second = divmod(rest, 60)
        microsecond, second = math.modf(second)

        # Convert to integers
        month = math.floor(month)
        day = math.floor(day)
        hour = math.floor(hour)
        minute = math.floor(minute)
        second = math.floor(second)
        microsecond = math.floor(microsecond * 1e6)

        return gnsstime(year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=microsecond)

    @classmethod
    def frommjd(cls, mjd):
        """Generate a ``gnsstime`` object from a Modified Julian Date.

        Args:
            mjd (float): The Modified Julian Date (MJD).

        Returns:
            gnsstime
        """
        # Seconds from 1970-01-01T00:00:00
        seconds = (mjd - MJD_2000) * 86_400 + SECONDS_2000
        return gnsstime.fromtimestamp(seconds)

    @classmethod
    def fromjd(cls, jd):
        """Generate a ``gnsstime`` object from a Julian Date.

        Args:
            mjd (float): The Julian Date (JD).

        Returns:
            gnsstime
        """
        return gnsstime.frommjd(jd - JD)
