from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from gnsstools import gnsstime, rinex
from gnsstools.rinex.datasets import NavigationDataFrame, ObservationDataFrame, PositionDataFrame

DATA_DIR = Path(__file__).parent / "data"

NAV3 = DATA_DIR / "BRDC00IGS_R_20182850000_01D_MN.rnx"
NAV2 = DATA_DIR / "brdc2850.18n"
NAV2_GLONASS = DATA_DIR / "brdc2850.18g"
OBS2 = DATA_DIR / "edf1285b.18o"
OBS3 = DATA_DIR / "ENSG00FRA_R_20182850100_01H_15S_MO.rnx"
SP3 = DATA_DIR / "COM20225_15M.SP3"


def record(df: pd.DataFrame, key: tuple[str, int, gnsstime]) -> "pd.Series[Any]":
    """The row of `df` at `key`, which must be unique."""
    # Merged navigation files repeat some epochs (e.g. the I/NAV and F/NAV messages of Galileo), so the index is not
    # unique and `.loc` would return a DataFrame for those.
    rows = df.loc[[key]]
    assert len(rows) == 1
    return rows.iloc[0]


@pytest.fixture(scope="session")
def nav3() -> NavigationDataFrame:
    df = rinex.load(str(NAV3))
    assert isinstance(df, NavigationDataFrame)
    return df


@pytest.fixture(scope="session")
def obs2() -> ObservationDataFrame:
    df = rinex.load(str(OBS2))
    assert isinstance(df, ObservationDataFrame)
    return df


@pytest.fixture(scope="session")
def obs3() -> ObservationDataFrame:
    df = rinex.load(str(OBS3))
    assert isinstance(df, ObservationDataFrame)
    return df


@pytest.fixture(scope="session")
def sp3() -> PositionDataFrame:
    df = rinex.load(str(SP3))
    assert isinstance(df, PositionDataFrame)
    return df
