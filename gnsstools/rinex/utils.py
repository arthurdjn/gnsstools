# Encoding: UTF-8
# File: utils.py
# Creation: Tuesday January 26th 2021
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


from collections import defaultdict
from collections.abc import Hashable
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from shapely.geometry import Point

if TYPE_CHECKING:
    # Only installed with the georinex extra.
    import xarray as xr


def convert_georinex(xarray: "xr.Dataset", convert: bool = True) -> pd.DataFrame:

    # If the dataset does not have "sv" and "time" coordinates, or have more than 3 coordinates,
    # the default DataFrame is constructed.
    if not convert or len(xarray.coords) > 3 or not set(["time", "sv"]).issubset(xarray.coords):
        df = xarray.to_dataframe()
        # Add the metadata (attributes) to the DataFrame to not loose any information
        df.attrs = xarray.attrs
        return df

    df_data: defaultdict[Hashable, list[Any]] = defaultdict(list)
    variable_names = xarray.keys()

    for sv_index, sv in enumerate(xarray.sv):
        # Look up for time indexes. If some are founds, save them.
        # The idea is to search for variable names that are NOT NaN over time.
        # It is assumed that all variable names for a satellite are filled, i.e. a GPS (e.g. "G01") will have
        # all its variable names (e.g. "SVclockBias", "position" etc.) associated to a value that is NOT NaN.
        time_indexes: NDArray[np.intp] = np.array([], dtype=np.intp)
        for variable_name in variable_names:
            variable = xarray[variable_name]
            time_indexes = np.argwhere(~np.isnan(np.array(variable[:, sv_index]))).flatten()
            if len(time_indexes) > 0:
                break

        # Retrieve the variable_names per PRN (satellite) and session id.
        for variable_name in variable_names:
            variable = xarray[variable_name]
            values: list[Any] = list(np.array(variable[time_indexes, sv_index]))
            # If the values are 3D, convert them to shapely Point.
            if len(variable.dims) == 3:
                points: list[Point | None] = []
                for value in values:
                    try:
                        points.append(Point(value))
                    except Exception:
                        points.append(None)
                values = points
            df_data[variable_name].extend(values)

        # Create a new variable_name for "date"
        date = list(np.array(xarray.time[time_indexes]))
        df_data["Date"].extend(date)
        # Create a new variable_name for "satellite"
        satellite = sv.item().split("_")[0]
        system, prn = satellite[0], int(satellite[1:3])
        df_data["System"].extend([system] * len(time_indexes))
        df_data["PRN"].extend([prn] * len(time_indexes))

    # Create the DataFrame
    df = pd.DataFrame(df_data)
    # Make it pretty
    df = df.set_index(["System", "PRN", "Date"])
    columns = sorted([col for col in df.columns])
    df = df.reindex(columns, axis=1)
    df = df.sort_index()
    return df
