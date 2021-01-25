# File: process.py
# Creation: Tuesday January 12th 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


# Basic imports
import re
import numpy as np
from gnsstoolbox.gnss_process import TrilatGps


# GNSS ToolBox
from gnsstools import Trilateration
from gnsstools.const import c
from gnsstools.logger import logger


class GNSSProcess:
    """GNSS proccess class"""

    def __init__(self):
        self.process = "spp"  # "DGNSS","phase"
        self.freq = "C1"
        self.X0 = np.zeros((3, 1))
        self.iono = 'none'
        self.nav = 'sp3'
        self.const = 'GRE'
        self.type = "o"


    def spp(self, epoch, orbit):
        """Process epoch using spp.

        Args:
            epoch (Epoch): Epoch to be processed.
            orbit (Orbit): Orbit object.

        Returns:
            tuple: Receptor coordinates and associated drift clock error.
        """
        obs_dist = []
        sat_coords = []

        self.nb_sat = len(epoch.satellites)

        mjd = epoch.tgps.mjd
        for satellite in epoch.satellites:

            logger.debug("Test if the satellite is part of the constellation.")
            if not(re.search(satellite.const, self.const)):
                continue

            observable = 'C1'
            satellite.PR = satellite.obs.get(observable)

            logger.debug("Test if observation is coherent.")
            if satellite.PR < 15e6:
                continue

            logger.debug("Test if satellite's navigation message is available.")
            eph = orbit.get_ephemeris(satellite.const, satellite.PRN, mjd)
            if not(hasattr(eph, 'mjd')):
                logger.warning(f"No orbit for satellite const={satellite.const}, PRN={satellite.PRN}")
                continue

            logger.debug(f"Current satellite: const={satellite.const}, PRN={satellite.PRN}")
            logger.debug(f"mjd={epoch.tgps.mjd}, observable={satellite.obs.get(observable)}")

            #! ------------------------------------------------------------------------ #
            #! TODO (TP10)                                                              #
            #!                                                                          #
            #! From now we have a valid observation and a usable navigation             #
            #! message for a satellite `sat` at a specified epoch.                      #
            #! ------------------------------------------------------------------------ #
            
            logger.debug(f"Compute time reception.")
            tr = epoch.tgps.mjd
            dt = (mjd - eph.mjd) * 86_400
            logger.debug(f"tr={tr} [mjd]")
            logger.debug(f"dt={dt} [s]")

            logger.debug(f"Compute travel time and emitted time.")
            travel_time = satellite.PR / c
            te = tr - travel_time / 86_400
            logger.debug(f"te={te} [mjd]")

            logger.debug(f"Compute clock drift.")
            dte = eph.alpha0 + eph.alpha1 * (tr - eph.TOC) + eph.alpha2 * (tr - eph.TOC) ** 2
            dte /= 86400.0
            logger.debug(f"dte={dte} [mjd]")

            logger.debug("Correct emitted time from clock drift.")
            te = te - dte
            logger.debug(f"te={te} [mjd]")

            logger.debug("Computing satellite coordinates.")
            (Xs, Ys, Zs), dts = orbit.get_sat_coords(satellite.const, satellite.PRN, te)
            logger.debug(f"Xs={Xs}, Ys={Ys}, Zs={Zs}, dte={dts}")

            logger.debug("Computing observed distances (satellite - receptor).")
            dist = satellite.PR + c * (dts)

            logger.debug("Adding observations.")
            obs_dist.append(dist)
            sat_coords.append([Xs, Ys, Zs])

        obs_dist = np.array(obs_dist)
        sat_coords = np.array(sat_coords)

        logger.debug("Compute receptor coordinates using trilateration.")
        # trilat = Trilateration(sat_coords, obs_dist)
        Xr, Yr, Zr, cdtr, sigma0_2, V, SigmaX = TrilatGps(sat_coords, obs_dist, np.zeros((4, 1)))
        logger.debug(f"Xr={Xr}, Yr={Yr}, Zr={Zr}, cdtr={cdtr}")

        return Xr, Yr, Zr, cdtr
