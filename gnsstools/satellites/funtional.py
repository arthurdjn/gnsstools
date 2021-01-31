# Encoding: UTF-8
# File: funtional.py
# Creation: Sunday January 31st 2021
# Author: Arthur Dujardin (arthurdjn)
# ------
# Copyright (c) 2021, Makina Corpus


# Basic imports
import numpy as np

# GNSS Tools
from gnsstools.const import mu, F


def get_satellite_position(satellite, date):
    # * Step 1
    # Convert specified date from mjd to time. Compute the time variation.
    dt = (date.mjd - satellite.toc.mjd) * 86_400
    # Compute mean movement n
    n0 = np.sqrt(mu / ((satellite.sqrt_a) ** 2) ** 3)
    n = n0 + satellite.delta_n

    # Compute mean anomaly at the specified time.
    M = satellite.m0 + n * dt

    # Solve Kepler equation with an iterative method.
    E0 = M
    E = M + satellite.e * np.sin(E0)
    max_steps = 100
    while np.abs(E0 - E) > 1e-9 and max_steps > 0:
        E0 = E
        E = M + satellite.e * np.sin(E0)
        max_steps -= 1

    # Compute satellite true anomaly.
    v_ = np.sqrt((1 + satellite.e) / (1 - satellite.e)) * np.tan(E/2)
    v = 2 * np.arctan(v_)

    # Compute distance Earth - Satellite (radius).
    r = (satellite.sqrt_a)**2 * (1 - satellite.e * np.cos(E))
    # Compute coordinates in the orbital plane.
    phi = satellite.omega + v
    # Compute corrections.
    dr = satellite.crs * np.sin(2 * phi) + satellite.crc * np.cos(2 * phi)
    dphi = satellite.cus * np.sin(2 * phi) + satellite.cuc * np.cos(2 * phi)

    # Compute (x, y) in the orbital plane.
    x = (r + dr) * np.cos(phi + dphi)
    y = (r + dr) * np.sin(phi + dphi)

    # * Step 2
    # Plane corrections.
    di = satellite.cis * np.sin(2 * phi) + satellite.cic * np.cos(2 * phi)
    i = satellite.i0 + satellite.idot * dt + di
    omega = satellite.omega0 + satellite.omega_dot * dt

    # Transform cartesian to geocentric coordinates.
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

    # Transform to ECEF cartesian coordinates.
    omega_e = -7.2921151467e-5

    t_sow = date.sow
    if date.weeks0 > satellite.gps_week:
        t_sow += 86_400 * 7
    R = np.array([[np.cos(omega_e * t_sow), -np.sin(omega_e * t_sow), 0],
                  [np.sin(omega_e * t_sow),  np.cos(omega_e * t_sow), 0],
                  [0,  0, 1]])
    X_ECEF = np.dot(R, X_ECI)

    # Compute satellite time error delta.
    dt_relat = F * satellite.sqrt_a * satellite.e * np.sin(E)
    dte = satellite.sv_clock_bias + satellite.sv_clock_drift * dt + satellite.sv_clock_drift_rate * dt**2 + dt_relat

    return X_ECEF.flatten(), dte
