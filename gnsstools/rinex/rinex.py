# Encoding: UTF-8
# File: rinex.py
# Creation: Monday January 25th 2021
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


# Basic imports
from abc import ABC
import re


class RinexReader(ABC):

    def __init__(self, lines):
        super().__init__()
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
            >>> _eval("    ")
                None
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

    def _skip_header(self):
        while self._cursor < len(self.lines) and self.lines[self._cursor].strip() != "END OF HEADER":
            self._cursor += 1

    def _skip_blank_lines(self):
        while self._cursor < len(self.lines) and self.lines[self._cursor].strip() == "":
            self._cursor += 1
