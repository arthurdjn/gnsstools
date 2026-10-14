import warnings

from .functional import get_satellite_position
from .galileo import Galileo
from .glonass import Glonass
from .gps import GPS
from .satellite import Satellite

__all__ = [
    "GPS",
    "Galileo",
    "Glonass",
    "Satellite",
    "get_satellite_position",
]

# The names of the classes before they followed PEP 8.
_DEPRECATED: dict[str, type[Satellite]] = {"GALILEO": Galileo, "GLONASS": Glonass}


def __getattr__(name: str) -> type[Satellite]:
    if name in _DEPRECATED:
        cls = _DEPRECATED[name]
        warnings.warn(
            f"gnsstools.satellites.{name} is deprecated, use gnsstools.satellites.{cls.__name__} instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return cls
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
