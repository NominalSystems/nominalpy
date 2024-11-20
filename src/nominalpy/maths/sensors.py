import numpy as np


def calculate_focal_length(area_mm2, fov_degrees):
    """
    Calculate the focal length of a camera given the sensor area and field of view.

    :param area_mm2: The area of the sensor in square millimeters.
    :type area_mm2: float
    :param fov_degrees: The field of view of the camera in degrees.
    :type fov_degrees: float
    :return: The focal length of the camera in millimeters.
    :rtype: float
    """
    # Assuming a square sensor
    sensor_width_mm = np.sqrt(area_mm2)
    # Convert FOV to radians
    fov_radians = np.radians(fov_degrees)
    # Calculate focal length
    focal_length_mm = sensor_width_mm / (2 * np.tan(fov_radians / 2))
    return focal_length_mm
