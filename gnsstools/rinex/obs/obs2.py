# Encoding: UTF-8
# File: obs2.py
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

# GNSS Tools
from gnsstools.logger import logger
from gnsstools import gnsstime


class Rinex2ObsReader:

    def __init__(self, lines):
        self.lines = lines
        self._cursor = cursor

    @staticmethod
    def _eval(string):
        """Conversion from `RINEX` string representation of floats to python float.
        
        Args:
            string (str): String to convert to float, int or str.
        
        Returns:
            any: Evaluated string.
        
        Examples:
            >>> _eval("string")
                "string"
            >>> _eval("   00013  ")
                13
            >>> _eval("  00010.d+12  ")
                1.000000e+13
        """
        # Remove black spaces
        string = string.strip()
        # Check if the string is None
        if string == "":
            return None
        # Check if the string is an integer
        elif string.isdigit():
            return int(string)
        # Try to convert to float
        try:
            string = re.sub("[Dd]", "e", string)
            return float(string)
        except:
            pass
        # Else, return the stripped string
        return str(string)
        
    def _read_header(self):
        self.reader = 0
        fields = []
        line = self.lines[self._cursor]

        # Look for the obsearvations. Break if the header is passed.
        while line[60:].strip() != "END OF HEADER":
            if line[60:].strip() == "# / TYPES OF OBSERV":
                # Get the number of available fields.
                fields_num = int(line[0:6])

                # There are 9 fields / observations per row in the header. Get the number of associated lines.
                field_row = math.ceil(fields_num / 9)

                # Extract all fields / observations if multiple lines are used.
                for _ in range(field_row):
                    # Look for the 9 potential fields / observations.
                    for ifield in range(9):
                        field = line[(ifield + 1) * 6:(ifield + 2) * 6]
                        if not field.isspace():
                            fields.append(field.strip())
                    # Read the nex line.
                    self._cursor += 1
                    line = self.lines[self._cursor]
            # If nothing was found, look for the next line.
            self._cursor += 1
            line = self.lines[self._cursor]

        return fields

    def _read_sat(self):
        satellites = []
        line = self.lines[self._cursor]
        year, month, day = line[0:3], line[3:6], line[6:9]
        hour, minute, second = line[9:12], line[12:15], line[15:26]
        sat_num = int(line[29:32])

        # If the date is not valid, exit the function.
        try:
            time = gnsstime(year, month, day, hour, minute, second)
        except:
            return None, []

        sat_row = math.ceil(sat_num / 12)
        while len(satellites) < sat_num:
            line = self.lines[self._cursor]
            satellites_sequence = line[32:68]

            # There are maximum 12 satellites in per row (e.g. "G02G06G12G14G19G24G25G29G31G32S23S36")
            for isat in range(12):
                # Extract and save the id of the satellite
                satellite = satellites_sequence[isat * 3:(isat + 1) * 3].strip()
                if satellite != "":
                    # Replace blank space by 0 (e.g. "G 2" -> "G02")
                    satellite = re.sub(f"[A-Z][\s][0-9]", lambda x: x.group(0).replace(" ", "0"), satellite)
                    satellites.append(satellite)
            self._cursor += 1

        # Return the corresponding satellites at a specific time.
        return time, satellites

    def _read_obs(self, fields):
        # There ara maximum 5 fields per row.
        field_row = math.ceil(len(fields) / 5)
        data = {field: np.nan for field in fields}

        # Read the row corresponding to the observations of one navigation element.
        line = self.lines[self._cursor]
        for irow in range(field_row):
            # Maximum of five fields per row
            for ifield in range(5):
                # If the field exist (in case the  number of field / observation on the row < 5)
                if irow * 5 + ifield < len(fields):
                    # Extract the value for a specific field / observation.
                    field = fields[irow * 5 + ifield]
                    value = line[ifield * 16: (ifield + 1) * 16]
                    # Replace blank space in the number by 0 (e.g. " 12223.444 42" -> " 12223.444042")
                    value = re.sub(f"[0-9\-][\s][0-9\-]", lambda x: x.group(0).replace(" ", "0"), value)
                    data[field] = self._eval(value)

            # Read next line or exit.
            self._cursor += 1
            if self._cursor >= len(self.lines):
                return data
            line = self.lines[self._cursor]

        return data

    def read(self):
        self._cursor = 0
        fields = self._read_header()
        self._cursor += 1

        sat_counters = defaultdict(int)
        df_data = defaultdict(list)

        while self._cursor < len(self.lines):
            # If the line is blank, continue.
            if self.lines[self._cursor].strip() == "":
                self._cursor += 1
                continue
            time, satellites = self._read_sat()
            for satellite in satellites:
                data = self._read_obs(fields)
                data["time"] = time
                data["satellite"] = satellite
                sat_counters[satellite] += 1
                data["session"] = sat_counters[satellite]
                for key, value in data.items():
                    df_data[key].append(value)
                    
        # Create the DataFrame
        df = pd.DataFrame(df_data)
        df = df.set_index(["satellite", "session"])
        # Order the columns as: "time", other
        columns = ["time"] + sorted([col for col in df.columns if col != "time"])
        df = df.reindex(columns, axis=1)
        return df
