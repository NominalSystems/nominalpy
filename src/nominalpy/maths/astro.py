#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

"""
This module contains public methods that can calculate various
astrophysical parameters. These include fetching planetary gravity
or return the position and velocity from an orbit.
"""

import numpy as np
from typing import Tuple
from . import constants
from . import value
from . import utils
from ..utils import NominalException


def get_planet_property (planet: str, property: str) -> float:
    """
    Returns the planet's property. If the planet does not exist,
    then an exception will be thrown.

    :param planet:      The name of the planet to fetch the property from
    :type planet:       str
    :param property:    The name of the property to fetch
    :type property:     str

    :return:            The value of the property
    :rtype:             float
    """
    param = f"{planet.upper()}_{property.upper()}"
    if hasattr(constants, param):
        return float(getattr(constants, param))

    # Throw an error if this occurs
    else:
        raise NominalException(f"No planet: {planet} with property {property}.")


def get_planet_mu (planet: str) -> float:
    """
    Returns the planet's gravitational mu parameter, equal to GM of the
    planet's body in units of [m^3/s^2]. If the planet does not exist,
    then an exception will be thrown.

    :param planet:  The name of the planet to fetch the MU from
    :type planet:   str

    :returns:       The gravitational MU parameter
    :rtype:         float
    """
    return get_planet_property(planet, "MU")


