import importlib
import inspect
import sys

import numpy as np
import pytest

from gnsstools import gnsstime, satellites
from gnsstools.rinex.datasets import ATTRIBUTES, NavigationDataFrame, PositionDataFrame
from gnsstools.satellites import GPS, Galileo, Glonass, Satellite, get_satellite_position

from .conftest import record


@pytest.mark.parametrize(
    ("system", "prn", "date", "cls", "toc"),
    [
        ("G", 1, gnsstime(2018, 10, 12, 0, 40, 15), GPS, gnsstime(2018, 10, 12)),
        ("G", 1, gnsstime(2018, 10, 12, 1, 30), GPS, gnsstime(2018, 10, 12, 2)),
        ("R", 1, gnsstime(2018, 10, 12, 0, 40), Glonass, gnsstime(2018, 10, 12, 0, 45)),
        ("E", 1, gnsstime(2018, 10, 12, 1), Galileo, gnsstime(2018, 10, 12, 0, 50)),
    ],
)
def test_select_the_closest_ephemeris(
    nav3: NavigationDataFrame, system: str, prn: int, date: gnsstime, cls: type[Satellite], toc: gnsstime
) -> None:
    satellite = nav3.select(system, prn, date)
    assert satellite is not None
    assert type(satellite) is cls
    assert satellite.system == system
    assert satellite.prn == prn
    assert satellite.toc == toc


def test_select_sets_the_ephemeris(nav3: NavigationDataFrame) -> None:
    satellite = nav3.select("G", 1, gnsstime(2018, 10, 12))
    assert isinstance(satellite, GPS)
    assert satellite.sqrt_a == 5.153665107727e03
    assert satellite.e == 8.116716751829e-03
    assert satellite.gps_week == 2022.0


def test_select_an_epoch_with_several_records(nav3: NavigationDataFrame) -> None:
    # E01 has the F/NAV and the I/NAV records of the same epoch: the first one is used.
    satellite = nav3.select("E", 1, gnsstime(2018, 10, 12, 1))
    assert isinstance(satellite, Galileo)
    assert satellite.sqrt_a == 5.440611371994e03
    assert satellite.data_sources == 258.0


def test_select_an_unknown_satellite(nav3: NavigationDataFrame) -> None:
    with pytest.raises(ValueError, match="G05 is not in the dataset"):
        nav3.select("G", 5, gnsstime(2018, 10, 12))


def test_select_too_far_from_the_date(nav3: NavigationDataFrame) -> None:
    date = gnsstime(2018, 10, 12, 4)
    with pytest.raises(ValueError, match="3.17 hours away"):
        nav3.select("E", 1, date)
    satellite = nav3.select("E", 1, date, ignore_offset=True)
    assert satellite is not None
    assert satellite.toc == gnsstime(2018, 10, 12, 0, 50)


@pytest.mark.parametrize(("system", "cls"), [("G", GPS), ("R", Glonass), ("E", Galileo)])
def test_every_navigation_field_is_a_satellite_argument(
    nav3: NavigationDataFrame, system: str, cls: type[Satellite]
) -> None:
    fields = nav3.loc[[system]].dropna(axis=1, how="all").columns
    parameters = inspect.signature(cls).parameters
    assert [field for field in fields if ATTRIBUTES[field] not in parameters] == []


@pytest.mark.parametrize(("system", "name"), [("G", "GPS("), ("R", "Glonass(")])
def test_repr(nav3: NavigationDataFrame, system: str, name: str) -> None:
    text = repr(nav3.select(system, 1, gnsstime(2018, 10, 12, 1)))
    assert text.startswith(name)
    assert "toc:" in text


def test_galileo_repr(nav3: NavigationDataFrame) -> None:
    text = repr(nav3.select("E", 1, gnsstime(2018, 10, 12, 1)))
    assert text.startswith("Galileo(")
    assert "sqrt_a:" in text
    assert "data_sources:" in text


@pytest.mark.parametrize(
    ("system", "prn", "toc", "date"),
    [
        ("G", 1, gnsstime(2018, 10, 12), gnsstime(2018, 10, 12)),
        ("G", 1, gnsstime(2018, 10, 12), gnsstime(2018, 10, 12, 0, 45)),
        ("G", 1, gnsstime(2018, 10, 12), gnsstime(2018, 10, 12, 1, 30)),
        ("E", 1, gnsstime(2018, 10, 12, 0, 50), gnsstime(2018, 10, 12, 0, 30)),
        ("E", 1, gnsstime(2018, 10, 12, 0, 50), gnsstime(2018, 10, 12, 1, 30)),
    ],
)
def test_broadcast_orbit_matches_precise_orbit(
    nav3: NavigationDataFrame,
    sp3: PositionDataFrame,
    sp3_mgex: PositionDataFrame,
    system: str,
    prn: int,
    toc: gnsstime,
    date: gnsstime,
) -> None:
    satellite = nav3.select(system, prn, toc)
    assert isinstance(satellite, (GPS, Galileo))
    position, clock = get_satellite_position(satellite, date)
    precise = record(sp3 if system == "G" else sp3_mgex, (system, prn, date))
    # Broadcast orbits are good to a few meters.
    assert np.linalg.norm(position - precise[["X", "Y", "Z"]].to_numpy(dtype=float)) < 3.0
    # SP3 clocks do not include the periodic relativistic correction, up to ~20 ns for GPS.
    assert abs(clock - precise["Clock"]) < 30e-9


@pytest.mark.parametrize(("name", "cls"), [("GALILEO", Galileo), ("GLONASS", Glonass)])
def test_deprecated_class_names(name: str, cls: type[Satellite]) -> None:
    with pytest.warns(DeprecationWarning, match=f"use gnsstools.satellites.{cls.__name__}"):
        assert getattr(satellites, name) is cls


def test_deprecated_functional_module() -> None:
    sys.modules.pop("gnsstools.satellites.funtional", None)
    with pytest.warns(DeprecationWarning, match="gnsstools.satellites.functional"):
        module = importlib.import_module("gnsstools.satellites.funtional")
    assert module.get_satellite_position is get_satellite_position
