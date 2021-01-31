# Encoding: UTF-8
# File: obs3.py
# Creation: Tuesday January 26th 2021
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


# Basic imports
from collections import defaultdict
import re
import math
import pandas as pd

# GNSS Tools
from .reader import ABCReader
from .datasets import ObservationDataFrame
from gnsstools import gnsstime


class Rinex3ObsReader(ABCReader):

    def __init__(self, lines):
        super().__init__(lines)

    def _read_header(self):
        self._cursor = 0
        fields_dict = defaultdict(list)
        line = self.lines[0]

        # Look for the obsearvations. Break if the header is passed.
        while line[60:].strip() != "END OF HEADER":
            if line[60:].strip() == "SYS / # / OBS TYPES":
                # Get the number of available fields.
                fields_num = int(line[1:6])
                system = line[0]

                # There are 13 fields / observations per row in the header. Get the number of associated lines.
                field_row = math.ceil(fields_num / 13)

                # Extract all fields / observations if multiple lines are used.
                for _ in range(field_row):
                    # Look for the 13 potential fields / observations.
                    fields_string = re.sub("  +", " ", line[7:60].strip())
                    fields_row = fields_string.split(" ")
                    fields_dict[system].extend(fields_row)
                    # Read the nex line.
                    self._cursor += 1
                    line = self.lines[self._cursor]
            else:
                # If nothing was found, look for the next line.
                self._cursor += 1
                line = self.lines[self._cursor]
        return fields_dict

    def _read_obs(self, fields):
        data = {}
        line = self.lines[self._cursor]
        for i, field in enumerate(fields):
            value = line[4+i + 15*i: 4+i + 15*(i + 1)]
            value = re.sub(f"[0-9][\s][0-9]", lambda x: x.group(0).replace(" ", "0"), value)
            data[field] = self._eval(value)
        return data

    def read(self):
        self._cursor = 0
        fields_dict = self._read_header()
        self._cursor += 1

        satellites = defaultdict(list)

        while self._cursor < len(self.lines):
            line = self.lines[self._cursor]
            if line.strip() == "":
                self._cursor += 1
                continue
            elif line[0] == ">":
                # Read the date
                year, month, day, hour, minute, second = line[2:6], line[7:9], line[10:12], line[13:15], line[16:18], line[19:29]
                date = gnsstime(year, month, day, hour, minute, second)
                # Read the number associated to this date. Loop and extract their data.
                sat_num = self._eval(line[33:35])
                for _ in range(sat_num):
                    self._cursor += 1
                    line = self.lines[self._cursor]
                    # Extract the data for one satellite.
                    system, prn = self._eval(line[0]), self._eval(line[1:3])
                    satellite = f"{system}{prn}"
                    fields = fields_dict[system]
                    data = self._read_obs(fields)
                    data["Date"] = date
                    data["System"] = system
                    data["PRN"] = prn
                    data["Session"] = len(satellites[satellite]) + 1
                    # Save the data.
                    satellites[satellite].append(data)

            # Then, read next line (even if the line does not contain data)
            self._cursor += 1

        # Create the DataFrame
        df_data = []
        for satellites, values in satellites.items():
            df_data.extend(values)
        df = pd.DataFrame(df_data)
        # Make it pretty
        df = df.set_index(["System", "PRN", "Date"])
        columns = sorted([col for col in df.columns])
        df = df.reindex(columns, axis=1)
        return ObservationDataFrame(df)
