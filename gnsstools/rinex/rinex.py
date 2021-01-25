# File: rinex.py
# Creation: Saturday January 23rd 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


"""
This module should be used to read any `RINEX` file.

.. note::
    The loaded dataset is a ``pandas.DataFrame`` object.

.. code-block:: python

    from gnsstools import rinex
    
    df = rinex.load("BRDC00IGS_R_20182850000_01D_MN.rnx")

"""


from collections import defaultdict
from shapely.geometry import Point
import numpy as np
import pandas as pd
import xarray as xr
import georinex


class Rinex(xr.Dataset):

    @classmethod
    def load(cls, filename, *args, **kwargs):
        dataset = georinex.load(filename, *args, **kwargs)
        return cls(dataset)

    def to_dataframe(self):
        df_data = defaultdict(list)
        previous_prn = None
        session_cursor = 1
        fields = self.keys()

        for sv_index, sv in enumerate(self.sv):
            # Time session (e.g. different time for a same satellite 'G01')
            # Look up for time indexes. If some are founds, save them.
            time_indexes = []
            for field in fields:
                variable = getattr(self, field)
                if variable.dims != ('time', 'sv'):
                    continue

                time_indexes = np.argwhere(~np.isnan(np.array(variable[:, sv_index]))).flatten()
                if len(time_indexes) > 0:
                    break

            for field in fields:
                # Get the variable by name from the xarray Dataset
                variable = getattr(self, field)
                # Get the values (get NaN if there are no values for this variable)
                values = list(np.array(variable[time_indexes, sv_index]))
                # Convert to shapely Point for 3D values
                if len(variable.dims) == 3:
                    points = []
                    for value in values:
                        try:
                            points.append(Point(value))
                        except:
                            points.append(None)
                    values = points
                df_data[field].extend(values)

            time = list(np.array(self.time[time_indexes]))
            df_data["time"].extend(time)
            prn = sv.item().split("_")[0]
            df_data["satellite"].extend([prn] * len(time_indexes))
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
        return df
