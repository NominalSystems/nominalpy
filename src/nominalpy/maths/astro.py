#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2023.

'''
This module contains public methods that can calculate various
astrophysical parameters. These include fetching planetary gravity
or return the position and velocity from an orbit.
'''

import numpy as np
from . import constants
from . import value
from . import utils
from ..utils import NominalException


def get_planet_mu (planet: str) -> float:
    '''
    Returns the planet's gravitational mu parameter, equal to GM of the
    planet's body in units of [m^3/s^2]. If the planet does not exist,
    then an exception will be thrown.

    :param planet:  The name of the planet to fetch the MU from
    :type planet:   str

    :returns:       The gravitational MU parameter
    :rtype:         float
    '''
    
    # Check if the value is valid
    param = "%s_MU" % planet.upper()
    if hasattr(constants, param):
        return float(getattr(constants, param))
    
    # Throw an error if this occurs
    else:
        raise NominalException("No planet or body named '%s' exists." % planet)

def t_perifocal_to_vector_elements (
    right_ascension: float = 0,
    argument_of_periapsis: float = 0,
    inclination: float = 0
)-> np.ndarray:
    '''
    Creates the transformation matrix to convert perifocal coordinates into 
    Planet-Centered Inertial (PCI) coordinates.

    This function computes the transformation matrix using the right ascension 
    of the ascending node, the argument of periapsis, and the orbital inclination. 
    These parameters are expected to be in radians. The transformation matrix 
    is computed based on classical orbital elements, and it's used in orbital 
    mechanics to convert coordinates from the perifocal (or orbital plane) 
    coordinate system, where the x-axis points towards the periapsis, to the 
    PCI coordinate system.

    :param right_ascension:         The right ascension of the ascending node in radians
    :type right_ascension:          float
    :param argument_of_periapsis:   The argument of periapsis in radians
    :type argument_of_periapsis:    float
    :param inclination:             The orbital inclination in radians
    :type inclination:              float

    :returns:                       A 3x3 numpy matrix representing the transformation from perifocal to ECI coordinates.
    :rtype:                         numpy.matrix
    '''

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

def perifocal_to_vector_elements(
    r_bp_p: np.ndarray,
    v_bp_p: np.ndarray,
    right_ascension: float = 0,
    inclination: float = 0,
    argument_of_periapsis: float = 0,
) -> tuple:
    '''
    Converts position and velocity vectors from perifocal to Planet-Centered 
    Inertial (PCI) coordinates.

    Given position and velocity vectors in the perifocal coordinate system (PQW), 
    along with orbital elements such as right ascension of the ascending node, 
    inclination, and argument of perigee, this function transforms these vectors 
    into the ECI coordinate system. The transformation is performed using a matrix 
    obtained from the `t_perifocal_to_vector` function, which constructs the 
    transformation matrix based on the provided orbital elements.

    :param r_bp_p:                  Position vector in perifocal coordinates.
    :type r_bp_p:                   numpy.ndarray
    :param v_bp_p:                  Velocity vector in perifocal coordinates.
    :type v_bp_p:                   numpy.ndarray
    :param right_ascension:         Right ascension of the ascending node in radians. Defaults to 0.
    :type right_ascension:          float
    :param inclination:             Orbital inclination in radians. Defaults to 0.
    :type inclination:              float
    :param argument_of_periapsis:   Argument of periapsis in radians. Defaults to 0.
    :type argument_of_periapsis:    float

    :returns:                       Tuple of transformed position and velocity vectors in ECI coordinates.
    :rtype:                         (numpy.ndarray, numpy.ndarray)
    '''

    TIP = t_perifocal_to_vector_elements(
        right_ascension=right_ascension,
        argument_of_periapsis=argument_of_periapsis,
        inclination=inclination
    )
    # perform that matrix multiplication assuming that the position and velocity vector are 3x1 vectors
    r_bn_n = TIP @ r_bp_p
    v_bn_n = TIP @ v_bp_p
    return r_bn_n, v_bn_n

