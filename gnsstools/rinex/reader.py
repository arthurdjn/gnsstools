# Encoding: UTF-8
# File: rinex.py
# Creation: Monday January 25th 2021
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


import re
from abc import ABC, abstractmethod

# A field of a RINEX record, as converted by `ABCReader._eval`.
Value = int | float | str | None
# A row of the DataFrame built by a reader: the fields of a record, its date, system, PRN, etc.
Record = dict[str, object]


class ABCReader(ABC):
    def __init__(self, lines: list[str]) -> None:
        super().__init__()
        self.lines = lines
        self._cursor = 0

    @abstractmethod
    def read(self) -> object:
        """Parse the lines of the file."""

    @staticmethod
    def _eval(string: str) -> Value:
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
        except ValueError:
            pass
        # Else, return the stripped string
        return str(string)

    @classmethod
    def _eval_float(cls, string: str) -> float:
        """Like `_eval`, for the fields that must hold a number."""
        value = cls._eval(string)
        if not isinstance(value, (int, float)):
            raise ValueError(f"Expected a number, got {string!r}.")
        return value

    def _skip_header(self) -> None:
        while self._cursor < len(self.lines) and self.lines[self._cursor].strip() != "END OF HEADER":
            self._cursor += 1

    def _skip_blank_lines(self) -> None:
        while self._cursor < len(self.lines) and self.lines[self._cursor].strip() == "":
            self._cursor += 1
