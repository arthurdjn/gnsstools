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

    def read(self, system=None):
        """Read all the lines from a `RINEX3` file and return a ``pandas.DataFrame``.
        The indexes are based on the ``satellite`` id.
        The number of row corresponds to the number of records (i.e. navigation elements).

        Returns:
            pandas.DataFrame
        """
        # Construct a DataFrame
        self._cursor = 0
        satellites = defaultdict(list)

        # Skip the header
        self._skip_header()
        self._cursor += 1

        while self._cursor < len(self.lines):
            line = self.lines[self._cursor]
            print(f"\r{self._cursor}", end="")

            # If the line is blank
            if line.strip() == "":
                self._cursor += 1
                continue

            # Find the associated satellite system
            # Create the satellite name (e.g. " 03" - > "G03", "G 2" -> "G02")
            if line[0] == " " or line[0].isdigit():
                system_ = system or "G"
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

            # From here we should have found a valid system (satellite with known PRN).
            # Extract the date (year, month, day etc.), common for all systems.
            # Remove redundant spaces and split on spaces (dates are separated by a space (or more...))
            line_dates = re.sub("  +", " ", line[3:23].strip())
            year, month, day, hour, minute, second = line_dates.split(" ")
            data["Date"] = gnsstime(year, month, day, hour, minute, second)

            # Count PRN and save the data
            data["Session"] = len(satellites[satellite]) + 1
            data["System"] = system_
            data["PRN"] = prn
            satellites[satellite].append(data)

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
