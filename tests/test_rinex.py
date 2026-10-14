import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point

from gnsstools import gnsstime, rinex
from gnsstools.rinex.datasets import NavigationDataFrame, ObservationDataFrame, PositionDataFrame
from gnsstools.rinex.obs2 import Rinex2ObsReader
from gnsstools.rinex.obs3 import Rinex3ObsReader
from gnsstools.rinex.utils import convert_georinex

from .conftest import NAV2, NAV2_GLONASS, NAV3, OBS2, OBS3, record

INDEX = ["System", "PRN", "Date"]


def test_navigation_header(nav3: NavigationDataFrame) -> None:
    assert nav3.attrs["Version"] == 3.03
    assert nav3.attrs["Type"] == "N"
    assert nav3.attrs["System"] == "M"
    assert nav3.attrs["PGM"] == "MergeMNfile.tcl"
    assert nav3.attrs["RunBy"] == "IGS"


def test_navigation_records(nav3: NavigationDataFrame) -> None:
    assert isinstance(nav3, NavigationDataFrame)
    assert nav3.index.names == INDEX
    assert nav3.index.is_monotonic_increasing
    counts = nav3.groupby(level=["System", "PRN"]).size().to_dict()
    assert counts == {("E", 1): 2, ("G", 1): 13, ("G", 2): 2, ("R", 1): 2}


def test_navigation_gps_values(nav3: NavigationDataFrame) -> None:
    row = record(nav3, ("G", 1, gnsstime(2018, 10, 12)))
    assert row["SVClockBias"] == -9.926548227668e-05
    assert row["SVClockDrift"] == -4.888534022029e-12
    assert row["M0"] == 1.406949795964
    assert row["e"] == 8.116716751829e-03
    assert row["sqrtA"] == 5.153665107727e03
    assert row["TOE"] == 432_000.0
    assert row["GPSWeek"] == 2022.0


def test_navigation_glonass_values(nav3: NavigationDataFrame) -> None:
    row = record(nav3, ("R", 1, gnsstime(2018, 10, 12, 0, 15)))
    assert row["SVClockBias"] == 3.331806510687e-05
    assert row["MessageFrameTime"] == 432_000.0
    assert (row["X"], row["Y"], row["Z"]) == (-6.855064453125e03, 1.633214501953e04, -1.835140966797e04)
    assert row["Health"] == 0.0
    assert row["FreqNum"] == 1.0


def test_navigation_galileo_values(nav3: NavigationDataFrame) -> None:
    # The same orbit is broadcast in the F/NAV and the I/NAV messages, with a clock for E1/E5a and one for E1/E5b.
    records = nav3.loc[[("E", 1, gnsstime(2018, 10, 12, 0, 50))]]
    assert len(records) == 2
    assert set(records["SVClockBias"]) == {-4.541045636870e-04, -4.541051457636e-04}
    assert set(records["IODnav"]) == {85.0}
    assert set(records["sqrtA"]) == {5.440611371994e03}


def test_navigation_galileo_data_sources(nav3: NavigationDataFrame) -> None:
    records = nav3.loc[[("E", 1, gnsstime(2018, 10, 12, 0, 50))]]
    assert "DataSources" in records.columns
    assert set(records["DataSources"]) == {258.0, 517.0}


@pytest.mark.parametrize(("path", "system"), [(NAV2, "G"), (NAV2_GLONASS, "R")])
def test_rinex2_navigation_matches_rinex3(nav3: NavigationDataFrame, path: Path, system: str) -> None:
    # The RINEX 2 files hold the same records as the RINEX 3 one, with the RINEX 2 layout.
    nav2 = rinex.load(path)
    assert isinstance(nav2, NavigationDataFrame)
    assert nav2.attrs["Version"] == 2.11
    assert nav2.attrs["System"] == system
    expected = nav3.loc[[system]].dropna(axis=1, how="all")
    pd.testing.assert_frame_equal(nav2[expected.columns], expected, check_frame_type=False)


def test_load_accepts_paths(nav3: NavigationDataFrame) -> None:
    pd.testing.assert_frame_equal(rinex.load(NAV3), nav3)


def test_rinex2_observation(obs2: ObservationDataFrame) -> None:
    assert isinstance(obs2, ObservationDataFrame)
    assert obs2.attrs["Version"] == 2.11
    assert obs2.attrs["Type"] == "O"
    assert obs2.index.names == INDEX
    assert sorted(obs2.columns) == sorted(
        ["L1", "C1", "D1", "S1", "L2", "P2", "D2", "S2", "P1", "C2", "L5", "C5", "D5", "S5", "Session"]
    )
    first_epoch = obs2.xs(gnsstime(2018, 10, 12, 1, 0, 15), level="Date")
    assert len(first_epoch) == 27
    assert set(first_epoch.index.get_level_values("System")) == {"E", "G", "R", "S"}


