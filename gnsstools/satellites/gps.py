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

    def __init__(self, prn=None, toc=None,
                 sv_clock_bias=None, sv_clock_drift=None, sv_clock_drift_rate=None,
                 iode=None, crs=None, delta_n=None, m0=None,
                 cuc=None, e=None, cus=None, sqrt_a=None,
                 toe=None, cic=None, omega0=None, cis=None,
                 i0=None, crc=None, omega=None, omega_dot=None,
                 idot=None, l2_codes=None, gps_week=None, l2_pflag=None,
                 sv_acc=None, sv_health=None, tgd=None, iodc=None,
                 trans_time=None, fit_inter=None):
        super().__init__(prn=prn, toc=toc)
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
        self.sv_health = sv_health
        self.tgd = tgd
        self.iodc = iodc
        # Eighth row
        self.trans_time = trans_time
        self.fit_inter = fit_inter

    @property
    def system(self):
        return "G"

    def __repr__(self):
        rep = f"GPS("
        # First line
        rep += f"\n  system:               {self.system}"
        rep += f"\n  prn:                  {self.prn:d}"
        rep += f"\n  toc:                  {self.toc} [UTC] (Time Of Clock)"
        rep += f"\n  sv_clock_bias:       {self.sv_clock_bias: .6e} [s]"
        rep += f"\n  sv_clock_drift:      {self.sv_clock_drift: .6e} [s/s]"
        rep += f"\n  sv_clock_drift_rate: {self.sv_clock_drift_rate: .6e} [s/s2]"
        # Second line
        rep += f"\n  iode:                {self.iode: 13} (Issue Of Data, Ephemeris)"
        rep += f"\n  crs:                 {self.crs: .6e} [m]"
        rep += f"\n  delta_n:             {self.delta_n: .6e} [rad/s]"
        rep += f"\n  m0:                  {self.m0: .6e} [rad]"
        # Third line
        rep += f"\n  cuc:                 {self.cuc: .6e} [rad]"
        rep += f"\n  e:                   {self.e: .6e} (Eccentricity)"
        rep += f"\n  cus:                 {self.cus: .6e} [rad]"
        rep += f"\n  sqrt_a:              {self.sqrt_a: .6e} [sqrt(m)]"
        # Fourth line
        rep += f"\n  toe:                 {self.toe: .6e} [sec of GPS week] (Time Of Ephemeris)"
        rep += f"\n  cic:                 {self.cic: .6e} [rad]"
        rep += f"\n  omega0:              {self.omega0: .6e} [rad]"
        rep += f"\n  cis:                 {self.cis: .6e} [rad]"
        # Fifth line
        rep += f"\n  i0:                  {self.i0: .6e} [rad]"
        rep += f"\n  crc:                 {self.crc: .6e} [m]"
        rep += f"\n  omega:               {self.omega: .6e} [rad]"
        rep += f"\n  omega_dot:           {self.omega_dot: .6e} [rad/s]"
        # Sixth line
        rep += f"\n  idot:                {self.idot: .6e} [rad/s]"
        rep += f"\n  l2_codes:            {self.l2_codes: 13} (codes on L2 channel)"
        rep += f"\n  gps_week:            {self.gps_week: 13} (to go with TOE)"
        rep += f"\n  l2_pflag:            {self.l2_pflag: 13} (L2 P data flag)"
        # Seventh line
        rep += f"\n  sv_acc:              {self.sv_acc: .6e} [m]"
        rep += f"\n  sv_health:           {self.sv_health: .6e} (bits 17-22 w 3 sf 1)"
        rep += f"\n  tgd:                 {self.tgd: .6e} [s]"
        rep += f"\n  iodc:                {self.iodc: 13} (Issue Of Data, Clock)"
        # Eighth line
        rep += f"\n  trans_time:          {self.trans_time: .6e} [sec of GPS week] (e.g. derived from Z-count in Hand Over Word (HOW))"
        rep += f"\n  fit_inter:           {self.fit_inter: .6e} [hours] (Fit Interval in hours)"
        rep += f"\n)"
        return rep
