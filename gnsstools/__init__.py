# File: __init__.py
# Creation: Tuesday January 12th 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin

# Basic imports
import os

from .gnsstime import gnsstime
from .trilateration import Trilateration


__all__ = [
    "__version__",
    "gnsstime",
    "Trilateration",
]


ROOT = os.path.abspath(os.path.dirname(__file__))
__version__ = open(os.path.join(ROOT, "VERSION.md")).read().strip()