def t_perifocal_to_vector_elements (
    right_ascension: float = 0,
    argument_of_periapsis: float = 0,
    inclination: float = 0
)-> np.ndarray:
    """
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


def perifocal_to_vector_elements(
    r_bp_p: np.ndarray,
    v_bp_p: np.ndarray,
    right_ascension: float = 0,
    inclination: float = 0,
    argument_of_periapsis: float = 0,
) -> tuple:
    """
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
    """
    # ensure that the input arrays are of type float
    r_bp_p = r_bp_p.astype(np.float64)
    v_bp_p = v_bp_p.astype(np.float64)
    # calculate the transformation matrix
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
    """
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
    ], dtype=np.float64)
    rat = np.sqrt(mu / semi_latus_rectum)
    v_bp_p = np.array([
        -rat * np.sin(true_anomaly),
        rat * (eccentricity + np.cos(true_anomaly)),
        0
    ], dtype=np.float64)
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
    """
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

    :returns:
    :rtype:
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
    """
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
    """

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
    """
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
    """
    # ensure that the input arrays are of type float
    r_bn_n = r_bn_n.astype(np.float64)
    v_bn_n = v_bn_n.astype(np.float64)

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
    if np.fabs(node) <= 1e-10:
        if np.fabs(eccentricity) <= 1e-10:
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
    elif np.fabs(eccentricity) <= 1e-10:
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


def pcpf_to_geodetic_lla (position: np.ndarray, planet="Earth") -> np.ndarray:
    """
    Converts the Planet-Centred, Planet-Fixed parameters to Latitude, 
    Longitude, and Altitude using NumPy.

    :param position:    The current ECPF position as a NumPy array or list (X, Y, Z)
    :type position:     np.ndarray
    :param planet:      The planet to use for the conversion
    :type planet:       str

    :return:            Tuple containing Latitude [rad], Longitude [rad], and Altitude [m]
    :rtype:             np.ndarray
    """
    # ensure that the input array is of type float
    position = position.astype(np.float64)
    # handle the edge case where the position is zero
    if np.linalg.norm(position) == 0:
        return np.array([0, 0, 0], dtype=np.float64)
    # make sure that the position is of type float
    position = position.astype(dtype=np.float64)
    # WGS Parameters
    a: float = get_planet_property(planet=planet, property="REQ")  # Equatorial radius of the planet
    f: float = get_planet_property(planet=planet, property="FLATTENING")  # Flattening factor of the planet
    e: float = np.sqrt(2 * f - f ** 2)

    longitude: float = np.arctan2(position[1], position[0])
    P: float = np.sqrt(position[0] ** 2 + position[1] ** 2)

    # Initial calculations for latitude and altitude
    altitude: float = 0
    latitude: float = np.arctan2(position[2], P * (1 - e ** 2))
    N: float = a / np.sqrt(1 - (e * np.sin(latitude)) ** 2)
    delta_h: float = 1000000
    prevH: float = 0
    iterations: int = 0

    # Iterative calculations for latitude and altitude
    while delta_h > 0.01 and iterations < 10:
        prevH = altitude
        latitude = np.arctan2(position[2], P * (1 - e ** 2 * (N / (N + altitude))))
        if np.isnan(latitude):
            raise ValueError("Latitude is NaN")
        N = a / np.sqrt(1 - (e * np.sin(latitude)) ** 2)
        # handle the case when the cos(latitude) is zero (within floating point error) to avoid a divide by zero error
        if np.cos(latitude) < 1e-10:
            altitude = np.fabs(position[2]) - a * (1 - f)
        else:
            altitude = P / np.cos(latitude) - N
        delta_h = np.abs(altitude - prevH)
        iterations += 1

    return np.array([latitude, longitude, altitude], dtype=np.float64)


def pcpf_to_geodetic_lla_deg (position: np.ndarray, planet="Earth") -> np.ndarray:
    """
    Converts the Planet-Centred, Planet-Fixed parameters to Latitude, 
    Longitude, and Altitude using NumPy.

    :param position:    The current ECPF position as a NumPy array or list (X, Y, Z)
    :type position:     np.ndarray
    :param planet:      The planet to use for the conversion
    :type planet:       str

    :return:            Tuple containing Latitude [deg], Longitude [deg], and Altitude [m]
    :rtype:             np.ndarray
    """
    lla = pcpf_to_geodetic_lla(position, planet=planet)
    return np.array([np.degrees(lla[0]), np.degrees(lla[1]), lla[2]], dtype=np.float64)


def geodetic_lla_to_pcpf (lla: np.ndarray, planet="Earth") -> np.ndarray:
    """
    Converts from Latitude/Longitude/Altitude (LLA) coordinates to Planet-Centered,
    Planet-Fixed (PCPF) coordinates given a planet radius.

    :param lla:     A tuple or list containing Latitude (radians), Longitude (radians), and Altitude (meters) coordinates.
    :type lla:      np.ndarray
    :param planet:  The planet to use for the conversion
    :type planet:   str

    :return:        A tuple representing the final position in the PCPF frame in meters.
    :rtype:         np.ndarray
    """
    # ensure that the input array is of type float
    lla = lla.astype(np.float64)
    # Convert latitude and longitude from degrees to radians
    lat: float = lla[0]  # Latitude in radians
    lon: float = lla[1]  # Longitude in radians
    alt: float = lla[2]  # Altitude in meters
    planet_radius: float = get_planet_property(planet=planet, property="REQ")
    f: float = get_planet_property(planet=planet, property="FLATTENING")  # Flattening factor
    e_sq: float = f * (2 - f)  # Square of eccentricity

    # Calculate the radius of curvature in the prime vertical
    N: float = planet_radius / np.sqrt(1 - e_sq * np.sin(lat) ** 2)

    # Calculate PCPF coordinates
    X: float = (N + alt) * np.cos(lat) * np.cos(lon)
    Y: float = (N + alt) * np.cos(lat) * np.sin(lon)
    Z: float = ((1 - e_sq) * N + alt) * np.sin(lat)

    return np.array([X, Y, Z], dtype=np.float64)


def geodetic_lla_to_pcpf_deg (lla: np.ndarray, planet="Earth") -> np.ndarray:
    """
    Converts from Latitude/Longitude/Altitude (LLA) coordinates to Planet-Centered,
    Planet-Fixed (PCPF) coordinates given a planet radius.

    :param lla:     A tuple or list containing Latitude (degrees), Longitude (degrees), and Altitude (meters) coordinates.
    :type lla: n    p.ndarray
    :param planet:  The planet to use for the conversion
    :type planet:   str

    :return:        A tuple representing the final position in the PCPF frame in meters.
    :rtype:         np.ndarray
    """

    # Convert latitude and longitude from degrees to radians
    lat: float = np.radians(lla[0])  # Latitude in radians
    lon: float = np.radians(lla[1])  # Longitude in radians
    return geodetic_lla_to_pcpf(np.array([lat, lon, lla[2]], dtype=np.float64), planet=planet)


def calculate_orbital_velocity(r_bn_n_mag: float, semi_major_axis: float, gm: float = constants.EARTH_MU) -> float:
    """
    Calculate the magnitude of the orbital velocity for a spacecraft in any orbit type.

    This function uses the vis-viva equation to compute the orbital speed of a spacecraft at a given distance from the
        Earth's center, considering its semi-major axis. It ensures that the provided parameters are within physically
        meaningful ranges.

    :param r_bn_n_mag:  The distance from the Earth's center to the spacecraft - m.
    :type r_bn_n_mag:   float
    :param semi_major_axis:         The semi-major axis of the spacecraft's orbit. It must be a non-negative value - m
    :type semi_major_axis:          float
    :param gm:          The gravitational parameter, defaulting to Earth's gravitational parameter if not provided - m^3/s^2.
    :type gm:           float

    :return:            The magnitude of the spacecraft's orbital velocity - m/s.
    :rtype: float

    :raises TypeError:  If `r` or `semi_major_axis` is not a numeric type.
    :raises ValueError: If `r` is less than zero, or `semi_major_axis` is negative, or the radicand in the calculation is negative.

    Example:
        >>> calculate_orbital_velocity(7000, 10000)
        7.546049108166282
    """
    if r_bn_n_mag <= 0:
        raise ValueError(f"The input distance from Earth's center (r: {r_bn_n_mag} km) is not valid.")
    if semi_major_axis < 0:
        raise ValueError(f"The input semi-major axis (semi_major_axis: {semi_major_axis} km) is not valid.")
    # sanity check the input parameters
    radicand = 2 * gm * (1 / r_bn_n_mag - 1 / (2 * semi_major_axis))
    if radicand < 0:
        raise ValueError(f"The radicand ({radicand}) is not greater than zero, leading to a singularity.")
    # calculate the orbital velocity
    return np.sqrt(radicand)


def calculate_circular_orbit_velocity(semi_major_axis: float, gm=constants.EARTH_MU) -> float:
    """
    Calculates the magnitude of the orbital velocity for a spacecraft in 
    a circular orbit.

    :param semi_major_axis: The semi-major axis of the spacecraft's orbit. It must be a non-negative value - m
    :type semi_major_axis:  float
    :param gm:  The gravitational parameter, defaulting to Earth's gravitational parameter if not provided - m^3/s^2.
    :type gm:   float
    
    :return:    The magnitude of the spacecraft's orbital velocity resulting in a circular orbit - m/s.
    :rtype:     float
    """
    return calculate_orbital_velocity(r_bn_n_mag=semi_major_axis, semi_major_axis=semi_major_axis, gm=gm)


def mean_to_eccentric_anomaly(mean_anomaly: float, eccentricity: float) -> float:
    """
    Converts the Mean Anomaly to the Eccentric Anomaly.

    :param mean_anomaly:    [rad] The Mean Anomaly
    :type mean_anomaly:     float
    :param eccentricity:    [-] The eccentricity of the orbit (0 <= e < 1)
    :type eccentricity:     float

    :return:                [rad] The Eccentric Anomaly
    :rtype:                 float
    """
    # ensure that the input parameters are within physically meaningful ranges
    mean_anomaly = utils.normalize_angle(mean_anomaly)
    if eccentricity == 0:
        # if the eccentricity is zero, then the eccentric anomaly is equal to the mean anomaly
        # return this to avoid a singularity in ratio
        return mean_anomaly
    # define the initial guess for the eccentric anomaly
    eccentric_anomaly = mean_anomaly + eccentricity / 2 if mean_anomaly < np.pi else mean_anomaly - eccentricity / 2
    # calculate the eccentric anomaly
    ratio = 1.0
    while np.fabs(ratio) > 1e-10 / 100.0:
        ratio = (eccentric_anomaly - eccentricity * np.sin(eccentric_anomaly) - mean_anomaly) / (1 - eccentricity * np.cos(eccentric_anomaly))
        eccentric_anomaly = eccentric_anomaly - ratio
    return utils.normalize_angle(eccentric_anomaly)


def eccentric_to_true_anomaly(eccentric_anomaly: float, eccentricity: float) -> float:
    """
    Converts the Eccentric Anomaly to the True Anomaly.

    :param eccentric_anomaly:   [rad] The Eccentric Anomaly
    :type eccentric_anomaly:    float
    :param eccentricity:        [-] The eccentricity of the orbit (0 <= e < 1)
    :type eccentricity:         float

    :return:                    [rad] The True Anomaly
    :rtype:                     float
    """
    # ensure that the input parameters are within physically meaningful ranges
    eccentric_anomaly = utils.normalize_angle(eccentric_anomaly)
    # for EA > pi, TA will pi < TA < EA. But we need to take the corresponding angle
    test = -1 if eccentric_anomaly > np.pi else 1
    return utils.acos_quadrant_check(
        np.cos(eccentric_anomaly) - eccentricity,
        1 - eccentricity * np.cos(eccentric_anomaly),
        test
    )


def true_to_eccentric_anomaly(true_anomaly: float, eccentricity: float) -> float:
    """
    Maps true anomaly angles into eccentric anomaly angles.
    :param true_anomaly:   [rad] True anomaly angle
    :type true_anomaly:    float
    :param eccentricity:  [-] Eccentricity (0 <= e < 1)
    :type eccentricity:   float
    :return:             [rad] Eccentric anomaly
    :rtype:              float
    """
    return utils.normalize_angle(
        np.arctan2(
            np.sin(true_anomaly) * np.sqrt(1 - eccentricity**2),
            eccentricity + np.cos(true_anomaly)
        )
    )


def eccentric_to_mean_anomaly(eccentric_anomaly: float, eccentricity: float) -> float:
    """
    Maps the eccentric anomaly angle into the corresponding mean elliptic anomaly angle. Both 2D and 1D elliptic

    :param eccentric_anomaly:  [rad] Eccentric anomaly
    :type eccentric_anomaly:   float
    :param eccentricity: [-] Eccentricity (0 <= e < 1)
    :type eccentricity: float
    :return: [rad] Mean elliptic anomaly
    :rtype: float
    """
    return utils.normalize_angle(eccentric_anomaly - eccentricity * np.sin(eccentric_anomaly))


def true_to_mean_anomaly(true_anomaly: float, eccentricity: float) -> float:
    """
    Calculate the mean anomaly from the true anomaly.

    :param true_anomaly:    [rad] The true anomaly of the orbit
    :type true_anomaly:     float
    :param eccentricity:    [-] The eccentricity of the orbit (0 <= e < 1)
    :type eccentricity:     float
    :return:                [rad] Mean elliptic anomaly
    :rtype:                 float
    """
    return eccentric_to_mean_anomaly(true_to_eccentric_anomaly(true_anomaly, eccentricity), eccentricity)


def mean_to_true_anomaly(mean_anomaly: float, eccentricity: float) -> float:
    """
    Calculate the true anomaly from the mean anomaly.

    :param mean_anomaly:    [rad] The mean anomaly of the orbit
    :type mean_anomaly:     float
    :param eccentricity:    [-] The eccentricity of the orbit (0 <= e < 1)
    :type eccentricity:     float
    :return:                [rad] The true anomaly of the orbit
    :rtype:                 float
    """
    return eccentric_to_true_anomaly(
        mean_to_eccentric_anomaly(
            mean_anomaly,
            eccentricity
        ),
        eccentricity
    )


def mean_to_osculating_elements(
    req: float,
    j2: float,
    semi_major_axis: float,
    eccentricity: float,
    inclination: float,
    right_ascension: float,
    argument_of_periapsis: float,
    true_anomaly: float,
    mean_to_osculating: bool
) -> Tuple[float, float, float, float, float, float]:
    """
    First-order J2 Mapping Between Mean and Osculating Orbital Elements
    Analytical Mechanics of Space Systems, Hanspeter Schaub, John L. Junkins, 4th edition.
    [m] or [km] should be the same both for req and elements.

    :param req:                 [m] Equatorial radius or the orbital body
    :type req:                  float
    :param j2:                  [-] J2 parameter for the orbital body of interest
    :type j2:                   float
    :param semi_major_axis:     [m] Semi-major axis of the orbit
    :type semi_major_axis:      float
    :param eccentricity:        [-] Eccentricity of the orbit
    :type eccentricity:         float
    :param inclination:         [rad] Inclination of the orbit
    :type inclination:          float
    :param right_ascension:     [rad] Right ascension of the ascending node of the orbit
    :type right_ascension:      float
    :param argument_of_periapsis:   [rad] Argument of periapsis of the orbit
    :type argument_of_periapsis:    float
    :param true_anomaly:        [rad] True anomaly of the orbit
    :type true_anomaly:         float
    :param mean_to_osculating:  [-] Sgn=True:mean to osc, Sgn=False:osc to mean
    :type mean_to_osculating:   bool
    :return:                    [-] A classical element struct
                                    (
                                        semi_major_axis,
                                        eccentricity,
                                        inclination,
                                        raan,
                                        argument_of_periapsis,
                                        true_anomaly
                                    )
    :rtype:                     tuple
    """
    # ensure that the J2 parameter is positive
    j2 = np.abs(j2)
    # define the sign of the gamma2 parameter to dictate conversion from mean to osculating or vice versa
    sgn = 1 if mean_to_osculating else -1
    # unpack the orbital elements
    a = semi_major_axis
    e = eccentricity
    i = inclination
    Omega = right_ascension
    omega = argument_of_periapsis
    f = true_anomaly
    # calculate the mean anomaly
    E = true_to_eccentric_anomaly(f, e)
    M = eccentric_to_mean_anomaly(E, e)
    # calculate the gamma2 parameter
    gamma2 = sgn * j2 / 2 * (req / a) ** 2
    eta = np.sqrt(1 - e ** 2)
    eta2 = eta ** 2
    eta3 = eta ** 3
    eta4 = eta ** 4
    eta6 = eta ** 6
    gamma2p = gamma2 / eta4
    a_r = (1 + e * np.cos(f)) / eta2
    cos_i = np.cos(i)
    cos_i2 = cos_i ** 2
    cos_i4 = cos_i ** 4
    cos_i6 = cos_i ** 6
    cos_f = np.cos(f)
    # calculate the osculating semi-major axis
    ap = a + a * gamma2 * (
        (3 * cos_i2 - 1) * (a_r ** 3 - 1 / eta3) +
        3 * (1 - cos_i2) * (a_r ** 3) * np.cos(2 * omega + 2 * f)
    )
    # calculate the osculating eccentricity
    de1 = gamma2p / 8 * e * eta2 * (
        1 - 11 * cos_i2 - 40 * cos_i2 ** 2 / (1 - 5 * cos_i2)
    ) * np.cos(2 * omega)
    de = de1 + eta2 / 2 * (
        gamma2 * ((3 * cos_i2 - 1) / eta6
                  * (e * eta + e / (1 + eta) + 3 * cos_f + 3 * e * cos_f ** 2 + e ** 2
                     * cos_f ** 3) + 3 * (1 - cos_i2) / eta6
                  * (e + 3 * cos_f + 3 * e * cos_f ** 2 + e ** 2 * cos_f ** 3) *
                  np.cos(2 * omega + 2 * f))
        - gamma2p * (1 - cos_i2) *
        (3 * np.cos(2 * omega + f) + np.cos(2 * omega + 3 * f))
    )
    # calculate the osculating inclination
    di = -e * de1 / eta2 / np.tan(i) + gamma2p / 2 * cos_i * np.sqrt(1 - cos_i2) * (
        3 * np.cos(2 * omega + 2 * f) + 3 * e * np.cos(2 * omega + f) +
        e * np.cos(2 * omega + 3 * f))
    # calculate the osculating mean anomaly
    m_pop_op = M + omega + Omega + gamma2p / 8.0 * eta3 * (1 - 11 * cos_i2
                                                           - 40 * cos_i4 / (1 - 5 * cos_i2)) * np.sin(2 * omega) \
              - gamma2p / 16.0 * (2 + e ** 2 - 11 * (2 + 3 * e ** 2) * cos_i2 - 40 * (2 + 5 * e ** 2)
                                  * cos_i4 / (1 - 5 * cos_i2) - 400 * e ** 2 * cos_i6
                                  / ((1 - 5 * cos_i2) * (1 - 5 * cos_i2))) * np.sin(2 * omega) \
              + gamma2p / 4.0 * (-6 * (1 - 5 * cos_i2) * (f - M + e * np.sin(f)) + (3 - 5 * cos_i2)
                                 * (3 * np.sin(2 * omega + 2 * f) + 3 * e * np.sin(2 * omega + f) + e * np.sin(2 * omega + 3 * f))) \
              - gamma2p / 8 * e ** 2 * cos_i * (11 + 80 * cos_i2 / (1 - 5 * cos_i2)
                                                + 200 * cos_i4 / ((1 - 5 * cos_i2) * (1 - 5 * cos_i2))) * np.sin(2 * omega) \
              - gamma2p / 2.0 * cos_i * (6 * (f - M + e * np.sin(f)) - 3 * np.sin(2 * omega + 2 * f)
                                         - 3 * e * np.sin(2 * omega + f) - e * np.sin(2 * omega + 3 * f))
    # calculate the osculating eccentricity mean anomaly
    ed_m = gamma2p / 8.0 * e * eta3 * (1 - 11 * cos_i2 - 40 * cos_i4
                                        / (1 - 5 * cos_i2)) * np.sin(2 * omega) \
           - gamma2p / 4.0 * eta3 * (2 * (3 * cos_i2 - 1)
                                     * ((a_r * eta) * (a_r * eta) + a_r + 1) * np.sin(f) +
                                     3 * (1 - cos_i2) * ((-(a_r * eta) * (a_r * eta) - a_r + 1)
                                                         * np.sin(2 * omega + f) + ((a_r * eta) * (a_r * eta) + a_r + 1 / 3.0) * np.sin(2 * omega + 3 * f)))
    # calculate the osculating right ascension of the ascending node
    d_omega = -gamma2p / 8.0 * e ** 2 * cos_i * (11 + 80 * cos_i2 / (1 - 5 * cos_i2)
                                                 + 200 * cos_i4 / ((1 - 5 * cos_i2) * (1 - 5 * cos_i2))) * np.sin(2 * omega) \
              - gamma2p / 2.0 * cos_i * (6 * (f - M + e * np.sin(f)) - 3 * np.sin(2 * omega + 2 * f)
                                         - 3 * e * np.sin(2 * omega + f) - e * np.sin(2 * omega + 3 * f))
    # calculate the osculating mean anomaly
    d1 = (e + de) * np.sin(M) + ed_m * np.cos(M)
    d2 = (e + de) * np.cos(M) - ed_m * np.sin(M)
    m_p = np.arctan2(d1, d2)
    e_p = np.sqrt(d1 ** 2 + d2 ** 2)
    # calculate the osculating right ascension of the ascending node
    d3 = (np.sin(i / 2.0) + np.cos(i / 2.0) * di / 2.0) * np.sin(Omega) + \
         np.sin(i / 2.0) * d_omega * np.cos(Omega)
    d4 = (np.sin(i / 2.0) + np.cos(i / 2.0) * di / 2.0) * np.cos(Omega) - \
            np.sin(i / 2.0) * d_omega * np.sin(Omega)
    Omega_p = np.arctan2(d3, d4)
    d_34 = np.sqrt(d3 ** 2 + d4 ** 2)
    d_34 = -1 if d_34 < -1 else d_34
    d_34 = 1 if d_34 > 1 else d_34
    i_p = 2 * np.arcsin(d_34)
    omega_p = m_pop_op - m_p - Omega_p
    E_p = mean_to_eccentric_anomaly(m_p, e_p)
    f_p = eccentric_to_true_anomaly(E_p, e_p)
    return ap, e_p, i_p, Omega_p, omega_p, f_p


def vector_to_classical_elements_mean(
        r_bn_n: np.ndarray,
        v_bn_n: np.ndarray,
        planet: str = "earth"
) -> Tuple[float, float, float, float, float, float]:
    """
    Converts the position and velocity vectors into mean classical orbital elements.

    :param r_bn_n:      The position vector in the inertial frame [m]
    :type r_bn_n:       np.ndarray
    :param v_bn_n:      The velocity vector in the inertial frame [m/s]
    :type v_bn_n:       np.ndarray
    :param planet:      The planet to use for the conversion
    :type planet:       str

    :return:            A tuple containing the classical orbital elements
                            (
                                mean semi_major_axis,
                                mean eccentricity,
                                mean inclination,
                                mean right_ascension,
                                mean argument_of_periapsis,
                                mean true_anomaly
                            )
    :rtype:             tuple
    """
    # calculate the osculating orbital elements
    sma_osc, ecc_osc, inc_osc, raan_osc, aop_osc, ta_osc = vector_to_classical_elements(
        r_bn_n=r_bn_n,
        v_bn_n=v_bn_n,
        planet=planet
    )
    # convert the osculating orbital elements to mean orbital elements
    sma_mean, ecc_mean, inc_mean, raan_mean, aop_mean, ta_mean = mean_to_osculating_elements(
        req=get_planet_property(planet=planet, property="REQ"),
        j2=get_planet_property(planet=planet, property="J2"),
        semi_major_axis=sma_osc,
        eccentricity=ecc_osc,
        inclination=inc_osc,
        right_ascension=raan_osc,
        argument_of_periapsis=aop_osc,
        true_anomaly=ta_osc,
        mean_to_osculating=False
    )
    return sma_mean, ecc_mean, inc_mean, raan_mean, aop_mean, ta_mean


def classical_to_non_singular_elements(
        semi_major_axis: float,
        eccentricity: float,
        inclination: float,
        right_ascension: float,
        argument_of_periapsis: float,
        true_anomaly: float
) -> Tuple[float, float, float, float, float, float]:
    """
    convert classical orbital elements to non-singular orbital elements as defined in the PhD Thesis:
    D’Amico, S. (2010). Autonomous Formation Flying in Low Earth Orbit [Delft University of Technology].
    http://www.narcis.nl/publication/RecordID/oai:tudelft.nl:uuid:a10e2d63-399d-48e5-884b-402e9a105c70, Page 21

    This set of non-singular orbital elements are often used to parameterize the relative motion between two spacecraft

    :param semi_major_axis:        Semi-major axis of the orbit in meters
    :type semi_major_axis:         float
    :param eccentricity:          Eccentricity of the orbit
    :type eccentricity:           float
    :param inclination:          Inclination of the orbit in radians
    :type inclination:           float
    :param right_ascension:     Right ascension of the ascending node in radians
    :type right_ascension:      float
    :param argument_of_periapsis: Argument of periapsis in radians
    :type argument_of_periapsis:  float
    :param true_anomaly:        True anomaly at the epoch in radians
    :type true_anomaly:         float
    :return:                   A tuple containing the non-singular orbital elements
                                    (
                                        semi_major_axis,
                                        e_x: x component of eccentricity,
                                        e_y: y component of eccentricity
                                        inclination,
                                        right_ascension,
                                        mean argument of latitude
                                    )
    :rtype:                    tuple
    """
    return (
        semi_major_axis,
        eccentricity * np.cos(argument_of_periapsis),  # x component of eccentricity
        eccentricity * np.sin(argument_of_periapsis),  # y component of eccentricity
        inclination,
        right_ascension,
        utils.normalize_angle(
            argument_of_periapsis + true_to_mean_anomaly(
                true_anomaly,
                eccentricity)
        )
    )


def non_singular_to_relative_elements(
        semi_major_axis_leader: float,
        e_x_leader: float,
        e_y_leader: float,
        inclination_leader: float,
        right_ascension_leader: float,
        mean_argument_of_latitude_leader: float,
        semi_major_axis_follower: float,
        e_x_follower: float,
        e_y_follower: float,
        inclination_follower: float,
        right_ascension_follower: float,
        mean_argument_of_latitude_follower: float,
) -> Tuple[float, float, float, float, float, float]:
    """
    Convert non-singular orbital elements to relative orbital elements as defined in the PhD Thesis:
    D’Amico, S. (2010). Autonomous Formation Flying in Low Earth Orbit [Delft University of Technology].
    http://www.narcis.nl/publication/RecordID/oai:tudelft.nl:uuid:a10e2d63-399d-48e5-884b-402e9a105c70, Page 21

    :param semi_major_axis_leader: Semi-major axis of the leader's orbit in meters
    :type semi_major_axis_leader: float
    :param e_x_leader: x component of the leader's eccentricity
    :type e_x_leader: float
    :param e_y_leader: y component of the leader's eccentricity
    :type e_y_leader: float
    :param inclination_leader: Inclination of the leader's orbit in radians
    :type inclination_leader: float
    :param right_ascension_leader: Right ascension of the ascending node of the leader's orbit in radians
    :type right_ascension_leader: float
    :param mean_argument_of_latitude_leader: Mean argument of latitude of the leader's orbit in radians
    :type mean_argument_of_latitude_leader: float
    :param semi_major_axis_follower: Semi-major axis of the follower's orbit in meters
    :type semi_major_axis_follower: float
    :param e_x_follower: x component of the follower's eccentricity
    :type e_x_follower: float
    :param e_y_follower: y component of the follower's eccentricity
    :type e_y_follower: float
    :param inclination_follower: Inclination of the follower's orbit in radians
    :type inclination_follower: float
    :param right_ascension_follower: Right ascension of the ascending node of the follower's orbit in radians
    :type right_ascension_follower: float
    :param mean_argument_of_latitude_follower: Mean argument of latitude of the follower's orbit in radians
    :type mean_argument_of_latitude_follower: float
    :return: A tuple containing the relative orbital elements
                (
                    da: the relative semi-major axis [m]
                    dex: relative e_x [m]
                    dix: relative x component of inclination [m]
                    diy: relative y component of inclination [m]
                    dey: relative e_y [m]
                    daoml: change in mean argument of latitude [m]
                )
    :rtype: tuple
    """
    da = semi_major_axis_follower - semi_major_axis_leader  # [m]
    d_raan = utils.shortest_angular_difference(right_ascension_follower, right_ascension_leader)  # [rad]
    dex = (e_x_follower - e_x_leader) * semi_major_axis_leader  # [m]
    dix = utils.shortest_angular_difference(inclination_follower, inclination_leader) * semi_major_axis_leader  # [m]
    diy = d_raan * np.sin(inclination_leader) * semi_major_axis_leader  # [m]
    dey = (e_y_follower - e_y_leader) * semi_major_axis_leader  # [m]
    daoml = (utils.shortest_angular_difference(
        mean_argument_of_latitude_follower,
        mean_argument_of_latitude_leader
    ) + d_raan * np.cos(inclination_leader)) * semi_major_axis_leader  # [m]
    return da, dex, dix, diy, dey, daoml


def classical_to_relative_elements(
        semi_major_axis_leader: float,
        eccentricity_leader: float,
        inclination_leader: float,
        right_ascension_leader: float,
        argument_of_periapsis_leader: float,
        true_anomaly_leader: float,
        semi_major_axis_follower: float,
        eccentricity_follower: float,
        inclination_follower: float,
        right_ascension_follower: float,
        argument_of_periapsis_follower: float,
        true_anomaly_follower: float
) -> Tuple[float, float, float, float, float, float]:
    """
    Convert classical orbital elements to relative orbital elements as defined in the PhD Thesis:
    D’Amico, S. (2010). Autonomous Formation Flying in Low Earth Orbit [Delft University of Technology].
    http://www.narcis.nl/publication/RecordID/oai:tudelft.nl:uuid:a10e2d63-399d-48e5-884b-402e9a105c70, Page 21

    :param semi_major_axis_leader: Semi-major axis of the leader's orbit in meters
    :type semi_major_axis_leader: float
    :param eccentricity_leader: Eccentricity of the leader's orbit
    :type eccentricity_leader: float
    :param inclination_leader: Inclination of the leader's orbit in radians
    :type inclination_leader: float
    :param right_ascension_leader: Right ascension of the ascending node of the leader's orbit in radians
    :type right_ascension_leader: float
    :param argument_of_periapsis_leader: Argument of periapsis of the leader's orbit in radians
    :type argument_of_periapsis_leader: float
    :param true_anomaly_leader: True anomaly of the leader's orbit in radians
    :type true_anomaly_leader: float
    :param semi_major_axis_follower: Semi-major axis of the follower's orbit in meters
    :type semi_major_axis_follower: float
    :param eccentricity_follower: Eccentricity of the follower's orbit
    :type eccentricity_follower: float
    :param inclination_follower: Inclination of the follower's orbit in radians
    :type inclination_follower: float
    :param right_ascension_follower: Right ascension of the ascending node of the follower's orbit in radians
    :type right_ascension_follower: float
    :param argument_of_periapsis_follower: Argument of periapsis of the follower's orbit in radians
    :type argument_of_periapsis_follower: float
    :param true_anomaly_follower: True anomaly of the follower's orbit in radians
    :type true_anomaly_follower: float
    :return: A tuple containing the relative orbital elements
                (
                    da: the relative semi-major axis [m]
                    dex: relative e_x [m]
                    dix: relative x component of inclination [m]
                    diy: relative y component of inclination [m]
                    dey: relative e_y [m]
                    daoml: change in mean argument of latitude [m]
                )
    :rtype: tuple
