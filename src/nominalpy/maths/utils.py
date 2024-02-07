#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

'''
This module contains public methods that aid with mathematical
calculations and astrophysical dimensions.
'''

import numpy as np


def acos_quadrant_check(adjacent: float, hypotenuse: float, test: float) -> float:
    """
    Calculate an angle using the arccosine function and perform a 
    quadrant check. The function calculates the angle using the arccosine 
    of the ratio of the adjacent side to the hypotenuse. It adjusts the 
    angle based on the quadrant determined by the 'test' parameter.

    :param adjacent:    The length of the adjacent side of a right triangle.
    :type adjacent:     float
    :param hypotenuse:  The length of the hypotenuse of the triangle.
    :type hypotenuse:   float
    :param test:        A value to determine the quadrant of the angle.
    :type test:         float

    :returns:           The calculated angle in radians.
    :rtype:             float
    """
    # Calculate the ratio of the adjacent side to the hypotenuse
    rat = adjacent / hypotenuse

    # Adjust the ratio if the adjacent side is slightly greater than the hypotenuse
    if adjacent > hypotenuse:
        if np.fabs((adjacent - hypotenuse) / hypotenuse) < 1e-10:
            rat = 1.0
        else:
            raise ValueError("The adjacent: {}, is greater than the hypotenuse: {}".format(adjacent, hypotenuse))
    # Calculate the angle using arccos; adjust based on the 'test' parameter
    return 2*np.pi - np.arccos(rat) if test < 0 else np.arccos(rat)


def normalize_angle(angle: float, angle_max: float = 2*np.pi) -> float:
    """
    normalize an angle between 0 <= theta < max, where max is an arbitrary angle

    :param angle:   The angle to be normalized
    :type angle:    float
    :param angle_max:     The maximum value for the angle
    :type angle_max:      float

    :returns:       The normalized angle
    :rtype:         float
    """
    angle = np.fmod(angle, angle_max)
    if angle < 0:
        angle += angle_max
    return angle


def shortest_angular_difference(angle1: float, angle2: float) -> float:
    """
    Calculate the shortest angular difference between two angles. This function
    calculates the shortest angular difference between two angles using the
    arccosine function and the quadrant check function.

    :param angle1:  The first angle
    :type angle1:   float
    :param angle2:  The second angle
    :type angle2:   float

    :returns:       The shortest angular difference between the two angles
    :rtype:         float
    """
    # Calculate the difference between the two angles
    d_angle: float = angle1 - angle2
    # Get the alternative angle
    alt_angle: float = -np.sign(d_angle) * (2 * np.pi - np.fabs(d_angle))
    # Return the shortest angle
    return alt_angle if np.fabs(alt_angle) < np.fabs(d_angle) else d_angle


def normalize_array(array: np.ndarray) -> np.ndarray:
    """
    Normalize a numpy array. This function normalizes a numpy array by
    dividing each element by the magnitude of the array.

    :param array:   The array to be normalized
    :type array:    np.ndarray

    :returns:       The normalized array
    :rtype:         np.ndarray
    """
    # Return the normalized array
    return array / np.linalg.norm(array)


def parallel_vector(v1: np.ndarray, v_ref: np.ndarray) -> np.ndarray:
    """
    Calculate the component of v1 that is parallel with v_ref.

    :param v1:  The first vector
    :type v1:   np.ndarray
    :param v_ref:  The second vector
    :type v_ref:   np.ndarray

    :returns:   The parallel vector of the two vectors
    :rtype:     np.ndarray
    """
    # find the parrallel component
    reference_normalised = normalize_array(v_ref)
    return reference_normalised * np.dot(v1, reference_normalised)


def perpendicular_vector(v1: np.ndarray, v_ref: np.ndarray) -> np.ndarray:
    """
    Calculate the perpendicular vector of two vectors. This function calculates
    the perpendicular vector of two vectors using the dot product and the magnitude
    of each vector. The perpendicular vector is calculated using the dot product
    and the magnitude of the first vector.

    :param v1:  The first vector
    :type v1:   np.ndarray
    :param v_ref:  The second vector
    :type v_ref:   np.ndarray

    :returns:   The perpendicular vector of the two vectors
    :rtype:     np.ndarray
    """
    # find the perpendicular component
    return v1 - parallel_vector(v1, v_ref)


def angle_between_vectors(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Calculate the angle between two vectors. This function calculates the
    angle between two vectors using the dot product and the magnitude of
    each vector. The angle is calculated using the arccosine function.

    :param v1:  The first vector
    :type v1:   np.ndarray
    :param v2:  The second vector
    :type v2:   np.ndarray

    :returns:   The angle between the two vectors in radians.
    :rtype:     float
    """

    # Calculate the dot product of the two vectors
    dot: float = np.dot(v1, v2)

    # Calculate the magnitude of each vector
    denom: float = np.linalg.norm(v1) * np.linalg.norm(v2)
    if denom == 0:
        raise ZeroDivisionError
    # Calculate the angle between the two vectors
    angle: float = acos_quadrant_check(dot, denom, dot)

    return angle
