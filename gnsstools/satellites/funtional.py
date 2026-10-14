"""Deprecated alias of :mod:`gnsstools.satellites.functional`."""

import warnings

from .functional import get_satellite_position

__all__ = ["get_satellite_position"]

warnings.warn(
    "gnsstools.satellites.funtional is deprecated, import from gnsstools.satellites.functional instead.",
    DeprecationWarning,
    stacklevel=2,
)
