# Encoding: UTF-8
# File: utils.py
# Creation: Tuesday January 26th 2021
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


from collections import defaultdict
from shapely.geometry import Point
import numpy as np
import pandas as pd


def convert_georinex(xarray, convert=True):

    # If the dataset does not have "sv" and "time" coordinates, or have more than 3 coordinates,
    # the default DataFrame is constructed.
    if not convert or len(xarray.coords) > 3 or not set(["time", "sv"]).issubset(xarray.coords):
        df = xarray.to_dataframe()
        # Add the metadata (attributes) to the DataFrame to not loose any information
        df.attrs = xarray.attrs
        return df

    df_data = defaultdict(list)
    previous_prn = None
    session_cursor = 1
    variable_names = xarray.keys()

    for sv_index, sv in enumerate(xarray.sv):
        # Look up for time indexes. If some are founds, save them.
        # The idea is to search for variable names that are NOT NaN over time.
        # It is assumed that all variable names for a satellite are filled, i.e. a GPS (e.g. "G01") will have
        # all its variable names (e.g. "SVclockBias", "position" etc.) associated to a value that is NOT NaN.
        time_indexes = []
        for variable_name in variable_names:
            variable = getattr(xarray, variable_name)
            time_indexes = np.argwhere(~np.isnan(np.array(variable[:, sv_index]))).flatten()
            if len(time_indexes) > 0:
                break

        # Retrieve the variable_names per PRN (satellite) and session id.
        for variable_name in variable_names:
            variable = getattr(xarray, variable_name)
            values = list(np.array(variable[time_indexes, sv_index]))
            # If the values are 3D, convert them to shapely Point.
            if len(variable.dims) == 3:
                points = []
                for value in values:
                    try:
                        points.append(Point(value))
                    except:
                        points.append(None)
                values = points
            df_data[variable_name].extend(values)

        # Create a new variable_name for "time"
        time = list(np.array(xarray.time[time_indexes]))
        df_data["time"].extend(time)
        # Create a new variable_name for "satellite"
        prn = sv.item().split("_")[0]
        df_data["satellite"].extend([prn] * len(time_indexes))
        # Create a new variable_name for the "session"
        sessions_indexes = range(session_cursor, len(time_indexes) + session_cursor)
        df_data["session"].extend(list(sessions_indexes))

        # Update for next time
        if prn == previous_prn:
            session_cursor += len(time_indexes)
        else:
            session_cursor = 1
        previous_prn = prn

    # Create the DataFrame, with multiple indexes (PRN, Session)
    df = pd.DataFrame(df_data)
    df = df.set_index(["satellite", "session"])
    # Order the columns as: "time", other
    columns = ["time"] + sorted([col for col in df.columns if col != "time"])
    df = df.reindex(columns, axis=1)
    # Attach the metadata (attributes) to the DataFrame to not loose any information
    df.attrs = xarray.attrs
    return df