def test_rinex2_observation_values(obs2: ObservationDataFrame) -> None:
    row = record(obs2, ("G", 2, gnsstime(2018, 10, 12, 1, 0, 15)))
    assert row["C1"] == 23851268.160
    assert row["P2"] == 23851263.480
    assert row["D1"] == 1691.514
    assert row["S1"] == 44.0
    assert pd.isna(row["C5"])
    assert row["Session"] == 1


def test_rinex2_observation_ignores_flags(obs2: ObservationDataFrame) -> None:
    # The file reads "125339261.645 6": a signal strength of 6, no loss of lock indicator.
    assert obs2.loc[("G", 2, gnsstime(2018, 10, 12, 1, 0, 15)), "L1"] == 125339261.645


def test_rinex3_observation(obs3: ObservationDataFrame) -> None:
    assert isinstance(obs3, ObservationDataFrame)
    assert obs3.attrs["Version"] == 3.03
    assert obs3.attrs["Type"] == "O"
    assert obs3.index.names == INDEX
    assert sorted(obs3.columns) == ["C1C", "D1C", "L1C", "S1C", "Session"]
    assert len(obs3) == 6


def test_rinex3_observation_values(obs3: ObservationDataFrame) -> None:
    row = record(obs3, ("E", 7, gnsstime(2018, 10, 12, 1, 0, 30)))
    assert row["C1C"] == 28353767.980
    assert row["L1C"] == 149000049.348
    assert row["D1C"] == -3074.290
    assert row["S1C"] == 36.0
    assert row["Session"] == 2


def test_rinex3_observation_ignores_flags() -> None:
    lines = OBS3.read_text().splitlines()
    assert lines[7].startswith("G02")
    lines[7] = "G02  23851268.160 7 125339261.645 6        1691.514          44.000"
    row = record(Rinex3ObsReader(lines).read(), ("G", 2, gnsstime(2018, 10, 12, 1, 0, 15)))
    assert (row["C1C"], row["L1C"]) == (23851268.160, 125339261.645)


def test_rinex3_observation_with_100_satellites() -> None:
    lines = OBS3.read_text().splitlines()[:6] + ["> 2018 10 12 01 00 15.0000000  0100"]
    # The header declares observation types for GPS and Galileo.
    lines += [f"{system}{prn:02d}  23851268.160 7 125339261.645 6" for system in "GE" for prn in range(1, 51)]
    df = Rinex3ObsReader(lines).read()
    assert len(df) == 100
    assert set(df["L1C"]) == {125339261.645}


def test_observation_readers_accept_lines() -> None:
    df = Rinex2ObsReader(OBS2.read_text().split("\n")).read()
    assert len(df) == 80


def test_sp3(sp3: PositionDataFrame) -> None:
    assert isinstance(sp3, PositionDataFrame)
    assert sp3.index.names == INDEX
    assert sorted(sp3.columns) == ["Clock", "Position", "Session"]
    # 7 epochs of 51 satellites (32 GPS, 19 GLONASS).
    assert len(sp3) == 7 * 51
    assert sp3.groupby(level="System").size().to_dict() == {"G": 7 * 32, "R": 7 * 19}


def test_sp3_values(sp3: PositionDataFrame) -> None:
    row = record(sp3, ("G", 1, gnsstime(2018, 10, 12)))
    assert isinstance(row["Position"], Point)
    assert row["Position"].coords[0] == (-17852.839089, -6014.552104, 18675.309680)
    assert row["Clock"] == -99.264764
    assert sp3.loc[("G", 1, gnsstime(2018, 10, 12, 1, 30)), "Session"] == 7


def test_unknown_formats_need_georinex(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # A Hatanaka-compressed header: gnsstools does not read it and hands it over to georinex.
    path = tmp_path / "edf12850.18d"
    path.write_text(f"{'1.0':<20}{'COMPACT RINEX FORMAT':<40}CRINEX VERS   / TYPE\n")
    monkeypatch.setitem(sys.modules, "georinex", None)
    with pytest.raises(ImportError, match=r"gnsstools\[georinex\]"):
        rinex.load(str(path))


def test_convert_georinex_keeps_every_satellite() -> None:
    xr = pytest.importorskip("xarray")
    times = pd.to_datetime(["2018-10-12T00:00", "2018-10-12T02:00"])
    clock = [[1.0e-5, 2.0e-5], [1.1e-5, np.nan]]
    ds = xr.Dataset({"SVclockBias": (("time", "sv"), clock)}, coords={"time": times, "sv": ["G01", "E05"]})
    df = convert_georinex(ds)
    assert df.index.names == INDEX
    assert df.groupby(level=["System", "PRN"]).size().to_dict() == {("E", 5): 1, ("G", 1): 2}
