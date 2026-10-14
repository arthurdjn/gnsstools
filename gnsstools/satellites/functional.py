import numpy as np
from numpy.typing import NDArray

from gnsstools.const import F, mu
from gnsstools.gnsstime import gnsstime

from .galileo import Galileo
from .gps import GPS


def _required(value: float | None, name: str) -> float:
    if value is None:
        raise ValueError(f"The ephemeris has no {name}.")
    return value


def get_satellite_position(satellite: GPS | Galileo, date: gnsstime) -> tuple[NDArray[np.float64], float]:
    sqrt_a = _required(satellite.sqrt_a, "sqrt_a")
    delta_n = _required(satellite.delta_n, "delta_n")
    m0 = _required(satellite.m0, "m0")
    e = _required(satellite.e, "e")
    perigee = _required(satellite.omega, "omega")
    crs = _required(satellite.crs, "crs")
    crc = _required(satellite.crc, "crc")
    cus = _required(satellite.cus, "cus")
    cuc = _required(satellite.cuc, "cuc")
    cis = _required(satellite.cis, "cis")
    cic = _required(satellite.cic, "cic")
    i0 = _required(satellite.i0, "i0")
    idot = _required(satellite.idot, "idot")
    omega0 = _required(satellite.omega0, "omega0")
    omega_dot = _required(satellite.omega_dot, "omega_dot")
    # Galileo weeks are numbered like GPS weeks.
    week = (
        _required(satellite.gps_week, "gps_week")
        if isinstance(satellite, GPS)
        else _required(satellite.gal_week, "gal_week")
    )
    sv_clock_bias = _required(satellite.sv_clock_bias, "sv_clock_bias")
    sv_clock_drift = _required(satellite.sv_clock_drift, "sv_clock_drift")
    sv_clock_drift_rate = _required(satellite.sv_clock_drift_rate, "sv_clock_drift_rate")

    # * Step 1
    # Convert specified date from mjd to time. Compute the time variation.
    dt = (date.mjd - satellite.toc.mjd) * 86_400
    # Compute mean movement n
    n0 = np.sqrt(mu / ((sqrt_a) ** 2) ** 3)
    n = n0 + delta_n

    # Compute mean anomaly at the specified time.
    M = m0 + n * dt

    # Solve Kepler equation with an iterative method.
    E0 = M
    E = M + e * np.sin(E0)
    max_steps = 100
    while np.abs(E0 - E) > 1e-9 and max_steps > 0:
        E0 = E
        E = M + e * np.sin(E0)
        max_steps -= 1

    # Compute satellite true anomaly.
    v_ = np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2)
    v = 2 * np.arctan(v_)

    # Compute distance Earth - Satellite (radius).
    r = (sqrt_a) ** 2 * (1 - e * np.cos(E))
    # Compute coordinates in the orbital plane.
    phi = perigee + v
    # Compute corrections.
    dr = crs * np.sin(2 * phi) + crc * np.cos(2 * phi)
    dphi = cus * np.sin(2 * phi) + cuc * np.cos(2 * phi)

    # Compute (x, y) in the orbital plane.
    x = (r + dr) * np.cos(phi + dphi)
    y = (r + dr) * np.sin(phi + dphi)

    # * Step 2
    # Plane corrections.
    di = cis * np.sin(2 * phi) + cic * np.cos(2 * phi)
    i = i0 + idot * dt + di
    omega = omega0 + omega_dot * dt

    # Transform cartesian to geocentric coordinates.
    Romega = np.array([[np.cos(omega), -np.sin(omega), 0], [np.sin(omega), np.cos(omega), 0], [0, 0, 1]])
    Ri = np.array([[1, 0, 0], [0, np.cos(i), -np.sin(i)], [0, np.sin(i), np.cos(i)]])
    Xorb = np.array([[x], [y], [0]])
    X_ECI = np.dot(np.dot(Romega, Ri), Xorb)

    # Transform to ECEF cartesian coordinates.
    omega_e = -7.2921151467e-5

    t_sow = date.sow
    if date.weeks0 > week:
        t_sow += 86_400 * 7
    R = np.array(
        [
            [np.cos(omega_e * t_sow), -np.sin(omega_e * t_sow), 0],
            [np.sin(omega_e * t_sow), np.cos(omega_e * t_sow), 0],
            [0, 0, 1],
        ]
    )
    X_ECEF = np.dot(R, X_ECI)

    # Compute satellite time error delta.
    dt_relat = F * sqrt_a * e * np.sin(E)
    dte = sv_clock_bias + sv_clock_drift * dt + sv_clock_drift_rate * dt**2 + dt_relat

    return X_ECEF.flatten(), dte