"""
    # convert the classical orbital elements to non-singular orbital elements
    (
        semi_major_axis_leader,
        e_x_leader,
        e_y_leader,
        inclination_leader,
        right_ascension_leader,
        mean_argument_of_latitude_leader
    ) = classical_to_non_singular_elements(
        semi_major_axis_leader,
        eccentricity_leader,
        inclination_leader,
        right_ascension_leader,
        argument_of_periapsis_leader,
        true_anomaly_leader
    )
    (
        semi_major_axis_follower,
        e_x_follower,
        e_y_follower,
        inclination_follower,
        right_ascension_follower,
        mean_argument_of_latitude_follower
    ) = classical_to_non_singular_elements(
        semi_major_axis_follower,
        eccentricity_follower,
        inclination_follower,
        right_ascension_follower,
        argument_of_periapsis_follower,
        true_anomaly_follower
    )
    # convert the non-singular orbital elements to relative orbital elements
    return non_singular_to_relative_elements(
        semi_major_axis_leader,
        e_x_leader,
        e_y_leader,
        inclination_leader,
        right_ascension_leader,
        mean_argument_of_latitude_leader,
        semi_major_axis_follower,
        e_x_follower,
        e_y_follower,
        inclination_follower,
        right_ascension_follower,
        mean_argument_of_latitude_follower
    )


def vector_to_relative_elements(
        r_bn_n_leader: np.ndarray,
        v_bn_n_leader: np.ndarray,
        r_bn_n_follower: np.ndarray,
        v_bn_n_follower: np.ndarray,
        planet: str = "earth"
) -> Tuple[float, float, float, float, float, float]:
    """
    Convert the relative position and velocity vectors to relative orbital elements as defined in the PhD Thesis:
    D’Amico, S. (2010). Autonomous Formation Flying in Low Earth Orbit [Delft University of Technology].
    http://www.narcis.nl/publication/RecordID/oai:tudelft.nl:uuid:a10e2d63-399d-48e5-884b-402e9a105c70, Page 21

    :param r_bn_n_leader: Position vector of the leader in the inertial frame in meters
    :type r_bn_n_leader: np.ndarray
    :param v_bn_n_leader: Velocity vector of the leader in the inertial frame in meters per second
    :type v_bn_n_leader: np.ndarray
    :param r_bn_n_follower: Position vector of the follower in the inertial frame in meters
    :type r_bn_n_follower: np.ndarray
    :param v_bn_n_follower: Velocity vector of the follower in the inertial frame in meters per second
    :type v_bn_n_follower: np.ndarray
    :param planet: The name of the planet used to search for the Gravitational parameter of the central body in
                        meters cubed per second squared
    :type planet: str
    :return: A tuple containing the relative orbital elements
                (
                    da: the relative semi-major axis [m]
                    dex: relative e_x [m]
                    dix: relative x component of inclination [m]
                    diy: relative y component of inclination [m]
                    dey: relative e_y [m]
                    daoml: change in mean argument of latitude [m]
                )
    :rtype: tuple
    """
    # calculate the classical elements from the vector elements
    return classical_to_relative_elements(
        # unpack the output of the vector to classical elements function
        *vector_to_classical_elements(
            r_bn_n=r_bn_n_leader,
            v_bn_n=v_bn_n_leader,
            planet=planet,
        ),
        # unpack the output of the vector to classical elements function
        *vector_to_classical_elements(
            r_bn_n=r_bn_n_follower,
            v_bn_n=v_bn_n_follower,
            planet=planet,
        )
    )


def classical_to_relative_elements_mean(
        semi_major_axis_leader: float,
        eccentricity_leader: float,
        inclination_leader: float,
        right_ascension_leader: float,
        argument_of_periapsis_leader: float,
        true_anomaly_leader: float,
        semi_major_axis_follower: float,
        eccentricity_follower: float,
        inclination_follower: float,
        right_ascension_follower: float,
        argument_of_periapsis_follower: float,
        true_anomaly_follower: float,
        planet: str = "earth"
) -> Tuple[float, float, float, float, float, float]:
    """
    Convert classical orbital elements to relative orbital elements as defined in the PhD Thesis:
    D’Amico, S. (2010). Autonomous Formation Flying in Low Earth Orbit [Delft University of Technology].
    http://www.narcis.nl/publication/RecordID/oai:tudelft.nl:uuid:a10e2d63-399d-48e5-884b-402e9a105c70, Page 21

    :param semi_major_axis_leader: Semi-major axis of the leader's orbit in meters
    :type semi_major_axis_leader: float
    :param eccentricity_leader: Eccentricity of the leader's orbit
    :type eccentricity_leader: float
    :param inclination_leader: Inclination of the leader's orbit in radians
    :type inclination_leader: float
    :param right_ascension_leader: Right ascension of the ascending node of the leader's orbit in radians
    :type right_ascension_leader: float
    :param argument_of_periapsis_leader: Argument of periapsis of the leader's orbit in radians
    :type argument_of_periapsis_leader: float
    :param true_anomaly_leader: True anomaly of the leader's orbit in radians
    :type true_anomaly_leader: float
    :param semi_major_axis_follower: Semi-major axis of the follower's orbit in meters
    :type semi_major_axis_follower: float
    :param eccentricity_follower: Eccentricity of the follower's orbit
    :type eccentricity_follower: float
    :param inclination_follower: Inclination of the follower's orbit in radians
    :type inclination_follower: float
    :param right_ascension_follower: Right ascension of the ascending node of the follower's orbit in radians
    :type right_ascension_follower: float
    :param argument_of_periapsis_follower: Argument of periapsis of the follower's orbit in radians
    :type argument_of_periapsis_follower: float
    :param true_anomaly_follower: True anomaly of the follower's orbit in radians
    :type true_anomaly_follower: float
    :param planet: The name of the planet used to search for the Gravitational parameter of the central body in
                        meters cubed per second squared
    :type planet: str
    :return: A tuple containing the relative orbital elements
                (
                    da: the relative semi-major axis [m]
                    dex: relative e_x [m]
                    dix: relative x component of inclination [m]
                    diy: relative y component of inclination [m]
                    dey: relative e_y [m]
                    daoml: change in mean argument of latitude [m]
                )
    :rtype: tuple
