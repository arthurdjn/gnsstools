# File: trilat.py
# Creation: Tuesday January 12th 2021
# Author: Arthur Dujardin
# ------
# Copy_recight (c) 2021 Arthur Dujardin


# Basic imports
import numpy as np

# GNSS ToolBox
from gnsstools.const import c


class Trilateration:

    def __init__(self, sat_coords, distances, rec_coords=None, cdt=0, sigma=1):
        # Satellites position
        nb_sat, nb_coords = sat_coords.shape
        assert nb_sat > 3 and nb_coords == 3, \
            f"The satellites coordinates must be represented as a matrix of shape (N, 3), where N > 3." \
            f"Got a shape of {sat_coords.shape}."
        self.sat_coords = sat_coords

        # Observation distances (Satellites - Receptor)
        assert len(distances) == len(sat_coords), \
            f"The length of observed distances should be equals to the number of satellites. " \
            f"Got {len(distances)} distances and {len(sat_coords)} satellites."
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
        self.Qx = np.zeros((4, 4))
        self.v = np.zeros((4, 1))
        self.sigma0_2 = 1

    def optimize(self, max_steps=None, epsilon=1e-6):
        """Calcul d'une trilatération simple avec un offset
        correspondant à l'erreur d'horloge du récepteur
        """
        nb_sat = len(self.sat_coords)

        # Satellite positions
        x_sat = self.sat_coords[:, 0]
        y_sat = self.sat_coords[:, 1]
        z_sat = self.sat_coords[:, 2]

        # Initial state
        x0 = np.array([self.rec_coords[0], self.rec_coords[1], self.rec_coords[2], self.cdt]).reshape((-1, 1))
        Kl = self.sigma**2 * np.eye(nb_sat)
        P = np.linalg.inv(Kl)
        N = np.zeros((4, 4))

        # Iterative process
        max_steps = max_steps or 20
        epsilon = 1e-6
        sigma0_2_previous = np.inf
        while max_steps > 0 and abs(sigma0_2_previous - self.sigma0_2) > epsilon:
            # Jacobian matrix
            x_rec, y_rec, z_rec, cdt = x0.flatten()
            distance = ((x_rec - x_sat)**2 + (y_rec - y_sat)**2 + (z_rec - z_sat)**2)**0.5
            f_prime_x = (x_rec - x_sat) / distance
            f_prime_y = (y_rec - y_sat) / distance
            f_prime_z = (z_rec - z_sat) / distance
            f_prime_cdt = np.ones(nb_sat)
            A = np.column_stack((f_prime_x, f_prime_y, f_prime_z, f_prime_cdt))

            # Observation - Model
            B = self.distances - (distance + cdt)
            B = B.reshape((-1, 1))

            # Optimization
            N = A.T @ P @ A
            K = A.T @ P @ B
            dx = np.linalg.inv(N) @ K

            # Update the parameters vector
            x0 = x0 + dx

            # Compute residual errors (MSE)
            self.v = B - A @ dx
            sigma0_2_previous = self.sigma0_2
            sigma0_2 = self.v.T @ P @ self.v / (nb_sat - 4)
            self.sigma0_2 = sigma0_2.item()  # Convert to scalar
            max_steps -= 1

        self.Qx = self.sigma0_2 * np.linalg.inv(N)
        rec_coords = x0.flatten()[:3]
        cdt = x0.flatten()[-1]
        return rec_coords, cdt

    def __call__(self, *args, **kwargs):
        return self.optimize(*args, **kwargs)
