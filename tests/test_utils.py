import pytest

from gnsstools.utils import camel2snake


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("SVClockBias", "sv_clock_bias"),
        ("sqrtA", "sqrt_a"),
        ("OmegaDot", "omega_dot"),
        ("GPSWeek", "gps_week"),
        ("TOE", "toe"),
        ("dX2", "dx2"),
        ("e", "e"),
    ],
)
def test_camel2snake(name: str, expected: str) -> None:
    assert camel2snake(name) == expected
