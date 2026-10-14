import numpy as np
import pandas as pd
import pytest

from gnsstools import Trilateration, gnsstime

# APPROX POSITION XYZ of the receiver in tests/data/edf1285b.18o (meters, ECEF).
RECEIVER = np.array([4253804.4427, -224255.7080, 4731475.5125])
CLOCK_OFFSET = 1_234.5  # Receiver clock offset times the speed of light (meters)


def satellites(sp3: pd.DataFrame, count: int) -> np.ndarray:
    positions = sp3.xs(gnsstime(2018, 10, 12), level="Date").loc["G", "Position"].iloc[:count]
    return np.array([point.coords[0] for point in positions]) * 1e3


@pytest.mark.parametrize(
    "count",
    [
        pytest.param(
            4,
            marks=pytest.mark.xfail(
                reason="With exactly 4 satellites sigma0^2 divides by zero and the iteration stops after one step"
            ),
        ),
        5,
        8,
    ],
)
def test_recovers_position_and_clock(sp3: pd.DataFrame, count: int) -> None:
    sat_coords = satellites(sp3, count)
    distances = np.linalg.norm(sat_coords - RECEIVER, axis=1) + CLOCK_OFFSET
    position, cdt = Trilateration(sat_coords, distances).optimize()
    np.testing.assert_allclose(position, RECEIVER, atol=1e-4)
    assert cdt == pytest.approx(CLOCK_OFFSET, abs=1e-4)


def test_call_runs_the_optimization(sp3: pd.DataFrame) -> None:
    sat_coords = satellites(sp3, 6)
    distances = np.linalg.norm(sat_coords - RECEIVER, axis=1)
    position, _ = Trilateration(sat_coords, distances)()
    np.testing.assert_allclose(position, RECEIVER, atol=1e-4)


def test_needs_four_satellites(sp3: pd.DataFrame) -> None:
    sat_coords = satellites(sp3, 3)
    with pytest.raises(AssertionError, match="N > 3"):
        Trilateration(sat_coords, np.linalg.norm(sat_coords - RECEIVER, axis=1))
