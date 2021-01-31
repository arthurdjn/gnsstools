# File: galileo.py
# Creation: Sunday January 24th 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


from .satellite import Satellite


class GALILEO(Satellite):

    def __init__(self, prn=None, toc=None,
                 sv_clock_bias=None, sv_clock_drift=None, sv_clock_drift_rate=None,
                 iod_nav=None, crs=None, delta_n=None, m0=None,
                 cuc=None, e=None, cus=None, sqrt_a=None,
                 toe=None, cic=None, omega0=None, cis=None,
                 i0=None, crc=None, omega=None, omega_dot=None,
                 idot=None, gps_week=None, gal_week=None,
                 sisa=None, sv_health=None, bgd_e5a=None, bgd_e5b=None,
                 trans_time=None):
        super().__init__(prn=prn, toc=toc)
        # First row
        self.sv_clock_bias = sv_clock_bias
        self.sv_clock_drift = sv_clock_drift
        self.sv_clock_drift_rate = sv_clock_drift_rate
        # Second row
        self.iod_nav = iod_nav
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
        self.gps_week = gps_week
        self.gal_week = gal_week
        # Seventh row
        self.sisa = sisa
        self.sv_heath = sv_health
        self.bgd_e5a = bgd_e5a
        self.bgd_e5b = bgd_e5b
        # Eighth row
        self.trans_time = trans_time

    @property
    def system(self):
        return "E"

    def __repr__(self):
        rep = f"GALILEO("
        # First line
        rep += f"\n  system:               {self.system}"
        rep += f"\n  prn:                  {self.prn:d}"
        rep += f"\n  toc:                  {self.toc} [UTC] (Time Of Clock)"
        rep += f"\n  sv_clock_bias:       {self.sv_clock_bias: .6e} [s]"
        rep += f"\n  sv_clock_drift:      {self.sv_clock_drift: .6e} [s/s]"
        rep += f"\n  sv_clock_drift_rate: {self.sv_clock_drift_rate: .6e} [s/s2]"
        # Second line
        rep += f"\n  iod_nav:             {self.iod_nav: .6e} (Issue Of Data of the nav batch)"
        rep += f"\n  crs:                 {self.crs: .6e} [m]"
        rep += f"\n  delta_n:             {self.delta_n: .6e} [rad/s]"
        rep += f"\n  m0:                  {self.m0: .6e} [rad]"
        # Third line
        rep += f"\n  cuc:                 {self.cuc: .6e} [rad]"
        rep += f"\n  e:                   {self.e: .6e} (Eccentricity)"
        rep += f"\n  cus:                 {self.cus: .6e} [rad]"
        rep += f"\n  sqrt_a:              {self.sqrt_a: .6e} [sqrt(m)]"
        # Fourth line
        rep += f"\n  toe:                 {self.toe: .6e} [sec of GAL week] (Time Of Ephemeris)"
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
        rep += f"\n  l2_codes:            {self.l2_codes: .6e} (codes on L2 channel)"
        rep += f"\n  gal_week:            {self.gal_week: .6e} (to go with TOE)"
        # Seventh line
        rep += f"\n  sisa:                {self.sisa: .6e} [m] (Signal in space accuracy)"
        rep += f"\n  sv_health:           {self.sv_health: .6e} (See Galileo ICD Section 5.1.9.3)"
        rep += f"\n  bgd_e5a:             {self.bgd_e5a: .6e} [s] (BGD E5a/E1)"
        rep += f"\n  bgd_e5b:             {self.bgd_e5b: .6e} [s] (BGD E5b/E1)"
        # Eighth line
        rep += f"\n  trans_time:          {self.trans_time: .6e} [sec of GAL week] (e.g. derived from WN and TOW of page type 1)"
        rep += f"\n)"
        return rep
