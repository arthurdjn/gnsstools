# Encoding: UTF-8
# File: nav3.py
# Creation: Tuesday January 26th 2021
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


r"""
This module handles reading `RINEX3` files. 
It was only tested with `RINEX` version 3.03, but should works for any 3. versions.
"""


# Basic imports
import re
from collections import defaultdict
import pandas as pd

# gnsstime
from .rinex import RinexReader
from gnsstools import gnsstime


__all__ = [
    "RinexNavReader"
]


# satellite  '0:3'      'G01'
# year       '4:8'      '2018'
# month      '9:11'     '10'
# day        '12:14'    '12'
# hour       '15:17'    '18'
# minute     '18:20'    '00'
# second     '21:23'    '00'
# -1/        '23:42'    '-2.745445817709E-05'
# -2/        '42:62'    '-1.080024958355E-11'
# -3/        '61:80'    ' 0.000000000000E+00'
#1/          '4:23'     ' 3.500000000000E+01'
#2/          '23:42'    ' 1.175000000000E+01'
#3/          '42:61'    ' 4.424827168955E-09'
#4/          '61:80'    ' 2.781290457443E+00'


# Fields for GPS satellites
G_FIELDS_MAP = [
    [("satellite", "0:3"), ("year", "4:8"), ("month", "9:11"), ("day", "12:14"),
     ("hour", "15:17"), ("minute", "18:20"), ("second", "21:23"),
     ("SVClockBias", "23:42"), ("SVClockDrift", "42:61"), ("SVClockDriftRate", "61:80")],
    [("IODE", "4:23"), ("Crs", "23:42"), ("DeltaN", "42:61"), ("M0", "61:80")],
    [("Cuc", "4:23"), ("e", "23:42"), ("Cus", "42:61"), ("sqrtA", "61:80")],
    [("TOE", "4:23"), ("Cic", "23:42"), ("Omega0", "42:61"), ("Cis", "61:80")],
    [("i0", "4:23"), ("Crc", "23:42"), ("Omega", "42:61"), ("OmegaDot", "61:80")],
    [("IDOT", "4:23"), ("L2Codes", "23:42"), ("GPSWeek", "42:61"), ("L2Pflag", "61:80")],
    [("SVAcc", "4:23"), ("SVHealth", "23:42"), ("TGD", "42:61"), ("IODC", "61:80")],
    [("TransTime", "4:23"), ("FitInter", "23:42")]
]
G_FIELDS = set([field[0] for fields in G_FIELDS_MAP for field in fields])

# Fields for GALILEO satellites
E_FIELDS_MAP = [
    [("satellite", "0:3"), ("year", "4:8"), ("month", "9:11"), ("day", "12:14"),
     ("hour", "15:17"), ("minute", "18:20"), ("second", "21:23"),
     ("SVClockBias", "23:42"), ("SVClockDrift", "42:61"), ("SVClockDriftRate", "61:80")],
    [("IODnav", "4:23"), ("Crs", "23:42"), ("DeltaN", "42:61"), ("M0", "61:80")],
    [("Cuc", "4:23"), ("e", "23:42"), ("Cus", "42:61"), ("sqrtA", "61:80")],
    [("TOE", "4:23"), ("Cic", "23:42"), ("Omega0", "42:61"), ("Cis", "61:80")],
    [("i0", "4:23"), ("Crc", "23:42"), ("Omega", "42:61"), ("OmegaDot", "61:80")],
    [("IDOT", "4:23"), ("GPSWeek", "23:42"), ("GALWeek", "42:61")],
    [("SISA", "4:23"), ("SVhealth", "23:42"), ("BGDe5a", "42:61"), ("BGDe5b", "61:80")],
    [("TransTime", "4:23")]
]
E_FIELDS = set([field[0] for fields in E_FIELDS_MAP for field in fields])


# Fields for GLONASS satellites
R_FIELDS_MAP = [
    [("satellite", "0:3"), ("year", "4:8"), ("month", "9:11"), ("day", "12:14"),
     ("hour", "15:17"), ("minute", "18:20"), ("second", "21:23"),
     ("SVClockBias", "23:42"), ("SVRelFreqBias", "42:61"), ("MessageFrameTime", "61:80")],
    [("X", "4:23"), ("dX", "23:42"), ("dX2", "42:61"), ("Health", "61:80")],
    [("Y", "4:23"), ("dY", "23:42"), ("dY2", "42:61"), ("FreqNum", "61:80")],
    [("Z", "4:23"), ("dZ", "23:42"), ("dZ2", "42:61"), ("AgeOpInfo", "61:80")]
]
R_FIELDS = set([field[0] for fields in R_FIELDS_MAP for field in fields])


