# File: satellite.py
# Creation: Saturday January 23rd 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


# Basic imports
from abc import ABC

# GNSS Tools
from gnsstools.gnsstime import to_gnsstime, gnsstime


class Satellite(ABC):
    def __init__(self, prn, date):
        print(date)
        self._prn = prn
        self._date = to_gnsstime(date)

    @property
    def system(self):
        raise AttributeError("This attribute was not set. Please open an issue.")

    @property
    def prn(self):
        return self._prn

    @property
    def date(self):
        return self._date

    @classmethod
    def from_dataframe(cls, *args, **kwargs):
        raise NotImplementedError("This method is currently not available. Make a PR if you wish to update gnsstools.")

    def position(self, *args, **kwargs):
        raise NotImplementedError("This method is currently not available. Make a PR if you wish to update gnsstools.")
