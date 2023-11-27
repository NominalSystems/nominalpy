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


def get_planet_property (planet: str, property: str) -> float:
    '''
    Returns the planet's property. If the planet does not exist,
    then an exception will be thrown.

    :param planet:      The name of the planet to fetch the property from
    :type planet:       str
    :param property:    The name of the property to fetch
    :type property:     str

    :return:            The value of the property
    :rtype:             float
    '''
    param = f"{planet.upper()}_{property.upper()}"
    if hasattr(constants, param):
        return float(getattr(constants, param))

    # Throw an error if this occurs
    else:
        raise NominalException(f"No planet: {planet} with property {property}.")

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
    return get_planet_property(planet, "MU")

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

    :returns:
    :rtype:
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


def pcpf_to_geodetic_lla (position: np.ndarray, planet="Earth") -> np.ndarray:
    '''
    Converts the Planet-Centred, Planet-Fixed parameters to Latitude, 
    Longitude, and Altitude using NumPy.

    :param position:    The current ECPF position as a NumPy array or list (X, Y, Z)
    :type position:     np.ndarray
    :param planet:      The planet to use for the conversion
    :type planet:       str

    :return:            Tuple containing Latitude [rad], Longitude [rad], and Altitude [m]
    :rtype:             np.ndarray
    '''
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
    '''
    Converts the Planet-Centred, Planet-Fixed parameters to Latitude, 
    Longitude, and Altitude using NumPy.

    :param position:    The current ECPF position as a NumPy array or list (X, Y, Z)
    :type position:     np.ndarray
    :param planet:      The planet to use for the conversion
    :type planet:       str

    :return:            Tuple containing Latitude [deg], Longitude [deg], and Altitude [m]
    :rtype:             np.ndarray
    '''
    lla = pcpf_to_geodetic_lla(position, planet=planet)
    return np.array([np.degrees(lla[0]), np.degrees(lla[1]), lla[2]], dtype=np.float64)


def geodetic_lla_to_pcpf (lla: np.ndarray, planet="Earth") -> np.ndarray:
    '''
    Converts from Latitude/Longitude/Altitude (LLA) coordinates to Planet-Centered,
    Planet-Fixed (PCPF) coordinates given a planet radius.

    :param lla:     A tuple or list containing Latitude (radians), Longitude (radians), and Altitude (meters) coordinates.
    :type lla:      np.ndarray
    :param planet:  The planet to use for the conversion
    :type planet:   str

    :return:        A tuple representing the final position in the PCPF frame in meters.
    :rtype:         np.ndarray
    '''
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
    '''
    Converts from Latitude/Longitude/Altitude (LLA) coordinates to Planet-Centered,
    Planet-Fixed (PCPF) coordinates given a planet radius.

    :param lla:     A tuple or list containing Latitude (degrees), Longitude (degrees), and Altitude (meters) coordinates.
    :type lla: n    p.ndarray
    :param planet:  The planet to use for the conversion
    :type planet:   str

    :return:        A tuple representing the final position in the PCPF frame in meters.
    :rtype:         np.ndarray
    '''

    # Convert latitude and longitude from degrees to radians
    lat: float = np.radians(lla[0])  # Latitude in radians
    lon: float = np.radians(lla[1])  # Longitude in radians
    return geodetic_lla_to_pcpf(np.array([lat, lon, lla[2]], dtype=np.float64), planet=planet)

def calculate_orbital_velocity(r_bn_n_mag: float, sma: float, gm: float = constants.EARTH_MU) -> float:
    '''
    Calculate the magnitude of the orbital velocity for a spacecraft in any orbit type.

    This function uses the vis-viva equation to compute the orbital speed of a spacecraft at a given distance from the
        Earth's center, considering its semi-major axis. It ensures that the provided parameters are within physically
        meaningful ranges.

    :param r_bn_n_mag:  The distance from the Earth's center to the spacecraft - m.
    :type r_bn_n_mag:   float
    :param sma:         The semi-major axis of the spacecraft's orbit. It must be a non-negative value - m
    :type sma:          float
    :param gm:          The gravitational parameter, defaulting to Earth's gravitational parameter if not provided - m^3/s^2.
    :type gm:           float

    :return:            The magnitude of the spacecraft's orbital velocity - m/s.
    :rtype: float

    :raises TypeError:  If `r` or `sma` is not a numeric type.
    :raises ValueError: If `r` is less than zero, or `sma` is negative, or the radicand in the calculation is negative.

    Example:
        >>> calculate_orbital_velocity(7000, 10000)
        7.546049108166282
    '''
    if r_bn_n_mag <= 0:
        raise ValueError(f"The input distance from Earth's center (r: {r_bn_n_mag} km) is not valid.")
    if sma < 0:
        raise ValueError(f"The input semi-major axis (sma: {sma} km) is not valid.")
    # sanity check the input parameters
    radicand = 2 * gm * (1 / r_bn_n_mag - 1 / (2 * sma))
    if radicand < 0:
        raise ValueError(f"The radicand ({radicand}) is not greater than zero, leading to a singularity.")
    # calculate the orbital velocity
    return np.sqrt(radicand)

def calculate_circular_orbit_velocity(sma: float, gm=constants.EARTH_MU) -> float:
    '''
    Calculates the magnitude of the orbital velocity for a spacecraft in 
    a circular orbit.

    :param sma: The semi-major axis of the spacecraft's orbit. It must be a non-negative value - m
    :type sma:  float
    :param gm:  The gravitational parameter, defaulting to Earth's gravitational parameter if not provided - m^3/s^2.
    :type gm:   float
    
    :return:    The magnitude of the spacecraft's orbital velocity resulting in a circular orbit - m/s.
    :rtype:     float
    '''
    return calculate_orbital_velocity(r_bn_n_mag=sma, sma=sma, gm=gm)