def semi_latus_rectum_to_vector_elements(
    semi_latus_rectum: float,
    eccentricity: float = 0.0,
    inclination: float = 0.0,
    right_ascension: float = 0.0,
    argument_of_periapsis: float = 0.0,
    true_anomaly: float = 0.0,
    planet: str = "earth"
) -> tuple:
    '''
    Transforms Keplerian orbital elements into position and velocity in Planet-Centered 
    Inertial (PCI) coordinates. by taking semi-latus rectum as direct input, this 
    function is valid for all orbits including parabolic and hyperbolic.

    Given the Keplerian orbital elements, this function calculates the orbital state 
    (position and velocity) in the PCI coordinate system. This transformation is essential 
    in astrodynamics for orbit propagation and analysis. The function first computes the 
    gravitational parameter of the planet, then calculates the semi-latus rectum, and 
    finally computes the position and velocity in perifocal coordinates. These are then 
    transformed into PCI coordinates.

    :param semi_latus_rectum:       Semi-latus rectum of the orbit in meters
    :type semi_latus_rectum:        float
    :param eccentricity:            Eccentricity of the orbit (default 0.0)
    :type eccentricity:             float
    :param inclination:             Inclination of the orbit in radians (default 0.0)
    :type inclination:              float
    :param right_ascension:         Right ascension of the ascending node in radians (default 0.0)
    :type right_ascension: f        loat
    :param argument_of_periapsis:   Argument of periapsis in radians (default 0.0)
    :type argument_of_periapsis:    float
    :param true_anomaly:            True anomaly at the epoch in radians (default 0.0)
    :type true_anomaly:             float
    :param planet:                  Name of the central body being orbited (default "earth")
    :type planet:                   str

    :returns:                       A tuple containing position and velocity vectors in PCI coordinates
    :rtype:                         tuple
    '''

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
    return perifocal_to_vector_elements(
        r_bp_p=r_bp_p,
        v_bp_p=v_bp_p,
        right_ascension=right_ascension,
        argument_of_periapsis=argument_of_periapsis,
        inclination=inclination
    )

def classical_to_vector_elements(
    semi_major_axis: float,
    eccentricity: float = 0.0,
    inclination: float = 0.0,
    right_ascension: float = 0.0,
    argument_of_periapsis: float = 0.0,
    true_anomaly: float = 0.0,
    planet: str = "earth"
) -> tuple:
    '''
    Transforms Keplerian orbital elements into position and velocity in Planet-Centered 
    Inertial (PCI) coordinates.

    Given the Keplerian orbital elements, this function calculates the orbital state 
    (position and velocity) in the PCI coordinate system. This transformation is
    essential in astrodynamics for orbit propagation and analysis. The function first 
    computes the gravitational parameter of the planet, then calculates the semi-latus 
    rectum, and finally computes the position and velocity in perifocal coordinates.
    These are then transformed into PCI coordinates.

    :param semi_major_axis:         Semi-major axis of the orbit in meters
    :type semi_major_axis:          float
    :param eccentricity:            Eccentricity of the orbit (default 0.0)
    :type eccentricity:             float
    :param inclination:             Inclination of the orbit in radians (default 0.0)
    :type inclination:              float
    :param right_ascension:         Right ascension of the ascending node in radians (default 0.0)
    :type right_ascension:          float
    :param argument_of_periapsis:   Argument of periapsis in radians (default 0.0)
    :type argument_of_periapsis:    float
    :param true_anomaly:            True anomaly at the epoch in radians (default 0.0)
    :type true_anomaly:             float
    :param planet:                  Name of the central body being orbited (default "earth")
    :type planet:                   str

    :returns:                       A tuple containing position and velocity vectors in PCI coordinates
    :rtype:                         tuple
    '''

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
    return semi_latus_rectum_to_vector_elements(
        semi_latus_rectum=p,
        eccentricity=eccentricity,
        inclination=inclination,
        right_ascension=right_ascension,
        argument_of_periapsis=argument_of_periapsis,
        true_anomaly=true_anomaly,
        planet=planet,
    )

def classical_to_vector_elements_deg(
    semi_major_axis: float,
    eccentricity: float = 0.0,
    inclination: float = 0.0,
    right_ascension: float = 0.0,
    argument_of_periapsis: float = 0.0,
    true_anomaly: float = 0.0,
    planet: str = "earth"
) -> tuple:
    '''
    Transforms Keplerian orbital elements into position and velocity in Planet-Centered 
    Inertial (PCI) coordinates.

    Given the Keplerian orbital elements, this function calculates the orbital state 
    (position and velocity) in the PCI coordinate system. This transformation is 
    essential in astrodynamics for orbit propagation and analysis. The function first 
    computes the gravitational parameter of the planet, then calculates the semi-latus 
    rectum, and finally computes the position and velocity in perifocal coordinates. 
    These are then transformed into PCI coordinates.

    :param semi_major_axis:         Semi-major axis of the orbit in meters
    :type semi_major_axis:          float
    :param eccentricity:            Eccentricity of the orbit (default 0.0)
    :type eccentricity:             float
    :param inclination:             Inclination of the orbit in degrees (default 0.0)
    :type inclination:              float
    :param right_ascension:         Right ascension of the ascending node in degrees (default 0.0)
    :type right_ascension:          float
    :param argument_of_periapsis:   Argument of periapsis in degrees (default 0.0)
    :type argument_of_periapsis:    float
    :param true_anomaly:            True anomaly at the epoch in degrees (default 0.0)
    :type true_anomaly:             float
    :param planet:                  Name of the central body being orbited (default "earth")
    :type planet:                   str

    :returns:                       A tuple containing position and velocity vectors in PCI coordinates
    :rtype:                         tuple
    '''

    return classical_to_vector_elements(
        semi_major_axis=semi_major_axis,
        eccentricity=eccentricity,
        inclination=np.radians(inclination),
        right_ascension=np.radians(right_ascension),
        argument_of_periapsis=np.radians(argument_of_periapsis),
        true_anomaly=np.radians(true_anomaly),
        planet=planet
    )


