# File: orbit_sp3.py
# Creation: Friday January 22nd 2021
# Author: Arthur Dujardin
# ------
# Copyright (c) 2021 Arthur Dujardin


# Basic imports
import numpy as np

# GNSS ToolBox
from gnsstools.logger import logger


class OrbitSP3:
    """
    Classe orbits à surcharger.
    
    """

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
    
    def __repr__(self):
        for s in self.__dict__:
            print('%-35s : ' %(s), self.__dict__.get(s))