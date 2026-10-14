import numpy as np
import pytest
from numpy.typing import NDArray

from gnsstools import Trilateration, gnsstime
from gnsstools.rinex.datasets import PositionDataFrame

# APPROX POSITION XYZ of the receiver in tests/data/edf1285b.18o (meters, ECEF).
RECEIVER = np.array([4253804.4427, -224255.7080, 4731475.5125])
CLOCK_OFFSET = 1_234.5  # Receiver clock offset times the speed of light (meters)


def satellites(sp3: PositionDataFrame, count: int) -> NDArray[np.float64]:
    at_epoch = sp3.index.get_level_values("Date") == gnsstime(2018, 10, 12)
    gps = sp3.index.get_level_values("System") == "G"
    positions = sp3.loc[at_epoch & gps, "Position"].iloc[:count]
    return np.array([point.coords[0] for point in positions]) * 1e3


@pytest.mark.parametrize("count", [4, 5, 8])
def test_recovers_position_and_clock(sp3: PositionDataFrame, count: int) -> None:
    sat_coords = satellites(sp3, count)
    distances = np.linalg.norm(sat_coords - RECEIVER, axis=1) + CLOCK_OFFSET
    position, cdt = Trilateration(sat_coords, distances).optimize()
    np.testing.assert_allclose(position, RECEIVER, atol=1e-4)
    assert cdt == pytest.approx(CLOCK_OFFSET, abs=1e-4)


def test_call_runs_the_optimization(sp3: PositionDataFrame) -> None:
    sat_coords = satellites(sp3, 6)
    distances = np.linalg.norm(sat_coords - RECEIVER, axis=1)
    position, _ = Trilateration(sat_coords, distances)()
    np.testing.assert_allclose(position, RECEIVER, atol=1e-4)


def test_needs_four_satellites(sp3: PositionDataFrame) -> None:
    sat_coords = satellites(sp3, 3)
    with pytest.raises(ValueError, match="N >= 4"):
        Trilateration(sat_coords, np.linalg.norm(sat_coords - RECEIVER, axis=1))
    with pytest.raises(ValueError, match="Got 3 distances and 4 satellites"):
        Trilateration(satellites(sp3, 4), np.linalg.norm(sat_coords - RECEIVER, axis=1))


def test_variance_factor(sp3: PositionDataFrame) -> None:
    sat_coords = satellites(sp3, 8)
    noise = np.random.default_rng(0).normal(scale=2.0, size=len(sat_coords))
    trilateration = Trilateration(sat_coords, np.linalg.norm(sat_coords - RECEIVER, axis=1) + noise, sigma=2.0)
    position, _ = trilateration.optimize()
    assert np.linalg.norm(position - RECEIVER) < 20.0
    assert trilateration.v.shape == (8, 1)
    assert 0.1 < trilateration.sigma0_2 < 3.0
    assert np.all(np.isfinite(trilateration.Qx))


def test_without_redundancy_the_variance_factor_is_a_priori(sp3: PositionDataFrame) -> None:
    sat_coords = satellites(sp3, 4)
    trilateration = Trilateration(sat_coords, np.linalg.norm(sat_coords - RECEIVER, axis=1))
    trilateration.optimize()
    assert trilateration.sigma0_2 == 1.0
    assert np.all(np.isfinite(trilateration.Qx))


def test_stops_at_epsilon(sp3: PositionDataFrame) -> None:
    sat_coords = satellites(sp3, 6)
    distances = np.linalg.norm(sat_coords - RECEIVER, axis=1)
    # From the center of the Earth, the first update is thousands of kilometers long.
    rough, _ = Trilateration(sat_coords, distances).optimize(epsilon=1e9)
    precise, _ = Trilateration(sat_coords, distances).optimize()
    assert np.linalg.norm(rough - RECEIVER) > 1.0
    assert np.linalg.norm(precise - RECEIVER) < 1e-4
