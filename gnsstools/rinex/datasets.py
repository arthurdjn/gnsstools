# Encoding: UTF-8
# File: datasets.py
# Creation: Saturday January 30th 2021
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


# Basic imports
import numpy as np
import pandas as pd

# GNSS Tools
from gnsstools.satellites import GPS, GLONASS, GALILEO
from gnsstools.gnsstime import to_gnsstime
from gnsstools.utils import camel2snake


class NavigationDataFrame(pd.DataFrame):

    @property
    def _constructor(self):
        return NavigationDataFrame

    def select(self, system=None, prn=None, date=None, ignore_offset=False):

        # Make sure the arguments are available.
        systems = np.unique(self.index.get_level_values('System'))
        prns = np.unique(self.index.get_level_values('PRN'))
        assert system in systems, f"The provided system {system} was not found in the dataset. " \
                                  f"Available systems are {', '.join(systems)}."
        assert prn in prns, f"The provided PRN {prn} was not found in the dataset. " \
                            f"Available PRNs are {', '.join(prns.astype('str'))}."

        # Search for subsets in the dataframe (if valid arguments are provided).
        if prn is None:
            sub_df = self.loc[system]
        else:
            sub_df = self.loc[system, prn]

        # Find the closest time to the provided `date`.
        deltas = []
        for date_ in sub_df.index.get_level_values('Date'):
            date_ = to_gnsstime(date_)
            deltas.append(np.abs((date - date_).total_seconds()))
        offset = np.min(deltas)
        # Find the indexes of the sub dataframe
        if system is not None and prn is None:
            prn, date = sub_df.index[np.argmin(deltas)]
        elif system is not None and prn is not None:
            date = sub_df.index[np.argmin(deltas)]
        # The time coverage should be lower than 2 hours.
        if not ignore_offset:
            assert offset / 3600 < 2, f"The provided date does not overlap with dates from {system}{prn} satellite. " \
                                      f"There must be a time delta of 2h at least. " \
                                      f"Got a time delta of {offset / 3600:.2f} hours. " \
                                      f"The closest date is {date}. You can ignore this behavior with `ignore_offset=True`."
        # Get the row and drop NaNs
        data = self.loc[system, prn, date].squeeze()
        data = data.dropna()
        arguments = {"prn": int(prn), "toc": to_gnsstime(date)}
        for arg, value in zip(data.index, data.values):
            arguments[camel2snake(arg)] = value

        # Create a satellite instance.
        if system == "G":
            return GPS(**arguments)
        elif system == "R":
            return GLONASS(**arguments)
        elif system == "E":
            return GALILEO(**arguments)
        return None


class ObservationDataFrame(pd.DataFrame):

    @property
    def _constructor(self):
        return ObservationDataFrame

    def select(self):
        raise NotImplementedError


class PositionDataFrame(pd.DataFrame):

    @property
    def _constructor(self):
        return PositionDataFrame

    def select(self):
        raise NotImplementedError
