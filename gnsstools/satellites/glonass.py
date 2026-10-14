# File: glonass.py
# Creation: Sunday January 24th 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


from datetime import datetime

import numpy as np

from .satellite import Satellite


class Glonass(Satellite):
    def __init__(
        self,
        prn: int | None = None,
        toc: datetime | np.datetime64 | None = None,
        sv_clock_bias: float | None = None,
        sv_rel_freq_bias: float | None = None,
        message_frame_time: float | None = None,
        x: float | None = None,
        dx: float | None = None,
        dx2: float | None = None,
        health: float | None = None,
        y: float | None = None,
        dy: float | None = None,
        dy2: float | None = None,
        freq_num: float | None = None,
        z: float | None = None,
        dz: float | None = None,
        dz2: float | None = None,
        age_op_info: float | None = None,
    ) -> None:
        super().__init__(prn=prn, toc=toc)
        self.sv_clock_bias = sv_clock_bias
        self.sv_rel_freq_bias = sv_rel_freq_bias
        self.message_frame_time = message_frame_time
        # Second row
        self.x = x
        self.dx = dx
        self.dx2 = dx2
        self.health = health
        # Third row
        self.y = y
        self.dy = dy
        self.dy2 = dy2
        self.freq_num = freq_num
        # Fourth row
        self.z = z
        self.dz = dz
        self.dz2 = dz2
        self.age_op_info = age_op_info

    @property
    def system(self) -> str:
        return "R"

    def __repr__(self) -> str:
        rep = "Glonass("
        rep += f"\n  system:              {self.system}"
        rep += f"\n  prn:                 {self.prn:d}"
        rep += f"\n  toc:                 {self.toc} [UTC] (Time Of Clock)"
        rep += f"\n  sv_clock_bias:      {self.sv_clock_bias: .6e} [s] (-TauN)"
        rep += f"\n  sv_rel_freq_bias:   {self.sv_rel_freq_bias: .6e} [s] (+GammaN)"
        rep += (
            f"\n  message_frame_time: {self.message_frame_time: .6e} [s] (tk + nd * 86400 in seconds of the UTC week)"
        )
        # Second line
        rep += f"\n  x:                  {self.x: .6e} [km] (satellite position X)"
        rep += f"\n  dx:                 {self.dx: .6e} [km/s] (velocity X dot)"
        rep += f"\n  dx2:                {self.dx2: .6e} [km/s2] (X acceleration)"
        rep += f"\n  health:             {self.health: 13} (0=healthy, 1=unhealthy)"
        # Third line
        rep += f"\n  y:                  {self.y: .6e} [km] (satellite position Y)"
        rep += f"\n  dy:                 {self.dy: .6e} [km/s] (velocity Y dot)"
        rep += f"\n  dy2:                {self.dy2: .6e} [km/s2] (Y acceleration)"
        rep += f"\n  freq_num:           {self.freq_num: 13} (frequency number)"
        # Fourth line
        rep += f"\n  z:                  {self.z: .6e} [km] (satellite position Z)"
        rep += f"\n  dz:                 {self.dz: .6e} [km/s] (velocity Z dot)"
        rep += f"\n  dz2:                {self.dz2: .6e} [km/s2] (Z acceleration)"
        rep += f"\n  age_op_info:        {self.age_op_info: 13} [days]"
        rep += "\n)"
        return rep
