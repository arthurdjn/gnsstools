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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def select(self, system=None, prn=None, date=None):

        # Search for subsets in the dataframe.
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
        # The time coverage should be lower than 2 hours.
        if offset / 3600 > 2:
            return None
        # Get the data (remove NaNs).
        system, prn, date = self.index[np.argmin(deltas)]
        data = self.loc[system, prn, date].dropna()

        # Select the data corresponding to the element at `index`.
        arguments = {"prn": int(prn), "date": to_gnsstime(date)}
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def select(self):
        raise NotImplementedError


class PositionDataFrame(pd.DataFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def select(self):
        raise NotImplementedError