"""
    req = get_planet_property(planet=planet, property="REQ")
    j2 = get_planet_property(planet=planet, property="j2")
    ce_leader_mean = mean_to_osculating_elements(
        semi_major_axis=semi_major_axis_leader,
        eccentricity=eccentricity_leader,
        inclination=inclination_leader,
        right_ascension=right_ascension_leader,
        argument_of_periapsis=argument_of_periapsis_leader,
        true_anomaly=true_anomaly_leader,
        req=req,
        j2=j2,
        mean_to_osculating=False
    )
    ce_follower_mean = mean_to_osculating_elements(
        semi_major_axis=semi_major_axis_follower,
        eccentricity=eccentricity_follower,
        inclination=inclination_follower,
        right_ascension=right_ascension_follower,
        argument_of_periapsis=argument_of_periapsis_follower,
        true_anomaly=true_anomaly_follower,
        req=req,
        j2=j2,
        mean_to_osculating=False
    )
    return classical_to_relative_elements(
        semi_major_axis_leader=ce_leader_mean[0],
        eccentricity_leader=ce_leader_mean[1],
        inclination_leader=ce_leader_mean[2],
        right_ascension_leader=ce_leader_mean[3],
        argument_of_periapsis_leader=ce_leader_mean[4],
        true_anomaly_leader=ce_leader_mean[5],
        semi_major_axis_follower=ce_follower_mean[0],
        eccentricity_follower=ce_follower_mean[1],
        inclination_follower=ce_follower_mean[2],
        right_ascension_follower=ce_follower_mean[3],
        argument_of_periapsis_follower=ce_follower_mean[4],
        true_anomaly_follower=ce_follower_mean[5],
    )


def vector_to_relative_elements_mean(
        r_bn_n_leader: np.ndarray,
        v_bn_n_leader: np.ndarray,
        r_bn_n_follower: np.ndarray,
        v_bn_n_follower: np.ndarray,
        planet: str = "earth"
) -> Tuple[float, float, float, float, float, float]:
    """
    Convert the relative position and velocity vectors to relative orbital elements as defined in the PhD Thesis:
    D’Amico, S. (2010). Autonomous Formation Flying in Low Earth Orbit [Delft University of Technology].
    http://www.narcis.nl/publication/RecordID/oai:tudelft.nl:uuid:a10e2d63-399d-48e5-884b-402e9a105c70, Page 21

    :param r_bn_n_leader: Position vector of the leader in the inertial frame in meters
    :type r_bn_n_leader: np.ndarray
    :param v_bn_n_leader: Velocity vector of the leader in the inertial frame in meters per second
    :type v_bn_n_leader: np.ndarray
    :param r_bn_n_follower: Position vector of the follower in the inertial frame in meters
    :type r_bn_n_follower: np.ndarray
    :param v_bn_n_follower: Velocity vector of the follower in the inertial frame in meters per second
    :type v_bn_n_follower: np.ndarray
    :param planet: The name of the planet used to search for the Gravitational parameter of the central body in
                        meters cubed per second squared
    :type planet: str
    :return: A tuple containing the relative orbital elements
                (
                    da: the relative mean semi-major axis [m]
                    dex: relative mean e_x [m]
                    dix: relative mean x component of inclination [m]
                    diy: relative mean y component of inclination [m]
                    dey: relative mean e_y [m]
                    daoml: change in mean, mean argument of latitude [m]
                )
    :rtype: tuple
    """
    # calculate the classical elements from the vector elements
    return classical_to_relative_elements_mean(
        # unpack the output of the vector to classical elements function
        *vector_to_classical_elements(
            r_bn_n=r_bn_n_leader,
            v_bn_n=v_bn_n_leader,
            planet=planet,
        ),
        # unpack the output of the vector to classical elements function
        *vector_to_classical_elements(
            r_bn_n=r_bn_n_follower,
            v_bn_n=v_bn_n_follower,
            planet=planet,
        )
    )


def argument_of_latitude(argument_of_periapsis: float, anomaly: float, angle_max=2*np.pi) -> float:
    """
    Calculate the argument of latitude from the argument of periapsis and the true/mean anomaly.

    If the input anomaly is the true anomaly, then the corresponding argument of latitude will be the true argument of
        latitude. Conversely, if the input anomaly is the mean anomaly, then the corresponding argument of latitude will
        be the mean argument of latitude.

    :param argument_of_periapsis:   [rad] Argument of periapsis
    :type argument_of_periapsis:    float
    :param anomaly:                 [rad] True anomaly
    :type anomaly:                  float
    :param angle_max:               [rad] Maximum angle to normalize the argument of latitude to. If the argument of
                                            periapsis and anomaly are expressed in radians, then angle_max should be
                                            2*np.pi. If the argument of periapsis and anomaly are expressed in degrees,
                                            then angle_max should be 360.
    :type angle_max:                float
    :return:                        [rad] Argument of latitude
    :rtype:                         float
    """
    return utils.normalize_angle(argument_of_periapsis + anomaly, angle_max=angle_max)


def period(semi_major_axis: float, planet="earth") -> float:
    """
    Calculate the orbital period of an orbit with a given semi-major axis and gravitational parameter.

    :param semi_major_axis:     [m] Semi-major axis of the orbit
    :type semi_major_axis:      float
    :param planet:              Name of the planet to use for the calculation
    :type planet:               str
    :return:                    [s] Orbital period
    :rtype:                     float
    """
    # ensure that the semi-major axis is positive
    if semi_major_axis < 0:
        raise ValueError("Semi-major axis must be positive")
    # calculate the gravitational parameter of the central body
    mu = get_planet_mu(planet)
    # calculate the orbital period
    return 2 * np.pi * np.sqrt(semi_major_axis ** 3 / mu)


def mean_motion(semi_major_axis: float, planet="earth") -> float:
    """
    Calculate the mean motion of an orbit with a given semi-major axis and gravitational parameter.

    :param semi_major_axis:     [m] Semi-major axis of the orbit
    :type semi_major_axis:      float
    :param planet:              Name of the planet to use for the calculation
    :type planet:               str
    :return:                    [rad/s] Mean motion
    :rtype:                     float
    """
    # ensure that the semi-major axis is positive
    if semi_major_axis < 0:
        raise ValueError("Semi-major axis must be positive")
    # calculate the gravitational parameter of the central body
    mu = get_planet_mu(planet)
    # calculate the mean motion
    return np.sqrt(mu / semi_major_axis ** 3)
