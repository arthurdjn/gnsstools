# File: satellite.py
# Creation: Saturday January 23rd 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


# Basic imports
from abc import ABC

# GNSS Tools
from gnsstools.gnsstime import to_gnsstime, gnsstime


class Satellite(ABC):
    def __init__(self, prn, toc):
        self._prn = prn
        self._toc = to_gnsstime(toc)

    @property
    def system(self):
        return None

    @property
    def prn(self):
        return self._prn

    @property
    def toc(self):
        return self._toc

    def position(self, *args, **kwargs):
        raise NotImplementedError("This method is currently not available. Make a PR if you wish to update gnsstools.")

    def __repr__(self):
        rep = f"{self.__class__.__name__}("
        rep += f"\n  system: {self.system}"
        rep += f"\n  prn: {self.prn}"
        rep == f"\n  toc: {self.toc}"
        for attr, value in self.__dict__.items():
            if attr[0] != "_":
                rep += f"\n  {attr}: {value:.6e}"
        rep += "\n)"
        return rep
