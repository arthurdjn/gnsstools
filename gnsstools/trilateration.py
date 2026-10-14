# File: trilat.py
# Creation: Tuesday January 12th 2021
# Author: Arthur Dujardin
# ------
# Copy_recight (c) 2021 Arthur Dujardin


from typing import Any

import numpy as np
from numpy.typing import NDArray


class Trilateration:
    def __init__(
        self,
        sat_coords: NDArray[np.float64],
        distances: NDArray[np.float64],
        rec_coords: NDArray[np.float64] | None = None,
        cdt: float = 0,
        sigma: float = 1,
    ) -> None:
        # Satellites position
        if sat_coords.ndim != 2 or sat_coords.shape[1] != 3 or len(sat_coords) < 4:
            raise ValueError(
                "The satellites coordinates must be represented as a matrix of shape (N, 3), where N >= 4. "
                f"Got a shape of {sat_coords.shape}."
            )
        self.sat_coords = sat_coords

        # Observation distances (Satellites - Receptor)
        if len(distances) != len(sat_coords):
            raise ValueError(
                "The length of observed distances should be equals to the number of satellites. "
                f"Got {len(distances)} distances and {len(sat_coords)} satellites."
            )
        self.distances = distances.flatten()

        # Receptor position
        if rec_coords is None:
            rec_coords = np.zeros(3)
        self.rec_coords = rec_coords.flatten()

        # Time delay * celerity
        self.cdt = cdt

        # Parameters / variances
        self.sigma = sigma

        # Optimizer initial state
        self.Qx: NDArray[np.floating[Any]] = np.zeros((4, 4))
        self.v: NDArray[np.floating[Any]] = np.zeros((4, 1))
        self.sigma0_2: float = 1

    def optimize(self, max_steps: int | None = None, epsilon: float = 1e-6) -> tuple[NDArray[np.float64], float]:
        """Solve the position and the clock offset of the receiver by least squares (Gauss-Newton).

        The residuals, the variance factor and the covariance of the parameters are stored in :attr:`v`,
        :attr:`sigma0_2` and :attr:`Qx`. With 4 satellites (no redundancy), the variance factor cannot be estimated
        and keeps its a priori value, 1.

        Args:
            max_steps (int, optional): Maximum number of iterations. Defaults to 20.
            epsilon (float, optional): Stop when the update of the parameters is smaller than this, in meters.
                Defaults to ``1e-6``.

        Returns:
            tuple: The coordinates of the receiver, of shape (3,), and its clock offset times the speed of light.
        """
        nb_sat = len(self.sat_coords)
        redundancy = nb_sat - 4
        P = np.linalg.inv(self.sigma**2 * np.eye(nb_sat))
        N = np.eye(4)

        # Initial state: x, y, z and c * dt
        x0: NDArray[np.float64] = np.array([*self.rec_coords, self.cdt], dtype=np.float64).reshape((-1, 1))
        for _ in range(max_steps or 20):
            # Jacobian matrix
            rec_coords, cdt = x0[:3, 0], x0[3, 0]
            delta = rec_coords - self.sat_coords
            distance = np.linalg.norm(delta, axis=1)
            A = np.column_stack((delta / distance[:, np.newaxis], np.ones(nb_sat)))

            # Observation - Model
            B = (self.distances - (distance + cdt)).reshape((-1, 1))

            # Update the parameters vector
            N = A.T @ P @ A
            dx = np.linalg.solve(N, A.T @ P @ B)
            x0 = x0 + dx

            # Residual errors and variance factor
            self.v = B - A @ dx
            self.sigma0_2 = (self.v.T @ P @ self.v).item() / redundancy if redundancy > 0 else 1.0
            if np.linalg.norm(dx) < epsilon:
                break

        self.Qx = self.sigma0_2 * np.linalg.inv(N)
        return x0[:3, 0], float(x0[3, 0])

    def __call__(self, max_steps: int | None = None, epsilon: float = 1e-6) -> tuple[NDArray[np.float64], float]:
        return self.optimize(max_steps, epsilon)
