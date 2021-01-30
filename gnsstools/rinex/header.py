# Encoding: UTF-8
# File: header.py
# Creation: Tuesday January 26th 2021
# Supervisor: Daphné Lercier (dlercier)
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


# Basic imports
from collections import OrderedDict
import math
import re

# GNSS Tools
from gnsstools.rinex.rinex import RinexReader


DATA_TYPES = {
    "N": "NAVIGATION",
    "O": "OBSERVATION"
}


SYSTEMS = {
    "G": "GPS",
    "E": "GALILEO",
    "R": "GLONASS",
    "J": "QZSS",
    "C": "BDS",
    "I": "IRNSS",
    "S": "SBAS",
    "M": "MIXED"
}

CORR_TO_SYSTEM_TIME_FIELDS = [("year", "2:6"), ("month", "10:12"), ("day", "16:18"), ("Unknown", "22:39")]


class RinexHeaderReader(RinexReader):

    def __init__(self, lines):
        super().__init__(lines)

    def _read_version(self, line):
        data = OrderedDict()

        # Extract the data
        version, dtype_string, system_string = line[:20], line[20:40], line[40:60]

        # Add the version
        data["Version"] = self._eval(version)

        # Add the data type
        for dtype, name in DATA_TYPES.items():
            if dtype in dtype_string:
                data["Type"] = dtype
                data["TypeName"] = name

        # Add the system (default set to GPS: "G")
        # NOTE: If the loaded comes from ".*g" data, need to overwrite this section.
        # ? Change this part to look in the file extension, and update this part.
        for system, name in SYSTEMS.items():
            if system == system_string[0]:
                data["System"] = system
                data["SystemName"] = name

        return data

    def _read_pgm(self, line):
        return {
            "PGM": self._eval(line[:20]),
            "RunBy": self._eval(line[20:40]),
            "Date": self._eval(line[40:60])
        }

    def read(self):
        self._cursor = 0
        header = OrderedDict()
        # Category of the metadata (e.g. "RINEX VERSION / TYPE")
        category = None
        while self._cursor < len(self.lines) and category != "END OF HEADER":
            line = self.lines[self._cursor]
            category = line[60:].strip()
            if category == "RINEX VERSION / TYPE":
                data = self._read_version(line)
                header.update(data)
            elif category == "PGM / RUN BY / DATE":
                data = self._read_pgm(line)
                header.update(data)

            self._cursor += 1
        return header
