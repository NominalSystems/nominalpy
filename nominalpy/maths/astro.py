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


def classical_to_vector_elements_rad(semi_major_axis: float, eccentricity: float = 0.0,
    inclination: float = 0.0, right_ascension: float = 0.0, argument_of_periapsis: float = 0.0,
    true_anomaly: float = 0.0, planet: str = "earth") -> tuple:
    """
    Converts classical Keplerian elements to state vector (position and velocity).

    This function calculates the state vector from a set of classical
    Keplerian elements. The semi-major axis should be in kilometers, eccentricity
    should be between 0 and 1, and the angular elements (inclination, right ascension,
    argument of periapsis, and true anomaly) should be in radians. The function
    returns the position and velocity in meters and meters per second, respectively,
    formatted as JSON strings.

    :param semi_major_axis: The semi-major axis in kilometers.
    :type semi_major_axis: float
    :param eccentricity: The orbital eccentricity (default 0.0).
    :type eccentricity: float
    :param inclination: The inclination in radians (default 0.0).
    :type inclination: float
    :param right_ascension: The right ascension in radians (default 0.0).
    :type right_ascension: float
    :param argument_of_periapsis: The argument of periapsis in radians (default 0.0).
    :type argument_of_periapsis: float
    :param true_anomaly: The true anomaly in radians (default 0.0).
    :type true_anomaly: float
    :param planet: The name of the planet being orbited (default "earth").
    :type planet: str
    :return: A tuple containing position and velocity as JSON-formatted strings.
    :rtype: Tuple[str, str]

    .. note:: The function assumes that the orbiting body is Earth unless otherwise specified.
    """
    # Define a small numerical value
    EPS: float = 1e-12

    # Store local values from the input in the correct form
    a: float = semi_major_axis * 1000.0
    e: float = eccentricity
    i: float = inclination
    an: float = right_ascension
    ap: float = argument_of_periapsis
    f: float = true_anomaly
    mu: float = get_planet_mu(planet)

    # Keep track of the new variables for the vector
    p: float = 0.0              # the parameter or the semi-latus rectum
    theta: float = 0.0          # true latitude theta = omega + f
    h: float = 0.0              # orbit angular momentum magnitude
    r: float = 0.0
    v: float = 0.0
    ir: list = [0.0, 0.0, 0.0]
    rVec: list = [0.0, 0.0, 0.0]
    vVec: list = [0.0, 0.0, 0.0]

    # 1D rectilinear elliptic/hyperbolic orbit case
    if abs(e - 1.0) < EPS and abs(a) > EPS:
        angle: float = f
        if a > 0.0:
            r = a * (1 - e * math.cos(angle))
        else:
            r = a * (1 - e * math.cosh(angle))

        v = math.sqrt(2 * mu / r - mu / a);
        ir[0] = math.cos(an) * math.cos(ap) - math.sin(an) * math.sin(ap) * math.cos(i);
        ir[1] = math.sin(an) * math.cos(ap) + math.cos(an) * math.sin(ap) * math.cos(i);
        ir[2] = math.sin(ap) * math.sin(i);
        rVec[0] = ir[0] * r
        rVec[1] = ir[1] * r
        rVec[2] = ir[2] * r

        if math.sin(angle) > 0:
            vVec[0] = ir[0] * v
            vVec[1] = ir[1] * v
            vVec[2] = ir[2] * v
        else:
            vVec[0] = ir[0] * -v
            vVec[1] = ir[1] * -v
            vVec[2] = ir[2] * -v

    # General 2D orbit case
    else:
        # calculate the semi-latus rectum
        if abs(a) > EPS:
            p = a * (1 - e * e)             # elliptic or hyperbolic 
        else:
            # TODO: e for a parabolic orbit is 1 and math.cos(0) is always 1. Therefore, this version of p breaks down
            #   to be identical to the version above 2 * a * (1 - e * e) / 2 == a * (1 - e * e)
            p = 2 * a * (1 - e * e) / (1 + e * math.cos(0))  # parabolic 

        r = p / (1 + e * math.cos(f))      # orbit radius
        theta = ap + f                     # true latitude angle
        h = math.sqrt(mu * p)              # orbit ang. momentum mag.

        rVec[0] = r * (math.cos(an) * math.cos(theta) - math.sin(an) * math.sin(theta) * math.cos(i))
        rVec[1] = r * (math.sin(an) * math.cos(theta) + math.cos(an) * math.sin(theta) * math.cos(i))
        rVec[2] = r * (math.sin(theta) * math.sin(i))

        vVec[0] = -mu / h * (math.cos(an) * (math.sin(theta) + e * math.sin(ap)) + math.sin(an) * (math.cos(theta) + e * math.cos(ap)) * math.cos(i))
        vVec[1] = -mu / h * (math.sin(an) * (math.sin(theta) + e * math.sin(ap)) - math.cos(an) * (math.cos(theta) + e * math.cos(ap)) * math.cos(i))
        vVec[2] = -mu / h * (-(math.cos(theta) + e * math.cos(ap)) * math.sin(i))

    # Ensure the velocity is never NaN
    if math.isnan(rVec[0]) or math.isnan(rVec[1]) or math.isnan(rVec[2]):
        rVec = [0.0, 0.0, 0.0]
    if math.isnan(vVec[0]) or math.isnan(vVec[1]) or math.isnan(vVec[2]):
        vVec = [0.0, 0.0, 0.0]

    # Return the new elements
    position: str = value.vector3(rVec[0], rVec[1], rVec[2])
    velocity: str = value.vector3(vVec[0], vVec[1], vVec[2])
    return position, velocity


def classical_to_vector_elements(semi_major_axis: float, eccentricity: float = 0.0,
    inclination: float = 0.0, right_ascension: float = 0.0, argument_of_periapsis: float = 0.0,
    true_anomaly: float = 0.0, planet: str = "earth") -> tuple:
    """
    Converts classical Keplerian elements to state vector (position and velocity).

    This function calculates the state vector from a set of classical
    Keplerian elements. The semi-major axis should be in kilometers, eccentricity
    should be between 0 and 1, and the angular elements (inclination, right ascension,
    argument of periapsis, and true anomaly) should be in degrees. The function
    returns the position and velocity in meters and meters per second, respectively,
    formatted as JSON strings.

    :param semi_major_axis: The semi-major axis in kilometers.
    :type semi_major_axis: float
    :param eccentricity: The orbital eccentricity (default 0.0).
    :type eccentricity: float
    :param inclination: The inclination in degrees (default 0.0).
    :type inclination: float
    :param right_ascension: The right ascension in degrees (default 0.0).
    :type right_ascension: float
    :param argument_of_periapsis: The argument of periapsis in degrees (default 0.0).
    :type argument_of_periapsis: float
    :param true_anomaly: The true anomaly in degrees (default 0.0).
    :type true_anomaly: float
    :param planet: The name of the planet being orbited (default "earth").
    :type planet: str
    :return: A tuple containing position and velocity as JSON-formatted strings.
    :rtype: Tuple[str, str]

    .. note:: The function assumes that the orbiting body is Earth unless otherwise specified.
    """
    return classical_to_vector_elements_rad(
        semi_major_axis=semi_major_axis,
        eccentricity=eccentricity,
        inclination=inclination * constants.D2R,
        argument_of_periapsis=argument_of_periapsis * constants.D2R,
        right_ascension=right_ascension * constants.D2R,
        true_anomaly=true_anomaly * constants.D2R,
        planet=planet
    )
