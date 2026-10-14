from importlib.metadata import version as _version

from .gnsstime import gnsstime
from .trilateration import Trilateration

__all__ = [
    "__version__",
    "gnsstime",
    "Trilateration",
]


__version__ = _version("gnsstools")