# Fields for all satellites
FIELDS = E_FIELDS.union(G_FIELDS, R_FIELDS)


class RinexNavReader(RinexReader):
    """
    Handles reading `RINEX3` files.

    * :attr:`lines` (list): List of lines to process.

    """

    def __init__(self, lines):
        super().__init__(lines)

    def _extract_g_fields(self):
        lines = self.lines[self._cursor:self._cursor+8]
        self._cursor += 8
        return {
            # First row
            "SVClockBias": self._eval(lines[0][23:42]),
            "SVClockDrift": self._eval(lines[0][42:61]),
            "SVClockDriftRate": self._eval(lines[0][61:80]),
            # Second row
            "IODE": self._eval(lines[1][4:23]),
            "Crs": self._eval(lines[1][23:42]),
            "DeltaN": self._eval(lines[1][42:61]),
            "M0": self._eval(lines[1][61:80]),
            # Third row
            "Cuc": self._eval(lines[2][4:23]),
            "e": self._eval(lines[2][23:42]),
            "Cus": self._eval(lines[2][42:61]),
            "sqrtA": self._eval(lines[2][61:80]),
            # Fourth row
            "TOE": self._eval(lines[3][4:23]),
            "Cic": self._eval(lines[3][23:42]),
            "Omega0": self._eval(lines[3][42:61]),
            "Cis": self._eval(lines[3][61:80]),
            # Fifth row
            "i0": self._eval(lines[4][4:23]),
            "Crc": self._eval(lines[4][23:42]),
            "Omega": self._eval(lines[4][42:61]),
            "OmegaDot": self._eval(lines[4][61:80]),
            # Sixth row
            "IDOT": self._eval(lines[5][4:23]),
            "L2Codes": self._eval(lines[5][23:42]),
            "GPSWeek": self._eval(lines[5][42:61]),
            "L2Pflag": self._eval(lines[5][61:80]),
            # Seventh row
            "SVAcc": self._eval(lines[6][4:23]),
            "SVHealth": self._eval(lines[6][23:42]),
            "TGD": self._eval(lines[6][42:61]),
            "IODC": self._eval(lines[6][61:80]),
            # Eight row
            "TransTime": self._eval(lines[7][4:23]),
            "FitInter": self._eval(lines[7][23:42]),
        }

    def _extract_r_fields(self):
        lines = self.lines[self._cursor:self._cursor+4]
        self._cursor += 4
        return {
            # First row
            "SVClockBias": self._eval(lines[0][23:42]),
            "SVRelFreqBias": self._eval(lines[0][42:61]),
            "MessageFrameTime": self._eval(lines[0][61:80]),
            # Second row
            "X": self._eval(lines[1][4:23]),
            "dX": self._eval(lines[1][23:42]),
            "dX2": self._eval(lines[1][42:61]),
            "Health": self._eval(lines[1][61:80]),
            # Third row
            "Y": self._eval(lines[2][4:23]),
            "dY": self._eval(lines[2][23:42]),
            "dY2": self._eval(lines[2][42:61]),
            "FreqNum": self._eval(lines[2][61:80]),
            # Fourth row
            "Z": self._eval(lines[3][4:23]),
            "dZ": self._eval(lines[3][23:42]),
            "dZ2": self._eval(lines[3][42:61]),
            "AgeOpInfo": self._eval(lines[3][61:80]),
        }

    def _extract_e_fields(self):
        lines = self.lines[self._cursor:self._cursor+8]
        self._cursor += 8
        return {
            # First row
            "SVClockBias": self._eval(lines[0][23:42]),
            "SVClockDrift": self._eval(lines[0][42:61]),
            "SVClockDriftRate": self._eval(lines[0][61:80]),
            # Second row
            "IODnav": self._eval(lines[1][4:23]),
            "Crs": self._eval(lines[1][23:42]),
            "DeltaN": self._eval(lines[1][42:61]),
            "M0": self._eval(lines[1][61:80]),
            # Third row
            "Cuc": self._eval(lines[2][4:23]),
            "e": self._eval(lines[2][23:42]),
            "Cus": self._eval(lines[2][42:61]),
            "sqrtA": self._eval(lines[2][61:80]),
            # Fourth row
            "TOE": self._eval(lines[3][4:23]),
            "Cic": self._eval(lines[3][23:42]),
            "Omega0": self._eval(lines[3][42:61]),
            "Cis": self._eval(lines[3][61:80]),
            # Fifth row
            "i0": self._eval(lines[4][4:23]),
            "Crc": self._eval(lines[4][23:42]),
            "Omega": self._eval(lines[4][42:61]),
            "OmegaDot": self._eval(lines[4][61:80]),
            # Sixth row
            "IDOT": self._eval(lines[5][4:23]),
            "GPSWeek": self._eval(lines[5][23:42]),
            "GALWeek": self._eval(lines[5][42:61]),
            # Seventh row
            "SISA": self._eval(lines[6][4:23]),
            "SVHealth": self._eval(lines[6][23:42]),
            "BGDe5a": self._eval(lines[6][42:61]),
            "BGDe5b": self._eval(lines[6][61:80]),
            # Eight row
            "TransTime": self._eval(lines[7][4:23]),
        }

    def extract_fields(self, lines, fields_map):
        """Extract navigation data based on a fields map.

        Args:
            lines (list): List of lines containing the data to extract. 
                The number of lines should be the same as the number of row in ``fields_map``.
            fields_map (list): List of fields. Each row maps data from a line to its associated field.
                A field a tuple, composed of a name and the column index/range (i.e. location in the line).

        Returns:
            dict: The extracted data.
        """
        data = {}
        for fields, line in zip(fields_map, lines):
            for (field, field_range) in fields:
                start, end = field_range.split(":")
                start, end = int(start), int(end)
                value = line[start:end]
                data[field] = self._eval(value)
        return data

    def read(self, system=None):
        """Read all the lines from a `RINEX3` file and return a ``pandas.DataFrame``.
        The indexes are based on the ``satellite`` id.
        The number of row corresponds to the number of records (i.e. navigation elements).

        Returns:
            pandas.DataFrame
        """
        # Construct a DataFrame
        self._cursor = 0
        df_data = defaultdict(list)
        df_fields = FIELDS.difference({"year", "month", "day", "hour", "minute", "second"}).union({"session", "time"})

        previous_satellite = None
        session_counter = 1

        # Skip the header
        self._skip_header()
        self._cursor += 1

        while self._cursor < len(self.lines):
            #print(f"\r{self._cursor}/{len(self.lines)}\t\t\t\t\t", end="")
            line = self.lines[self._cursor]
            print(f"\r{self._cursor}", end="")

            # If the line is blank
            if line.strip() == "":
                self._cursor += 1
                continue

            # Find the associated satellite system
            # Create the satellite name (e.g. " 03" - > "G03", "G 2" -> "G02")
            if line[0] == " " or line[0].isdigit():
                system_ = system or "R"
                prn = self._eval(line[:3])
                satellite = f"{system_}{prn}"
            else:
                system_ = line[0]
                prn = self._eval(line[1:3])
                satellite = f"{system_}{prn}"

            # If the PRN was not found (unknown satellite or corrupted data)
            if prn is None:
                self._cursor += 1
                continue
            
            # Extract the data
            if system_ == "E":
                data = self._extract_e_fields()
            elif system_ == "G":
                data = self._extract_g_fields()
            elif system_ == "R":
                data = self._extract_r_fields()

            # If the system is unknown, read the next line
            else:
                self._cursor += 1
                continue

            # Extract the date (year, month, day etc.), common for all systems.
            # print(f"\r{line[3:23].strip().split(' ')}                                                  ", end="")
            # Remove redundant spaces and split on spaces (dates are separated by a space (or more...))
            line_dates = re.sub("  +", " ", line[3:23].strip())
            year, month, day, hour, minute, second = line_dates.split(" ")
            data["time"] = gnsstime(year, month, day, hour, minute, second)

            # Make PRN as unique id
            if satellite == previous_satellite:
                session_counter += 1
            else:
                session_counter = 1
            previous_satellite = satellite
            data["session"] = session_counter
            data["system"] = system_
            data["prn"] = prn

            # And add the data to the ordered list of satellites
            # Update the DataFrame data
            for key, value in data.items():
                df_data[key].append(value)

            # Update for missing fields
            missing_fields = df_fields.difference(set(data.keys()))
            for key in missing_fields:
                df_data[key].append(None)

        # Create the DataFrame
        df = pd.DataFrame(df_data)
        df = df.set_index(["system", "prn", "session"])
        # Order the columns as: "time", other
        columns = ["time"] + sorted([col for col in df.columns if col != "time"])
        df = df.reindex(columns, axis=1)
        return df
