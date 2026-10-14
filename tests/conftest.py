from pathlib import Path

import pandas as pd
import pytest

from gnsstools import rinex

DATA_DIR = Path(__file__).parent / "data"

NAV3 = DATA_DIR / "BRDC00IGS_R_20182850000_01D_MN.rnx"
NAV2 = DATA_DIR / "brdc2850.18n"
OBS2 = DATA_DIR / "edf1285b.18o"
OBS3 = DATA_DIR / "ENSG00FRA_R_20182850100_01H_15S_MO.rnx"
SP3 = DATA_DIR / "COM20225_15M.SP3"


@pytest.fixture(scope="session")
def nav3() -> pd.DataFrame:
    return rinex.load(str(NAV3))


@pytest.fixture(scope="session")
def obs2() -> pd.DataFrame:
    return rinex.load(str(OBS2))


@pytest.fixture(scope="session")
def obs3() -> pd.DataFrame:
    return rinex.load(str(OBS3))


@pytest.fixture(scope="session")
def sp3() -> pd.DataFrame:
    return rinex.load(str(SP3))
