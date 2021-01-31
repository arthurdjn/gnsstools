# File: orbit.py
# Creation: Tuesday January 12th 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


# Basic imports
import numpy as np
import gpstime as gpst
import gnsstoolbox.orbits as orbits

# GNSS ToolBox
from gnsstools.const import mu, F
from gnsstools.logger import logger


class Orbit(orbits.orbit):
    """
    Classe orbite à surcharger.
    Elle hérite de la classe orbit définie dans le module orbits.py

    """

    def get_sat_coords(self, const, prn, mjd):
        """Calcul de la postion du satellite "const/prn" à un instant donné mjd"""

        eph = self.get_ephemeris(const, prn, mjd)
        logger.debug(f"sqrt_a={eph.sqrt_a} [m]")
        logger.debug(f"mjd={mjd} [mjd]")
        logger.debug(f"ephemeris.mjd={eph.mjd} [mjd]")

        x_ECEF, y_ECEF, z_ECEF, dte = 0, 0, 0, 0
        #############################################################################
        # A FAIRE (TP3)                                                             #
        #############################################################################

        #* Step 1
        logger.debug("Convert specified date from mjd to time. Compute the time variation.")
        t = gpst.gpstime(mjd=mjd)
        dt = (mjd - eph.mjd) * 86_400
        logger.debug(f"dt={dt}")

        logger.debug("Compute mean movement n.")
        n0 = np.sqrt(mu / ((eph.sqrt_a) ** 2) ** 3)
        n = n0 + eph.delta_n
        logger.debug(f"n0={n0}")
        logger.debug(f"n={n}")

        logger.debug("Compute mean anomaly at the specified time.")
        M = eph.M0 + n * dt
        logger.debug(f"M={M}")

        logger.debug("Solve Kepler equation with an iterative method.")
        E0 = M
        E = M + eph.e * np.sin(E0)
        max_steps = 100
        while np.abs(E0 - E) > 1e-9 and max_steps > 0:
            E0 = E
            E = M + eph.e * np.sin(E0)
            max_steps -= 1
        logger.debug(f"E={E}, precision={np.abs(E0-E)}, steps={100 - max_steps}")

        logger.debug("Compute satellite true anomaly.")
        v_ = np.sqrt((1 + eph.e) / (1 - eph.e)) * np.tan(E/2)
        v = 2 * np.arctan(v_)
        logger.debug(f"v={v}")

        logger.debug("Compute distance Earth - Satellite (radius).")
        r = (eph.sqrt_a)**2 * (1 - eph.e * np.cos(E))
        logger.debug(f"r={r}")

        logger.debug("Compute coordinates in the orbital plane.")
        phi = eph.omega + v
        logger.debug(f"phi={phi}")  

        logger.debug("Compute corrections.")
        dr = eph.crs * np.sin(2 * phi) + eph.crc * np.cos(2 * phi)
        logger.debug(f"dr={dr}")  

        dphi = eph.cus * np.sin(2 * phi) + eph.cuc * np.cos(2 * phi)
        logger.debug(f"dphi={dphi}")

        logger.debug("Compute (x, y) in the orbital plane.")
        x = (r + dr) * np.cos(phi + dphi)
        y = (r + dr) * np.sin(phi + dphi)
        logger.debug(f"(x, y)={x, y}")

        #* Step 2
        logger.debug("Plane corrections.")
        di = eph.cis * np.sin(2 * phi) + eph.cic * np.cos(2 * phi)
        i = eph.i0 + eph.IDOT * dt + di
        logger.debug(f"i={i}")
        logger.debug(f"di={di}")

        omega = eph.OMEGA0 + eph.OMEGA_DOT * dt
        logger.debug(f"omega={omega}")

        logger.debug("Transform cartesian to geocentric coordinates.")
        Romega = np.array([[np.cos(omega), -np.sin(omega), 0],
                           [np.sin(omega),  np.cos(omega), 0],
                           [0,  0, 1]])
        Ri = np.array([[1, 0, 0],
                       [0, np.cos(i), -np.sin(i)],
                       [0, np.sin(i),  np.cos(i)]])
        Xorb = np.array([[x],
                         [y],
                         [0]])
        X_ECI = np.dot(np.dot(Romega, Ri), Xorb)
        logger.debug(f"Xorb={Xorb.flatten()}")
        logger.debug(f"X_ECI={X_ECI.flatten()}")

        logger.debug("Transform to ECEF cartesian coordinates.")
        omega_e = -7.2921151467e-5
        logger.debug(f"omega_e={omega_e}")

        t_wsec = t.wsec
        if t.wk > eph.gps_wk:
            t_wsec += 86400 * 7
        R = np.array([[np.cos(omega_e * t_wsec), -np.sin(omega_e * t_wsec), 0],
                      [np.sin(omega_e * t_wsec),  np.cos(omega_e * t_wsec), 0],
                      [0,  0, 1]])
        X_ECEF = np.dot(R, X_ECI)
        logger.debug(f"X_ECEF={X_ECEF.flatten()}")

        logger.debug("Compute satellite time error delta.")
        dt_relat = F * eph.sqrt_a * eph.e * np.sin(E)
        logger.debug(f"dt_relat={dt_relat}")

        dte = eph.alpha0 + eph.alpha1 * dt + eph.alpha2 * dt**2 + dt_relat
        logger.debug(f"dte={dte}")

        return X_ECEF.flatten(), dte

    def pos_sat_sp3(self, const, prn, mjd, ordre):
        """Calcul de la postion du satellite ``const/prn`` à un instant donné mjd."""
        X, Y, Z, dte = 0, 0, 0, 0

        ###########################################################################
        # A COMPLETER (TP5)                                                       #
        ###########################################################################
    
        orb, nl = self.get_sp3(const, prn)
        # orb = [mjd, X, Y, Z, dte]
        print(f"orb_shape={orb.shape}")
        print(f"nl={nl}")
        print(f"mjd={mjd}")
        # print(np.array2string(orb, max_line_width=1_000_000, separator=",", edgeitems=100))
        
        # Closest index of mjd in orb (i.e. position of mjd in orb)
        position = np.abs(orb[:, 0] - mjd).argmin()
        index = max(position - 1, 0)
        
        # index should be at the center of ordre + 1 values,
        # i.e. at (ordre + 1)//2 values right - left.
        # Otherwise, quit
        center = (ordre + 1)//2
        if index < center:
            start_index = 0
        elif index > center:
            start_index = nl - ordre - 1
        else:
            start_index = index - center + 1
        end_index = start_index + ordre + 1
        
        # Load the data
        A = orb[start_index:end_index, :]

        # Lagrange
        N, _ = A.shape
        degree = N - 1
        Xs = 0.0
        Ys = 0.0
        Zs = 0.0
        clock = 0.0

        Lj = np.ones(degree)
        for j in range(0, degree):
            for k in range(0, degree):
                if k != j:
                    # Lagrange formula
                    Lj[j] = Lj[j] * (mjd - A[k, 0]) / (A[j, 0] - A[k, 0])
            # Update the coefficients
            Xs = Xs + Lj[j] * A[j, 1]
            Ys = Ys + Lj[j] * A[j, 2]
            Zs = Zs + Lj[j] * A[j, 3]
            clock = clock + Lj[j] * A[j, 4]
        
        # Convert to the right unit. Cf. Jacques Beilin documentation
        X = 1.0e3 * Xs
        Y = 1.0e3 * Ys
        Z = 1.0e3 * Zs
        dte = clock * 1.0e-6
        
        return X, Y, Z, dte