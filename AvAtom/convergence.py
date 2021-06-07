"""
Module which handles convergence routines
"""

# standard libraries

# external libraries
import numpy as np

# internal modules
import mathtools
import config


class SCF:
    """
    Convergence attributes and functions related to SCF energy procedures

    Notes
    -----
    Contains the private attributes _energy, _potential and _density

    """

    def __init__(self):

        self._energy = np.zeros((2))
        self._potential = np.zeros((2, config.spindims, config.grid_params["ngrid"]))
        self._density = np.zeros((2, config.spindims, config.grid_params["ngrid"]))

    def check_conv(self, E_free, pot, dens, iscf):
        """
        Computes the changes in energy, integrated density and integrated potential
        and checks if they satisfy the proscribed convergence parameters

        Parameters
        ----------
        E_free : float
            the total free energy
        v_s : ndarray
            the KS potential
        dens : ndarray
            the electronic density
        iscf : int
            the iteration number

        Returns
        -------
        conv_vals : dict
            Dictionary of convergence parameters as follows:
            {'conv_energy' : float, 'conv_rho' : ndarray,
             'conv_pot' : ndarray, 'complete' : bool}

        """

        conv_vals = {}

        # first update the energy, potential and density attributes
        self._energy[0] = E_free
        self._potential[0] = pot
        self._density[0] = dens

        # compute the change in energy
        conv_vals["dE"] = abs((self._energy[0] - self._energy[1]) / self._energy[0])

        # compute the change in potential
        dv = np.abs(self._potential[0] - self._potential[1])
        # compute the norm
        norm_v = mathtools.int_sphere(np.abs(self._potential[0]), config.xgrid)
        conv_vals["dpot"] = mathtools.int_sphere(dv, config.xgrid) / norm_v

        # compute the change in density
        dn = np.abs(self._density[0] - self._density[1])
        # integrate over sphere to return a number
        conv_vals["drho"] = mathtools.int_sphere(dn, config.xgrid) / config.nele

        # reset the energy, potential and density attributes
        self._energy[1] = E_free
        self._potential[1] = pot
        self._density[1] = dens

        # see if the convergence criteria are satisfied
        conv_energy = False
        conv_rho = False
        conv_pot = False
        conv_vals["complete"] = False

        if iscf > 3:
            if conv_vals["dE"] < config.conv_params["econv"]:
                conv_energy = True
            if np.all(conv_vals["drho"] < config.conv_params["nconv"]):
                conv_rho = True
            if np.all(conv_vals["dpot"] < config.conv_params["vconv"]):
                conv_pot = True
            if conv_energy and conv_rho and conv_pot:
                conv_vals["complete"] = True

        return conv_vals
