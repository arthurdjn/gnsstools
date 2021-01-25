# File: rinex.py
# Creation: Saturday January 23rd 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


"""
This module should be used to read any `RINEX` file.

.. note::
    The loaded dataset is a ``pandas.DataFrame`` object.

.. code-block:: python

    from gnsstools import rinex
    
    df = rinex.load("BRDC00IGS_R_20182850000_01D_MN.rnx")

"""


# GNSS Tools
from .rinex3 import Rinex3Reader


def load(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    first_line = lines[0]
    if "RINEX VERSION / TYPE" in first_line:
        version = int(first_line[:10])
        if version >= 3:
            return Rinex3Reader(lines).read()
