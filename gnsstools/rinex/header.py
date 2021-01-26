# Encoding: UTF-8
# File: header.py
# Creation: Tuesday January 26th 2021
# Supervisor: Daphné Lercier (dlercier)
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


# Basic imports
import math
import re


class RinexHeaderReader:

    def __init__(self, lines):
        self.lines = lines
        self._cursor = 0

    def read(self):
        raise NotImplementedError
