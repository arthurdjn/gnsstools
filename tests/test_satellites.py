import inspect

import numpy as np
import pytest

from gnsstools import gnsstime
from gnsstools.rinex.datasets import NavigationDataFrame, PositionDataFrame
from gnsstools.satellites import GALILEO, GLONASS, GPS, Satellite
from gnsstools.satellites.funtional import get_satellite_position
from gnsstools.utils import camel2snake

from .conftest import record


@pytest.mark.parametrize(
    ("system", "prn", "date", "cls", "toc"),
    [
        ("G", 1, gnsstime(2018, 10, 12, 0, 40, 15), GPS, gnsstime(2018, 10, 12)),
        ("G", 1, gnsstime(2018, 10, 12, 1, 30), GPS, gnsstime(2018, 10, 12, 2)),
        ("R", 1, gnsstime(2018, 10, 12, 0, 40), GLONASS, gnsstime(2018, 10, 12, 0, 45)),
        ("E", 1, gnsstime(2018, 10, 12, 1), GALILEO, gnsstime(2018, 10, 12, 0, 50)),
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


@pytest.mark.xfail(reason="When an epoch has several records, select drops them all and returns an empty ephemeris")
def test_select_an_epoch_with_several_records(nav3: NavigationDataFrame) -> None:
    satellite = nav3.select("E", 1, gnsstime(2018, 10, 12, 1))
    assert isinstance(satellite, GALILEO)
    assert satellite.sqrt_a == 5.440611371994e03


@pytest.mark.parametrize(
    ("system", "cls"),
    [
        ("G", GPS),
        ("R", GLONASS),
        pytest.param("E", GALILEO, marks=pytest.mark.xfail(reason="IODnav and BGDe5a/b map to io_dnav and bg_de5a/b")),
    ],
)
def test_every_navigation_field_is_a_satellite_argument(
    nav3: NavigationDataFrame, system: str, cls: type[Satellite]
) -> None:
    fields = nav3.loc[[system]].dropna(axis=1, how="all").columns
    parameters = inspect.signature(cls).parameters
    assert [field for field in fields if camel2snake(field) not in parameters] == []


@pytest.mark.parametrize(("system", "name"), [("G", "GPS("), ("R", "GLONASS(")])
def test_repr(nav3: NavigationDataFrame, system: str, name: str) -> None:
    text = repr(nav3.select(system, 1, gnsstime(2018, 10, 12, 1)))
    assert text.startswith(name)
    assert "toc:" in text


def test_galileo_repr(nav3: NavigationDataFrame) -> None:
    # Built by hand: select() returns an empty ephemeris for E01 (see test_select_an_epoch_with_several_records).
    record = nav3.loc[[("E", 1, gnsstime(2018, 10, 12, 0, 50))]].iloc[0].dropna()
    names = {"IODnav": "iod_nav", "BGDe5a": "bgd_e5a", "BGDe5b": "bgd_e5b"}  # See test_camel2snake
    fields = {names.get(str(key), camel2snake(str(key))): value for key, value in record.items()}
    text = repr(GALILEO(prn=1, toc=gnsstime(2018, 10, 12, 0, 50), **fields))
    assert text.startswith("GALILEO(")
    assert "sqrt_a:" in text


@pytest.mark.parametrize("date", [gnsstime(2018, 10, 12), gnsstime(2018, 10, 12, 0, 45), gnsstime(2018, 10, 12, 1, 30)])
def test_broadcast_orbit_matches_precise_orbit(
    nav3: NavigationDataFrame, sp3: PositionDataFrame, date: gnsstime
) -> None:
    satellite = nav3.select("G", 1, gnsstime(2018, 10, 12))
    assert isinstance(satellite, GPS)
    position, clock = get_satellite_position(satellite, date)
    precise = record(sp3, ("G", 1, date))
    # Broadcast orbits are good to a few meters. SP3 positions are in kilometers.
    assert np.linalg.norm(position - np.array(precise["Position"].coords[0]) * 1e3) < 3.0
    # SP3 clocks (microseconds) do not include the periodic relativistic correction, up to ~20 ns for GPS.
    assert abs(clock - precise["Clock"] * 1e-6) < 30e-9
