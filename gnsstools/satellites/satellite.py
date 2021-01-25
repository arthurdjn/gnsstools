# File: satellite.py
# Creation: Saturday January 23rd 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


# Basic imports
from abc import ABC


class Satellite(ABC):
    """GNSS nav element class"""
    def __init__(self):
        self.tgps = gpst.gpstime()
        self.omega0 = None

    @property
    def const(self):
        raise NotImplemented