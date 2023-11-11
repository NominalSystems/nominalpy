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
        if abs(a) > EPS:
            p = a * (1 - e * e)             # elliptic or hyperbolic 
        else:
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
    classical_to_vector_elements_rad(
        semi_major_axis=semi_major_axis,
        eccentricity=eccentricity,
        inclination=inclination * constants.D2R,
        argument_of_periapsis=argument_of_periapsis * constants.D2R,
        right_ascension=right_ascension * constants.D2R,
        true_anomaly=true_anomaly * constants.D2R,
        planet=planet
    )
