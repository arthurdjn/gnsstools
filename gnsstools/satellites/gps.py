# File: gps.py
# Creation: Sunday January 24th 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


# Basic imports
import numpy as np
import pandas as pd

# GNSS Tools
from .satellite import Satellite
from gnsstools import gnsstime
from gnsstools.utils import camel2snake


class GPS(Satellite):

    def __init__(self, prn=None, date=None,
                 sv_clock_bias=None, sv_clock_drift=None, sv_clock_drift_rate=None,
                 iode=None, crs=None, delta_n=None, m0=None,
                 cuc=None, e=None, cus=None, sqrt_a=None,
                 toe=None, cic=None, omega0=None, cis=None,
                 i0=None, crc=None, omega=None, omega_dot=None,
                 idot=None, l2_codes=None, gps_week=None, l2_pflag=None,
                 sv_acc=None, sv_health=None, tgd=None, iodc=None,
                 trans_time=None, fit_inter=None):
        super().__init__(prn=prn, date=date)
        # First row
        self.sv_clock_bias = sv_clock_bias
        self.sv_clock_drift = sv_clock_drift
        self.sv_clock_drift_rate = sv_clock_drift_rate
        # Second row
        self.iode = iode
        self.crs = crs
        self.delta_n = delta_n
        self.m0 = m0
        # Third row
        self.cuc = cuc
        self.e = e
        self.cus = cus
        self.sqrt_a = sqrt_a
        # Fourth row
        self.toe = toe
        self.cic = cic
        self.omega0 = omega0
        self.cis = cis
        # Fifth row
        self.i0 = i0
        self.crc = crc
        self.omega = omega
        self.omega_dot = omega_dot
        # Sixth row
        self.idot = idot
        self.l2_codes = l2_codes
        self.gps_week = gps_week
        self.l2_pflag = l2_pflag
        # Seventh row
        self.sv_acc = sv_acc
        self.sv_heath = sv_health
        self.tgd = tgd
        self.iodc = iodc
        # Eighth row
        self.trans_time = trans_time
        self.fit_inter = fit_inter

    @property
    def system(self):
        return "G"
