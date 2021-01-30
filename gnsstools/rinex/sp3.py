# Encoding: UTF-8
# File: sp3.py
# Creation: Tuesday January 26th 2021
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


# Basic imports
from collections import defaultdict
import re
import math
import numpy as np
import pandas as pd
from shapely.geometry import Point

# GNSS Tools
from gnsstools.rinex.rinex import RinexReader
from gnsstools.logger import logger
from gnsstools import gnsstime


class SP3Reader(RinexReader):

    def __init__(self, lines):
        super().__init__(lines)

    def _read_header(self):
        line = self.lines[self._cursor]
        return {
            "NumEpoch": self._eval(line[32:39]),
            "CoordSystem": self._eval(line[46:51]),
            "OrbitType": self._eval(line[52:55]),
            "Agency": self._eval(line[56:60])
        }

    def _read_sat(self):
        satellites = []
        line = self.lines[self._cursor]
        sat_num = int(line[3:7])
        # There are maximum 17 satellites per row
        while len(satellites) < sat_num:
            line = self.lines[self._cursor]
            satellites_sequence = line[9:60]

            # There are maximum 17 satellites per row
            # e.g. satellites_sequence = "G01G02G03G04G05G06G07G08G09G10G11G12G13G14G15G16G17"
            for isat in range(17):
                # Extract and save the id of the satellite
                satellite = satellites_sequence[isat * 3:(isat + 1) * 3].strip()
                if satellite != "":
                    # Replace blank space by 0 (e.g. "G 2" -> "G02")
                    satellite = re.sub(f"[A-Z][\s][0-9]", lambda x: x.group(0).replace(" ", "0"), satellite)
                    satellites.append(satellite)
            self._cursor += 1

        # Return the corresponding satellites.
        return satellites

    def _read_position(self):
        line = self.lines[self._cursor]
        return {
            "Position": Point(self._eval(line[4:18]), self._eval(line[18:32]), self._eval(line[32:46])),
            "Clock": self._eval(line[46:60])
        }

    def _read_velocity(self):
        line = self.lines[self._cursor]
        return {
            "Velocity": Point(self._eval(line[4:18]), self._eval(line[18:32]), self._eval(line[32:46])),
            "Clock": self._eval(line[46:60])
        }

    def read(self):
        self._cursor = 0
        line = self.lines[self._cursor]

        # Read the header
        while not line.startswith("#"):
            self._cursor += 1
            line = self.lines[self._cursor]
        header = self._read_header()

        # Read the list of SV (satellites) available.
        while not line.startswith("+"):
            self._cursor += 1
            line = self.lines[self._cursor]
        satellites_list = self._read_sat()

        # Read the data
        satellites = defaultdict(list)
        date = None

        while self._cursor < len(self.lines):
            line = self.lines[self._cursor]
            # If the end is reached, break.
            if line.strip() == "EOF":
                break
            # Read the date for a set of observations.
            # NOTE: There should be `len(satellites_list)` observations.
            # However, the following will still work if it's not the case.
            if line.startswith("*"):
                line = self.lines[self._cursor]
                year, month, day, hour, minute, second = line[3:7], line[8:10], line[11:13], line[14:16], line[17:19], line[20:31]
                date = gnsstime(year, month, day, hour, minute, second)

            # Search for data to add
            elif re.search("[PV]", line[0]):
                line = self.lines[self._cursor]
                system, prn = self._eval(line[1]), self._eval(line[2:4])
                # Extract the data
                if line.startswith("P"):
                    data = data = self._read_position()
                elif line.startswith("V"):
                    data = self._read_velocity()
                else:
                    data = {}
                # Add relevant information
                data["Date"] = date
                data["System"] = system
                data["PRN"] = prn
                satellite = f"{system}{prn}"
                data["Session"] = len(satellites[satellite]) + 1
                satellites[satellite].append(data)
            # Read the next line
            self._cursor += 1

        # Create the DataFrame
        df_data = []
        for satellites, values in satellites.items():
            df_data.extend(values)
        df = pd.DataFrame(df_data)
        # Make it pretty
        df = df.set_index(["System", "PRN", "Session"])
        columns = ["Date"] + sorted([col for col in df.columns if col != "Date"])
        df = df.reindex(columns, axis=1)
        return df
