# File: __init__.py
# Creation: Tuesday January 12th 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin

from importlib.metadata import version as _version

from .gnsstime import gnsstime
from .trilateration import Trilateration

__all__ = [
    "__version__",
    "gnsstime",
    "Trilateration",
]


__version__ = _version("gnsstools")
