# File: time.py
# Creation: Saturday January 23rd 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


# Basic imports
from datetime import datetime, timedelta
import calendar
import math
import numpy as np
import pandas as pd


__all__ = [
    "gnsstime"
]


DATETIME_1970 = datetime(1970, 1, 1, 0, 0, 0, 0)
DATETIME_GPS0 = datetime(1980, 1, 6, 0, 0, 0, 0)
DATETIME_2000 = datetime(2000, 1, 1, 0, 0, 0, 0)
SECONDS_2000 = 946_728_000.0  # Seconds from 1970-01-01T00:00:00 to 2000-01-01T00:00:00 (UTC)
MJD_2000 = 51_544.5   # Modified Julian Day at 2000-01-01T00:00:00 (UTC)
JD = 2_400_000.5  # Julian Day starting at noon on Monday, January 1, 4713 BC
JD_2000 = 2_451_545.0  # Julian Day at 2000-01-01T00:00:00 (UTC)
JD_1950 = 2_433_282.50  # Julian Day at 1950-01-01T00:00:00 (UTC)
SESSIONS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', '0']


def to_gnsstime(element):

    if isinstance(element, (datetime, gnsstime)):
        pass

    elif isinstance(element, pd.Timestamp):
        element = pd.to_datetime(element)
    
    elif isinstance(element, np.datetime64):
        element = datetime.utcfromtimestamp(element.astype('O') / 1e9)

    else:
        raise ValueError(f"The element to be converted to gnsstime is unknown. Got type {type(element)}.")

    return gnsstime(year=element.year, month=element.month, day=element.day,
                    hour=element.hour, minute=element.minute, second=element.second,
                    microsecond=element.microsecond, tzinfo=element.tzinfo,
                    fold=element.fold)
    

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

    def __new__(cls, year, month=None, day=None,
                hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0, **kwargs):

        # Return None if the date is not valid
        if year is None or month is None or day is None:
            return None

        # Convert the values to integer
        year = int(year)
        month = int(month)
        day = int(day)
        hour = int(hour)
        minute = int(minute)
        # Split microsecond from second (i.e. second=1.9 -> second=1, microsecond=900000)
        microsecond_, second = math.modf(float(second))
        microsecond_ = math.floor(microsecond_ * 1e6)
        second = math.floor(second)
        microsecond = math.floor(microsecond)

        # Use the microsecond provided with the second (if any)
        if microsecond_ > microsecond:
            microsecond = microsecond_

        # Format the year, in case its a two digit number.
        # See the format used in RINEX files and navigation elements for more details.
        if year < 80:
            year = 2000 + year
        else:
            1900 + year

        # Initialize from the parent method
        return datetime.__new__(cls, year, month=month, day=day,
                                hour=hour, minute=minute, second=second,
                                microsecond=microsecond,
                                tzinfo=tzinfo, fold=fold, **kwargs)

    @property
    def session(self):
        return SESSIONS[int(round(self.hour))]

    @property
    def mjd(self):
        r"""Get the Modified Julian Day (MJD) relative to 2000-01-01T00:00:00 (UTC).

        Returns:
            float
        """
        delta = self - DATETIME_1970
        seconds = delta.total_seconds()
        return (seconds - SECONDS_2000) / 86_400 + MJD_2000

    @property
    def jd(self):
        r"""Get the Julian Day (JD) from a UTC datetime.

        Returns:
            float
        """
        return self.mjd + JD

    @property
    def jd50(self):
        r"""Get the Julian Day (JD) relative to 1950-01-01T00:00:00 (UTC).

        Returns:
            float
        """
        return self.jd - JD_1950

    @property
    def seconds0(self):
        r"""Get the number of seconds from :math:`GPS_{origin}`, 
        defined at 1980-01-06T00:00:00 (UTC).

        Returns:
            float
        """
        return (self - DATETIME_GPS0).total_seconds()

    @property
    def days0(self):
        r"""Get the number of days from :math:`GPS_{origin}`, 
        defined at 1980-01-06T00:00:00 (UTC).

        Returns:
            int
        """
        seconds = self.seconds0
        return math.floor(seconds / 86_400.0)

    @property
    def weeks0(self):
        r"""Get the number of weeks from :math:`GPS_{origin}`, 
        defined at 1980-01-06T00:00:00 (UTC).

        Returns:
            int
        """
        seconds = self.seconds0
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
            sod (int, optional): Seconds of the day. Values must be between :math:`[0, 86399]`.
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
        microsecond, second = math.modf(second)
        microsecond = math.floor(microsecond * 1e6)
        return gnsstime(year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=microsecond)

    @classmethod
    def frommjd(cls, mjd):
        """Generate a ``gnsstime`` object from a Modified Julian Day.

        Args:
            mjd (float): The Modified Julian Day (MJD).

        Returns:
            gnsstime
        """
        # Seconds from 1970-01-01T00:00:00
        seconds = (mjd - MJD_2000) * 86_400 + SECONDS_2000
        return gnsstime.utcfromtimestamp(seconds)

    @classmethod
    def fromjd(cls, jd):
        """Generate a ``gnsstime`` object from a Julian Day.

        Args:
            mjd (float): The Julian Day (JD).

        Returns:
            gnsstime
        """
        return gnsstime.frommjd(jd - JD)

    @classmethod
    def fromjd50(cls, jd50):
        """Generate a ``gnsstime`` object from a Julian Day at 1950.

        Args:
            mjd (float): The Julian Day at 1950 (JD50).

        Returns:
            gnsstime
        """
        jd = jd50 + JD_1950
        return gnsstime.fromjd(jd)

    @classmethod
    def fromdatetime64(cls, datetime64):
        """Generate a ``gnsstime`` object from a numpy datetime64.

        Args:
            mjd (float): The numpy datetime.

        Returns:
            gnsstime
        """
        return gnsstime.utcfromtimestamp(datetime64.astype('O') / 1e9)
