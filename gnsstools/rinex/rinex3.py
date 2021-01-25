# File: rinex3.py
# Creation: Saturday January 23rd 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


r"""
This module handles reading `RINEX3` files. 
It was only tested with `RINEX` version 3.03, but should works for any 3. versions.

"""


# Basic imports
import re
from collections import defaultdict
import pandas as pd

# gnsstime
from gnsstools import gnsstime


__all__ = [
    "Rinex3Reader"
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
    [("satellite", "0:3"), ("year", "4:8"), ("month", "9:11"), ("day", "12:14"), ("hour", "15:17"), ("minute", "18:20"), ("second", "21:23"), 
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
    [("satellite", "0:3"), ("year", "4:8"), ("month", "9:11"), ("day", "12:14"), ("hour", "15:17"), ("minute", "18:20"), ("second", "21:23"), 
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
    ["satellite", "year", "month", "day", "hour", "minute", "second", "SVClockBias", "SVRelFreqBias", "MessageFrameTime"],
    ["X", "dX", "dX2", "Health"],
    ["Y", "dY", "dY2", "FreqNum"],
    ["Z", "dZ", "dZ2", "AgeOpInfo"],
]
R_FIELDS_MAP = [
    [("satellite", "0:3"), ("year", "4:8"), ("month", "9:11"), ("day", "12:14"), ("hour", "15:17"), ("minute", "18:20"), ("second", "21:23"), 
     ("SVClockBias", "23:42"), ("SVRelFreqBias", "42:61"), ("MessageFrameTime", "61:80")],
    [("X", "4:23"), ("dX", "23:42"), ("dX2", "42:61"), ("Health", "61:80")],
    [("Y", "4:23"), ("dY", "23:42"), ("dY2", "42:61"), ("FreqNum", "61:80")],
    [("Z", "4:23"), ("dZ", "23:42"), ("dZ2", "42:61"), ("AgeOpInfo", "61:80")]
]
R_FIELDS = set([field[0] for fields in R_FIELDS_MAP for field in fields])


# Fields for all satellites
FIELDS = E_FIELDS.union(G_FIELDS, R_FIELDS)


class Rinex3Reader:
    """Handles reading `RINEX3` files.

    * :attr:`lines` (list): List of lines to process.

    """

    def __init__(self, lines):
        self.lines = lines
        self._cursor = 0

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
        try:
            return int(string)
        except:
            pass
        try:
            string = re.sub("[Dd]", "e", string)
            return float(string)
        except:
            pass
        return str(string)

    #! Deprecated
    @staticmethod
    def format_line(line):
        """Make sure the numbers / values are separated by at least one space.

        Args:
            line (str): The line to format.

        Returns:
            str: Formatted line.

        Examples:
            >>> line = "G01 2018 10 12 00 00 00-9.926548227668E-05-4.888534022029E-12 0.000000000000E+00"
            >>> format_line(line)
                "G01 2018 10 12 00 00 00 -9.926548227668E-05 -4.888534022029E-12 0.000000000000E+00"
        """
        line = re.sub(f"[E\D][+\-][^-][^-][0-9\-]", lambda x: f"{x.group(0)[:4]} {x.group(0)[4]}", line)
        line = re.sub(f"[0-9][0-9][-][0-9\.][0-9\.]", lambda x: f"{x.group(0)[:2]} {x.group(0)[2:]}", line)
        return line

    #! Deprecated
    @staticmethod
    def split_line(self, line):
        """Split a line on black spaces.

        Args:
            line (str): The line to split.

        Returns:
            list: Elements of the line separated by a space.

        Examples:
            >>> line = "G01 2018 10 12 00 00 00-9.926548227668E-05-4.888534022029E-12 0.000000000000E+00"
            >>> format_line(line)
                ["G01", "2018", "10", "12", "00", "00", "00", "-9.926548227668E-05", "-4.888534022029E-12", "0.000000000000E+00"]
        """
        line = self.format_line(line.strip())
        parts = re.sub(' +', ' ', line).split(" ")
        return parts

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

    def _read_header(self):
        self._cursor = 0
        header = {}
        for line in self.lines:
            self._cursor += 1
            if not header.get("version") and re.search("RINEX VERSION / TYPE", line):
                # Example:
                #      3.03           N: GNSS NAV DATA    M: MIXED            RINEX VERSION / TYPE
                # parts = ["3.03", "N: GNSS NAV DATA", "M: MIXED", "RINEX VERSION / TYPE"]
                parts = re.sub("  +", "  ", line.strip()).split("  ")
                header["version"] = float(parts[0])
                header["type"] = parts[1][0]

            elif not header.get("leap_seconds") and re.search("LEAP SECONDS", line):
                # Example:
                #     18    18  1929     7                                    LEAP SECONDS
                parts = re.sub(" +", "  ", line.strip()).split("  ")
                header["leap_seconds"] = float(parts[0])

            elif re.search("COMMENT", line):
                # Example:
                # Onboard RINEX convertor RC024                               COMMENT
                comment = line.strip().replace("COMMENT", "").strip()
                header["comment"] += comment

            elif re.search("END OF HEADER", line):
                return header

    def read(self):
        """Read all the lines from a `RINEX3` file and return a ``pandas.DataFrame``.
        The indexes are based on the ``satellite`` id.
        The number of row corresponds to the number of records (i.e. navigation elements).

        Returns:
            pandas.DataFrame
        """

        header = self._read_header()

        # Construct a DataFrame
        df_data = defaultdict(list)
        df_fields = FIELDS.difference({"year", "month", "day", "hour", "minute", "second"}).union({"session", "time"})

        previous_satellite = None
        session_counter = 1

        while self._cursor < len(self.lines):

            if re.search("[EGR][0-9][0-9]", self.lines[self._cursor][:3]):
                # Find the associated satellite system
                system = self.lines[self._cursor][0]
                fields_map = eval(f"{system}_FIELDS_MAP")
                num_fields = len(fields_map)

                # Find the corresponding lines & extract the data
                lines = self.lines[self._cursor:self._cursor+num_fields]
                data = self.extract_fields(lines, fields_map)
                satellite = data["satellite"]
                # Make PRN as unique id
                if satellite == previous_satellite:
                    session_counter += 1
                else:
                    session_counter = 1
                previous_satellite = satellite
                data["session"] = session_counter

                # Make a datetime from the session's time
                year = data.pop("year", 1970)
                month = data.pop("month", 0)
                day = data.pop("day", 0)
                hour = data.pop("hour", 0)
                minute = data.pop("minute", 0)
                second = data.pop("second", 0)
                data["time"] = gnsstime(year, month, day, hour, minute, second)

                # And add the data to the ordered list of satellites
                # Update the DataFrame data
                for key, value in data.items():
                    df_data[key].append(value)

                # Update for missing fields
                missing_fields = df_fields.difference(set(data.keys()))
                for key in missing_fields:
                    df_data[key].append(None)

                # Update the current state
                self._cursor += num_fields

            else:
                self._cursor += 1

        # Create the DataFrame
        df = pd.DataFrame(df_data)
        df.set_index(["satellite", "session"])
        return df
