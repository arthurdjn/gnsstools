# File: __init__.py
# Creation: Sunday January 24th 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


from typing import Any

import pandas as pd

from .header import RinexHeaderReader
from .nav import RinexNavReader
from .obs2 import Rinex2ObsReader
from .obs3 import Rinex3ObsReader
from .sp3 import SP3Reader
from .utils import convert_georinex

__all__ = ["load"]


def load(filename: str, *args: Any, force: bool = False, **kwargs: Any) -> pd.DataFrame:
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
    with open(filename) as f:
        lines = f.read().split("\n")

    header = RinexHeaderReader(lines).read()
    version = header.get("Version", 3.04)
    dtype = header.get("Type", None)

    df: pd.DataFrame
    # TODO: georinex is not optimized. Recreate its main functionalities (only 'SP3' and 'crx' reader are missing)
    # Read Navigation data
    if dtype == "N":
        system = None
        if filename.endswith("n"):
            system = "G"
        elif filename.endswith("g"):
            system = "R"
        df = RinexNavReader(lines, system=system).read()
        df.attrs = dict(header.items())

    # Read observation data
    elif dtype == "O":
        if isinstance(version, (int, float)) and version < 3:
            df = Rinex2ObsReader(lines).read()
        else:
            df = Rinex3ObsReader(lines).read()
        df.attrs = dict(header.items())

    # Read SP3 data
    elif filename.lower().endswith(".sp3"):
        df = SP3Reader(lines).read()
        df.attrs = dict(header.items())

    # Read with GeoRinex package
    else:
        try:
            import georinex
        except ImportError as error:
            raise ImportError(
                f"Reading '{filename}' requires the optional 'georinex' package: pip install 'gnsstools[georinex]'"
            ) from error
        ds = georinex.load(filename, *args, **kwargs)
        df = convert_georinex(ds)

    return df