def vector_to_classical_elements(
    r_bn_n: np.ndarray,
    v_bn_n: np.ndarray,
    planet: str = "earth"
) -> tuple:
    '''
    Convert state vectors to classical orbital elements. This function 
    calculates the classical orbital elements from the given position 
    and velocity vectors. It supports different planetary bodies by 
    adjusting the gravitational parameter. The function calculates 
    various orbital elements including angular momentum, node vector, 
    eccentricity vector, semi-major axis, inclination, RAAN, argument 
    of periapsis, and true anomaly. It handles different types of orbits: 
    circular equatorial, equatorial elliptical, circular inclined, and 
    classical elliptical inclined.

    :param r_bn_n:              The position vector in a Cartesian coordinate system in metres.
    :type r_bn_n:               np.ndarray
    :param v_bn_n:              The velocity vector in the same Cartesian coordinate system as r_bn_n in metres per second.
    :type v_bn_n:               np.ndarray
    :param planet:              The name of the planet for which the gravitational parameter is needed. Defaults to 'earth'.
    :type planet:               str

    :returns:                   A tuple of classical orbital elements: semi-major axis, eccentricity, inclination, right ascension of the ascending node (RAAN), argument of periapsis, and true anomaly.
    :rtype:                     tuple

    :raises ArithmeticError:    If the orbit is parabolic, which is not supported by this function.
    '''

    # find the gravitational parameter for the planet
    mu: float = get_planet_mu(planet)
    # calculate the magnitude of the position and velocity vectors
    r_mag: float = np.linalg.norm(r_bn_n)
    v_mag: float = np.linalg.norm(v_bn_n)

    v_mag_sqrd: float = v_mag * v_mag
    r_mag_dot_v_mag: float = np.dot(r_bn_n, v_bn_n)

    # angular momentum
    H: np.ndarray = np.cross(r_bn_n, v_bn_n)

    # the NODE is the cross product of K = [0 0 1] and H. For efficiency, directly assign the cross product result
    NODE: np.ndarray = np.array([-H[1], H[0], 0])
    node: float = np.linalg.norm(NODE)

    # the eccentricity vector
    ECC: np.ndarray = (r_bn_n * (v_mag_sqrd - mu / r_mag) - v_bn_n * r_mag_dot_v_mag) / mu
    eccentricity: float = np.linalg.norm(ECC)  # eccentricity

    # find the type of orbit and adjust the orbital element set accordingly
    if eccentricity == 1:
        raise ArithmeticError("The orbit is parabolic. Consider using a different function.")
    # calculate the semi-major axis
    energy: float = v_mag_sqrd / 2 - mu / r_mag
    semi_major_axis: float = -mu / (2 * energy)
    # calculate the inclination
    inclination: float = np.arccos(H[2] / np.linalg.norm(H))
    if np.fabs(node) == 0:
        if eccentricity == 0:
            # circular equatorial orbit
            return (
                semi_major_axis,
                eccentricity,
                inclination,
                utils.acos_quadrant_check(r_bn_n[0], r_mag, r_bn_n[1]),  # true longitude
                0,
                0
            )
        else:
            # equatorial elliptical orbit
            return (
                semi_major_axis,
                eccentricity,
                inclination,
                0,
                utils.acos_quadrant_check(ECC[0], eccentricity, ECC[1]),  # longitude of periapsis
                utils.acos_quadrant_check(np.dot(ECC, r_bn_n), eccentricity * r_mag, r_mag_dot_v_mag)  # true anomaly
            )
    elif eccentricity == 0:
        # circular inclined orbit
        return (
            semi_major_axis,
            eccentricity,
            inclination,
            utils.acos_quadrant_check(NODE[0], node, NODE[1]),  # RAAN
            utils.acos_quadrant_check(np.dot(NODE, r_bn_n), node * r_mag, r_bn_n[2]),  # true argument of latitude
            0
        )
    else:
        # classical elliptical inclined orbit
        return (
            semi_major_axis,
            eccentricity,
            inclination,
            utils.acos_quadrant_check(NODE[0], node, NODE[1]),  # RAAN
            utils.acos_quadrant_check(np.dot(NODE, ECC), node * eccentricity, ECC[2]),  # argument of periapsis
            utils.acos_quadrant_check(np.dot(ECC, r_bn_n), eccentricity * r_mag, r_mag_dot_v_mag)  # true anomaly
        )