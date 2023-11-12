'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

This file contains public methods that can calculate various
astrophysical parameters. These include fetching planetary gravity
or return the position and velocity from an orbit.
'''

import math
import numpy as np
from . import constants
from . import value
from .. import NominalException


def get_planet_mu (planet: str) -> float:
    '''
    Returns the planet's gravitational mu parameter, equal to GM of the
    planet's body in units of [m^3/s^2]. If the planet does not exist,
    then an exception will be thrown.
    '''
    
    # Check if the value is valid
    param = "%s_MU" % planet.upper()
    if hasattr(constants, param):
        return float(getattr(constants, param))
    
    # Throw an error if this occurs
    else:
        raise NominalException("No planet or body named '%s' exists." % planet)


def t_perifocal_to_pci(right_ascension: float = 0, argument_of_periapsis: float = 0, inclination: float = 0) -> np.ndarray:
    """
    Creates the transformation matrix to convert perifocal coordinates into Planet-Centered Inertial (PCI) coordinates.

    This function computes the transformation matrix using the right ascension of the ascending node, the argument
    of periapsis, and the orbital inclination. These parameters are expected to be in radians.

    :param right_ascension: The right ascension of the ascending node in radians.
    :type right_ascension: float
    :param argument_of_periapsis: The argument of periapsis in radians.
    :type argument_of_periapsis: float
    :param inclination: The orbital inclination in radians.
    :type inclination: float
    :return: A 3x3 numpy matrix representing the transformation from perifocal to ECI coordinates.
    :rtype: numpy.matrix

    The transformation matrix is computed based on classical orbital elements, and it's used in orbital mechanics
    to convert coordinates from the perifocal (or orbital plane) coordinate system, where the x-axis points towards
    the periapsis, to the ECI coordinate system.
    """
    c_raan = np.cos(right_ascension)
    c_aop = np.cos(argument_of_periapsis)
    c_inc = np.cos(inclination)
    s_raan = np.sin(right_ascension)
    s_aop = np.sin(argument_of_periapsis)
    s_inc = np.sin(inclination)
    TIP = np.array([
        [c_aop * c_raan - s_aop * c_inc * s_raan, -s_aop * c_raan - c_aop * c_inc * s_raan, s_raan * s_inc],
        [c_aop * s_raan + s_aop * c_inc * c_raan, c_aop * c_inc * c_raan - s_aop * s_raan, -c_raan * s_inc],
        [s_aop * s_inc, c_aop * s_inc, c_inc]
    ], dtype=np.float64)
    return TIP


def perifocal_to_pci(
        r_bp_p: np.ndarray,
        v_bp_p: np.ndarray,
        right_ascension: float = 0,
        inclination: float = 0,
        argument_of_periapsis: float = 0,
) -> tuple:
    """
    Converts position and velocity vectors from perifocal to Planet-Centered Inertial (PCI) coordinates.

    Given position and velocity vectors in the perifocal coordinate system (PQW), along with orbital elements
    such as right ascension of the ascending node, inclination, and argument of perigee, this function
    transforms these vectors into the ECI coordinate system.

    :param r_bp_p: Position vector in perifocal coordinates.
    :type r_bp_p: numpy.ndarray
    :param v_bp_p: Velocity vector in perifocal coordinates.
    :type v_bp_p: numpy.ndarray
    :param right_ascension: Right ascension of the ascending node in radians. Defaults to 0.
    :type right_ascension: float
    :param inclination: Orbital inclination in radians. Defaults to 0.
    :type inclination: float
    :param argument_of_periapsis: Argument of periapsis in radians. Defaults to 0.
    :type argument_of_periapsis: float
    :return: Tuple of transformed position and velocity vectors in ECI coordinates.
    :rtype: (numpy.ndarray, numpy.ndarray)

    The transformation is performed using a matrix obtained from the `t_perifocal_to_vector` function, which
    constructs the transformation matrix based on the provided orbital elements.
    """
    TIP = t_perifocal_to_pci(
        right_ascension=right_ascension,
        argument_of_periapsis=argument_of_periapsis,
        inclination=inclination
    )
    # perform that matrix multiplication assuming that the position and velocity vector are 3x1 vectors
    r_bn_n = TIP @ r_bp_p
    v_bn_n = TIP @ v_bp_p
    return r_bn_n, v_bn_n


def semi_latus_rectum_to_pci(
        semi_latus_rectum: float,
        eccentricity: float = 0.0,
        inclination: float = 0.0,
        right_ascension: float = 0.0,
        argument_of_periapsis: float = 0.0,
        true_anomaly: float = 0.0,
        planet: str = "earth"
) -> tuple:
    """
    Transforms Keplerian orbital elements into position and velocity in Planet-Centered Inertial (PCI) coordinates.
        by taking semi-latus rectum as direct input, this function is valid for all orbits including parabolic and
        hyperbolic

    Given the Keplerian orbital elements, this function calculates the orbital state (position and velocity) in the PCI
    coordinate system. This transformation is essential in astrodynamics for orbit propagation and analysis.

    :param semi_latus_rectum: Semi-latus rectum of the orbit in meters.
    :type semi_latus_rectum: float
    :param eccentricity: Eccentricity of the orbit (default 0.0).
    :type eccentricity: float
    :param inclination: Inclination of the orbit in radians (default 0.0).
    :type inclination: float
    :param right_ascension: Right ascension of the ascending node in radians (default 0.0).
    :type right_ascension: float
    :param argument_of_periapsis: Argument of periapsis in radians (default 0.0).
    :type argument_of_periapsis: float
    :param true_anomaly: True anomaly at the epoch in radians (default 0.0).
    :type true_anomaly: float
    :param planet: Name of the central body being orbited (default "earth").
    :type planet: str
    :return: A tuple containing position and velocity vectors in PCI coordinates.
    :rtype: tuple

    The function first computes the gravitational parameter of the planet, then calculates the semi-latus rectum, and
    finally computes the position and velocity in perifocal coordinates. These are then transformed into PCI coordinates.
    """
    # find the gravitational parameter for the planet
    mu: float = get_planet_mu(planet)
    # position and velocity in perifocal coordinates
    denom = 1 + eccentricity * np.cos(true_anomaly)
    # calculate the perifocal position and velocity
    r_bp_p = np.array([
        semi_latus_rectum * np.cos(true_anomaly) / denom,
        semi_latus_rectum * np.sin(true_anomaly) / denom,
        0
    ])
    rat = np.sqrt(mu / semi_latus_rectum)
    v_bp_p = np.array([
        -rat * np.sin(true_anomaly),
        rat * (eccentricity + np.cos(true_anomaly)),
        0
    ])
    # calculate the pci position and velocity
    return perifocal_to_pci(
        r_bp_p=r_bp_p,
        v_bp_p=v_bp_p,
        right_ascension=right_ascension,
        argument_of_periapsis=argument_of_periapsis,
        inclination=inclination
    )


def keplerian_to_pci(
        semi_major_axis: float,
        eccentricity: float = 0.0,
        inclination: float = 0.0,
        right_ascension: float = 0.0,
        argument_of_periapsis: float = 0.0,
        true_anomaly: float = 0.0,
        planet: str = "earth"
) -> tuple:
    """
    Transforms Keplerian orbital elements into position and velocity in Planet-Centered Inertial (PCI) coordinates.

    Given the Keplerian orbital elements, this function calculates the orbital state (position and velocity) in the PCI
    coordinate system. This transformation is essential in astrodynamics for orbit propagation and analysis.

    :param semi_major_axis: Semi-major axis of the orbit in meters.
    :type semi_major_axis: float
    :param eccentricity: Eccentricity of the orbit (default 0.0).
    :type eccentricity: float
    :param inclination: Inclination of the orbit in radians (default 0.0).
    :type inclination: float
    :param right_ascension: Right ascension of the ascending node in radians (default 0.0).
    :type right_ascension: float
    :param argument_of_periapsis: Argument of periapsis in radians (default 0.0).
    :type argument_of_periapsis: float
    :param true_anomaly: True anomaly at the epoch in radians (default 0.0).
    :type true_anomaly: float
    :param planet: Name of the central body being orbited (default "earth").
    :type planet: str
    :return: A tuple containing position and velocity vectors in PCI coordinates.
    :rtype: tuple

    The function first computes the gravitational parameter of the planet, then calculates the semi-latus rectum, and
    finally computes the position and velocity in perifocal coordinates. These are then transformed into PCI coordinates.
    """
    # calculate the semi-latus rectum
    if eccentricity == 1:
        # parabolic orbit, the semi-latus rectum can't be calculated from input orbital elements. Therefore, the user
        #   should use an alternative function
        raise ValueError("The input orbit is parabolic. The semi-latus rectum can't be calculated, please use different function.")
    elif eccentricity >= 0:
        # circular, elliptical or hyperbolic orbit
        p = semi_major_axis * (1 - eccentricity * eccentricity)
    else:
        raise ValueError("The input eccentricity is invalid")
    return semi_latus_rectum_to_pci(
        semi_latus_rectum=p,
        eccentricity=eccentricity,
        inclination=inclination,
        right_ascension=right_ascension,
        argument_of_periapsis=argument_of_periapsis,
        true_anomaly=true_anomaly,
        planet=planet,
    )


def keplerian_to_pci_deg(
        semi_major_axis: float,
        eccentricity: float = 0.0,
        inclination: float = 0.0,
        right_ascension: float = 0.0,
        argument_of_periapsis: float = 0.0,
        true_anomaly: float = 0.0,
        planet: str = "earth"
) -> tuple:
    """
    Transforms Keplerian orbital elements into position and velocity in Planet-Centered Inertial (PCI) coordinates.

    Given the Keplerian orbital elements, this function calculates the orbital state (position and velocity) in the PCI
    coordinate system. This transformation is essential in astrodynamics for orbit propagation and analysis.

    :param semi_major_axis: Semi-major axis of the orbit in meters.
    :type semi_major_axis: float
    :param eccentricity: Eccentricity of the orbit (default 0.0).
    :type eccentricity: float
    :param inclination: Inclination of the orbit in degrees (default 0.0).
    :type inclination: float
    :param right_ascension: Right ascension of the ascending node in degrees (default 0.0).
    :type right_ascension: float
    :param argument_of_periapsis: Argument of periapsis in degrees (default 0.0).
    :type argument_of_periapsis: float
    :param true_anomaly: True anomaly at the epoch in degrees (default 0.0).
    :type true_anomaly: float
    :param planet: Name of the central body being orbited (default "earth").
    :type planet: str
    :return: A tuple containing position and velocity vectors in PCI coordinates.
    :rtype: tuple

    The function first computes the gravitational parameter of the planet, then calculates the semi-latus rectum, and
    finally computes the position and velocity in perifocal coordinates. These are then transformed into PCI coordinates.
    """
    return keplerian_to_pci(
        semi_major_axis=semi_major_axis,
        eccentricity=eccentricity,
        inclination=np.radians(inclination),
        right_ascension=np.radians(right_ascension),
        argument_of_periapsis=np.radians(argument_of_periapsis),
        true_anomaly=np.radians(true_anomaly),
        planet=planet
    )
