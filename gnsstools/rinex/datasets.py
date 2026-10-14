# Encoding: UTF-8
# File: datasets.py
# Creation: Saturday January 30th 2021
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


from datetime import datetime
from typing import Any, NoReturn

import numpy as np
import pandas as pd

from gnsstools.gnsstime import to_gnsstime
from gnsstools.satellites import GALILEO, GLONASS, GPS, Satellite
from gnsstools.utils import camel2snake


class NavigationDataFrame(pd.DataFrame):
    @property
    def _constructor(self) -> type["NavigationDataFrame"]:
        return NavigationDataFrame

    def select(
        self,
        system: str | None = None,
        prn: int | None = None,
        date: datetime | None = None,
        ignore_offset: bool = False,
    ) -> Satellite | None:
        # Make sure the arguments are available.
        systems = np.unique(self.index.get_level_values("System"))
        prns = np.unique(self.index.get_level_values("PRN"))
        assert system in systems, (
            f"The provided system {system} was not found in the dataset. Available systems are {', '.join(systems)}."
        )
        assert prn in prns, (
            f"The provided PRN {prn} was not found in the dataset. Available PRNs are {', '.join(prns.astype('str'))}."
        )
        # Neither contains None, so both arguments are set from here.
        assert system is not None and prn is not None
        if date is None:
            raise ValueError("A date is required to select an ephemeris.")

        # Find the closest time to the provided `date`.
        sub_df = self.loc[(system, prn), :]
        deltas = []
        for date_ in sub_df.index.get_level_values("Date"):
            date_ = to_gnsstime(date_)
            deltas.append(np.abs((date - date_).total_seconds()))
        offset = np.min(deltas)
        date = sub_df.index[int(np.argmin(deltas))]
        # The time coverage should be lower than 2 hours.
        if not ignore_offset:
            assert offset / 3600 < 2, (
                f"The provided date does not overlap with dates from {system}{prn} satellite. "
                f"There must be a time delta of 2h at least. "
                f"Got a time delta of {offset / 3600:.2f} hours. "
                f"The closest date is {date}. You can ignore this behavior with `ignore_offset=True`."
            )
        # Get the row and drop NaNs
        data = self.loc[(system, prn, date), :].squeeze()
        arguments: dict[str, Any] = {"prn": int(prn), "toc": to_gnsstime(date)}
        # When several records share the epoch (e.g. the F/NAV and I/NAV messages of Galileo), `data` is a DataFrame
        # whose rows all have NaNs, and the satellite gets no ephemeris (known bug, see tests/test_satellites.py).
        if isinstance(data, pd.Series):
            for arg, value in data.dropna().items():
                arguments[camel2snake(str(arg))] = value

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
    def _constructor(self) -> type["ObservationDataFrame"]:
        return ObservationDataFrame

    def select(self) -> NoReturn:
        raise NotImplementedError


class PositionDataFrame(pd.DataFrame):
    @property
    def _constructor(self) -> type["PositionDataFrame"]:
        return PositionDataFrame

    def select(self) -> NoReturn:
        raise NotImplementedError
