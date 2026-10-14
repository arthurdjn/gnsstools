# Encoding: UTF-8
# File: nav3.py
# Creation: Tuesday January 26th 2021
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


r"""
This module reads the navigation messages of `RINEX` files, versions 2 and 3.
"""

import re
from collections import defaultdict

from gnsstools import gnsstime

from .datasets import NavigationDataFrame
from .header import RinexHeaderReader
from .reader import ABCReader, Record, Value

__all__ = ["RinexNavReader"]


# The fields of a navigation record, line by line: the clock fields of the first line (after the satellite and the
# date), then the broadcast orbit lines, of 4 fields each.
GPS_FIELDS = (
    ("SVClockBias", "SVClockDrift", "SVClockDriftRate"),
    ("IODE", "Crs", "DeltaN", "M0"),
    ("Cuc", "e", "Cus", "sqrtA"),
    ("TOE", "Cic", "Omega0", "Cis"),
    ("i0", "Crc", "Omega", "OmegaDot"),
    ("IDOT", "L2Codes", "GPSWeek", "L2Pflag"),
    ("SVAcc", "SVHealth", "TGD", "IODC"),
    ("TransTime", "FitInter"),
)
GLONASS_FIELDS = (
    ("SVClockBias", "SVRelFreqBias", "MessageFrameTime"),
    ("X", "dX", "dX2", "Health"),
    ("Y", "dY", "dY2", "FreqNum"),
    ("Z", "dZ", "dZ2", "AgeOpInfo"),
)
GALILEO_FIELDS = (
    ("SVClockBias", "SVClockDrift", "SVClockDriftRate"),
    ("IODnav", "Crs", "DeltaN", "M0"),
    ("Cuc", "e", "Cus", "sqrtA"),
    ("TOE", "Cic", "Omega0", "Cis"),
    ("i0", "Crc", "Omega", "OmegaDot"),
    # The data sources tell the message (I/NAV, F/NAV) and the signals of the clock parameters.
    ("IDOT", "DataSources", "GALWeek"),
    ("SISA", "SVHealth", "BGDe5a", "BGDe5b"),
    ("TransTime",),
)
FIELDS = {"G": GPS_FIELDS, "R": GLONASS_FIELDS, "E": GALILEO_FIELDS}

FIELD_WIDTH = 19


class RinexNavReader(ABCReader):
    """
    Reads the navigation records of a `RINEX` file, version 2 or 3.

    * :attr:`lines` (list): List of lines to process.
    * :attr:`system` (str, optional): The system of the records of a RINEX 2 file, which holds one system only.
      Defaults to the system of the header.

    """

    def __init__(self, lines: list[str], system: str | None = None) -> None:
        super().__init__(lines)
        header = RinexHeaderReader(lines).read()
        version = header.get("Version")
        # RINEX 2 records start with a 2-character PRN and a 2-digit year, and are indented by 3 characters instead of
        # 4: every field sits one character to the left of its RINEX 3 position.
        self.version2 = isinstance(version, (int, float)) and version < 3
        header_system = header.get("System")
        self.system = system or (header_system if isinstance(header_system, str) else None)

    def _fields(self, line: str, start: int, names: tuple[str, ...]) -> Record:
        values: list[Value] = [
            self._eval(line[start + FIELD_WIDTH * k : start + FIELD_WIDTH * (k + 1)]) for k in range(len(names))
        ]
        return dict(zip(names, values, strict=True))

    def _extract_fields(self, system: str) -> Record:
        """Read the record at the cursor, and move the cursor past it."""
        fields = FIELDS[system]
        lines = self.lines[self._cursor : self._cursor + len(fields)]
        self._cursor += len(fields)
        shift = 1 if self.version2 else 0
        data = self._fields(lines[0], 23 - shift, fields[0])
        for line, names in zip(lines[1:], fields[1:], strict=False):
            data.update(self._fields(line, 4 - shift, names))
        return data

    def read(self) -> NavigationDataFrame:
        """Read all the lines from a `RINEX` file and return a ``pandas.DataFrame``.
        The indexes are based on the ``satellite`` id.
        The number of row corresponds to the number of records (i.e. navigation elements).

        Returns:
            pandas.DataFrame
        """
        # Construct a DataFrame
        self._cursor = 0
        satellites: defaultdict[str, list[Record]] = defaultdict(list)

        # Skip the header
        self._skip_header()
        self._cursor += 1

        while self._cursor < len(self.lines):
            line = self.lines[self._cursor]

            # If the line is blank
            if line.strip() == "":
                self._cursor += 1
                continue

            # Find the associated satellite system
            # Create the satellite name (e.g. " 3" - > "G03", "G 2" -> "G02")
            if self.version2:
                system_ = self.system or "G"
                prn = self._eval(line[:2])
                line_dates = line[2:22]
            else:
                system_ = line[0]
                prn = self._eval(line[1:3])
                line_dates = line[3:23]
            satellite = f"{system_}{prn}"

            # If the PRN was not found (unknown satellite or corrupted data), or the system is unknown,
            # read the next line
            if prn is None or system_ not in FIELDS:
                self._cursor += 1
                continue

            # Extract the data
            data = self._extract_fields(system_)

            # From here we should have found a valid system (satellite with known PRN).
            # Extract the date (year, month, day etc.), common for all systems.
            # Remove redundant spaces and split on spaces (dates are separated by a space (or more...))
            year, month, day, hour, minute, second = re.sub("  +", " ", line_dates.strip()).split(" ")
            data["Date"] = gnsstime(year, month, day, hour, minute, second)

            # Count PRN and save the data
            data["System"] = system_
            data["PRN"] = prn
            satellites[satellite].append(data)

        # Create the DataFrame
        df_data: list[Record] = []
        for values in satellites.values():
            df_data.extend(values)
        df = NavigationDataFrame(df_data)
        # Make it pretty
        df = df.set_index(["System", "PRN", "Date"])
        columns = sorted([col for col in df.columns])
        df = df.reindex(columns, axis=1)
        df = df.sort_index()
        return df
