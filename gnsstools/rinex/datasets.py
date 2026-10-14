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
from gnsstools.satellites import GPS, Galileo, Glonass, Satellite

# The attribute of the satellite classes (`gnsstools.satellites`) for each field of the navigation records.
ATTRIBUTES = {
    # GPS, Galileo and GLONASS
    "SVClockBias": "sv_clock_bias",
    "SVClockDrift": "sv_clock_drift",
    "SVClockDriftRate": "sv_clock_drift_rate",
    "IODE": "iode",
    "Crs": "crs",
    "DeltaN": "delta_n",
    "M0": "m0",
    "Cuc": "cuc",
    "e": "e",
    "Cus": "cus",
    "sqrtA": "sqrt_a",
    "TOE": "toe",
    "Cic": "cic",
    "Omega0": "omega0",
    "Cis": "cis",
    "i0": "i0",
    "Crc": "crc",
    "Omega": "omega",
    "OmegaDot": "omega_dot",
    "IDOT": "idot",
    "L2Codes": "l2_codes",
    "GPSWeek": "gps_week",
    "L2Pflag": "l2_pflag",
    "SVAcc": "sv_acc",
    "SVHealth": "sv_health",
    "TGD": "tgd",
    "IODC": "iodc",
    "TransTime": "trans_time",
    "FitInter": "fit_inter",
    "IODnav": "iod_nav",
    "DataSources": "data_sources",
    "GALWeek": "gal_week",
    "SISA": "sisa",
    "BGDe5a": "bgd_e5a",
    "BGDe5b": "bgd_e5b",
    # GLONASS
    "SVRelFreqBias": "sv_rel_freq_bias",
    "MessageFrameTime": "message_frame_time",
    "X": "x",
    "dX": "dx",
    "dX2": "dx2",
    "Health": "health",
    "Y": "y",
    "dY": "dy",
    "dY2": "dy2",
    "FreqNum": "freq_num",
    "Z": "z",
    "dZ": "dz",
    "dZ2": "dz2",
    "AgeOpInfo": "age_op_info",
}

# Ephemerides further than this from the requested date are rejected by `NavigationDataFrame.select`.
MAX_OFFSET = 2 * 3600.0


class NavigationDataFrame(pd.DataFrame):
    @property
    def _constructor(self) -> type["NavigationDataFrame"]:
        return NavigationDataFrame

    def select(self, system: str, prn: int, date: datetime, ignore_offset: bool = False) -> Satellite | None:
        """Select the ephemeris of a satellite that is the closest to a date.

        Args:
            system (str): The system of the satellite, e.g. ``"G"`` for GPS.
            prn (int): The PRN of the satellite.
            date (datetime): The date of the ephemeris to look for.
            ignore_offset (bool, optional): Return the closest ephemeris even when it is 2 hours or more away from
                ``date``. Defaults to ``False``.

        Returns:
            Satellite: A ``GPS``, ``Glonass`` or ``Galileo`` instance, or ``None`` for the other systems. When several
            records share the closest epoch (e.g. the F/NAV and I/NAV messages of Galileo), the first one is used.

        Raises:
            ValueError: If the satellite is not in the DataFrame, or if its closest ephemeris is 2 hours or more away
                from ``date`` (unless ``ignore_offset`` is set).
        """
        satellites = self.index.droplevel("Date").unique()
        if (system, prn) not in satellites:
            available = ", ".join(f"{system_}{prn_:02d}" for system_, prn_ in satellites)
            raise ValueError(
                f"The satellite {system}{prn:02d} is not in the dataset. Available satellites: {available}."
            )

        # Find the closest time to the provided `date`.
        records = self.loc[(system, prn), :]
        offsets = [abs((date - to_gnsstime(date_)).total_seconds()) for date_ in records.index]
        closest = int(np.argmin(offsets))
        toc = to_gnsstime(records.index[closest])
        if not ignore_offset and offsets[closest] >= MAX_OFFSET:
            raise ValueError(
                f"The closest ephemeris of {system}{prn:02d} is {offsets[closest] / 3600:.2f} hours away from {date} "
                f"({toc}), and must be less than {MAX_OFFSET / 3600:.0f} hours away. "
                "You can ignore this behavior with `ignore_offset=True`."
            )

        # Get the row and drop the fields of the other systems.
        data = records.iloc[closest].dropna()
        arguments: dict[str, Any] = {"prn": int(prn), "toc": toc}
        for field, value in data.items():
            arguments[ATTRIBUTES[str(field)]] = value

        # Create a satellite instance.
        if system == "G":
            return GPS(**arguments)
        elif system == "R":
            return Glonass(**arguments)
        elif system == "E":
            return Galileo(**arguments)
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
