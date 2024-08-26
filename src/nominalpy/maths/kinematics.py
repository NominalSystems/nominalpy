import numpy as np


def to_dcm(right: np.ndarray = None, forward: np.ndarray = None, up: np.ndarray = None) -> np.ndarray:
    """
    Converts the DCM to a new DCM using the provided vectors.

    :param right: A unit vector representing the right axis.
    :param forward: A unit vector representing the forward axis.
    :param up: A unit vector representing the up axis.
    :return: The new DCM.
    """
    # Normalize the input vectors
    if right is not None and forward is not None and up is not None:
        axis_u = up / np.linalg.norm(up)
        axis_r = right / np.linalg.norm(right)
        axis_f = forward / np.linalg.norm(forward)

        # Assign matrix components
        M = np.array([
            [axis_r[0], axis_f[0], axis_u[0]],
            [axis_r[1], axis_f[1], axis_u[1]],
            [axis_r[2], axis_f[2], axis_u[2]]
        ])
    else:
        # Default to identity matrix if no vectors are provided
        M = np.eye(3)
    return M


def up_axis_to_dcm(up: np.ndarray) -> np.ndarray:
    """
    Returns a DCM matrix that aligns the up axis with the given direction.

    :param up: The up axis to align with.
    :return: The DCM aligned to the up axis.
    """
    right_vec = np.array([1, 0, 0])
    forward_vec = np.array([0, 1, 0])
    up_vec = np.array([0, 0, 1])

    # Skip if a zero vector
    if np.linalg.norm(up) == 0:
        raise ValueError("Zero vector provided for up axis.")

    # Check if vectors are aligned
    check = np.dot(right_vec, up)

    # Aligned with up axis
    if check >= 1 - 1e-15:
        return to_dcm(-up_vec, forward_vec, right_vec)

    # Anti-aligned with up axis (down axis)
    if check <= -1 + 1e-15:
        return to_dcm(up_vec, forward_vec, -right_vec)

    # Calculate the axis
    up_norm = up / np.linalg.norm(up)
    forward = np.cross(up_norm, right_vec)
    right = np.cross(forward, up)

    # Return the matrix
    return to_dcm(right, forward, up)