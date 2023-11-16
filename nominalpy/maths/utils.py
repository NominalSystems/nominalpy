import numpy as np


def acos_quadrant_check(adjacent, hypotenuse, test):
    """
    Calculate an angle using the arccosine function and perform a quadrant check.

    :param adjacent: The length of the adjacent side of a right triangle.
    :type adjacent: float
    :param hypotenuse: The length of the hypotenuse of the triangle.
    :type hypotenuse: float
    :param test: A value to determine the quadrant of the angle.
    :type test: float
    :return: The calculated angle in radians.
    :rtype: float

    The function calculates the angle using the arccosine of the ratio of the adjacent side to the hypotenuse.
    It adjusts the angle based on the quadrant determined by the 'test' parameter.
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