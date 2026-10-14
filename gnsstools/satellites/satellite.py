from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, NoReturn

import numpy as np

from gnsstools.gnsstime import gnsstime, to_gnsstime


class Satellite(ABC):
    def __init__(self, prn: int | None, toc: datetime | np.datetime64 | None) -> None:
        self._prn = prn
        self._toc = to_gnsstime(toc)

    @property
    @abstractmethod
    def system(self) -> str:
        """The one-letter code of the constellation (e.g. ``"G"`` for GPS)."""

    @property
    def prn(self) -> int | None:
        return self._prn

    @property
    def toc(self) -> gnsstime:
        return self._toc

    def position(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise NotImplementedError("This method is currently not available. Make a PR if you wish to update gnsstools.")

    def __repr__(self) -> str:
        rep = f"{self.__class__.__name__}("
        rep += f"\n  system: {self.system}"
        rep += f"\n  prn: {self.prn}"
        rep += f"\n  toc: {self.toc}"
        for attr, value in self.__dict__.items():
            if attr[0] != "_":
                rep += f"\n  {attr}: {value:.6e}"
        rep += "\n)"
        return rep
