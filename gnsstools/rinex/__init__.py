# File: __init__.py
# Creation: Sunday January 24th 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


# Basic imports

# GNSS Tools
from .utils import convert_georinex
from gnsstools.logger import logger
from gnsstools.rinex.header import RinexHeaderReader
from .nav import RinexNavReader
from .obs import Rinex3ObsReader, Rinex2ObsReader

try:
    import georinex
except:
    logger.warning("The package 'georinex' was not found. Please install it to handles more files: pip install georinex.")


__all__ = [
    "load"
]


def load(filename, *args, force=False, **kwargs):
    """Load any `RINEX` files, from ``.SP3`` and ``.rnx`` to ``.*o`` extensions.

    Args:
        filename (str): Path to the file to open.

    Returns:
        pandas.DataFrame

    Examples:
        >>> from gnsstools import rinex
        >>> # Load a RINEX file
        >>> df = rinex.load("BRDC00IGS_R_20182850000_01D_MN.rnx")
        >>> # Load a GLONASS navigation file
        >>> df = rinex.load("edf1285b.18g")
        >>> # Load a Navigation file
        >>> df = rinex.load("edf1285b.18n")
        >>> # Load an Observation file
        >>> df = rinex.load("edf1285b.18o")
        >>> # Load a SP3 file
        >>> df = rinex.load("COM20225_15M.SP3")
    """
    with open(filename, "r") as f:
        lines = f.read().split("\n")

    reader = RinexHeaderReader(lines)
    header = reader.read()
    version = header.get("Version", 3.03)
    dtype = header["Type"]
    print(header)

    df = None
    # TODO: georinex is not optimized. Recreate its main functionalities (only 'SP3' and 'o' reader are missing)
    # Read Navigation data
    if dtype == "N":
        reader = RinexNavReader(lines)
        df = reader.read()
        df.attrs = header

    # Read observation data
    elif dtype == "O":
        if version < 3:
            reader = Rinex2ObsReader(lines)
            df = reader.read()
            df.attrs = header
        else:
            reader = Rinex3ObsReader(lines)
            df = reader.read()
            df.attrs = header

    # Read SP3 data
    elif filename.endswith(".SP3"):
        ds = georinex.load(filename, *args, **kwargs)
        df = convert_georinex(ds)

    return df
