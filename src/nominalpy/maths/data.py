

def bytes2bits(bytes: float) -> int:
    """
    Convert a quantity from bytes to bits.

    :param bytes: The number of bytes to be converted.
    :type bytes: float
    :raises ValueError: If the input bytes is a negative integer.
    :return: The equivalent number of bits.
    :rtype: int

    This function calculates the number of bits that correspond to a given number of bytes.
    Note that 1 byte equals 8 bits.
    """
    if bytes < 0:
        raise ValueError("bytes must be a positive float")
    try:
        bytes = float(bytes)
    except TypeError:
        raise TypeError("bytes must be a positive float")
    return int(bytes * 8)


def kilobytes2bytes(kilobytes: float) -> int:
    """
    Convert a quantity from kilobytes to bytes.

    :param kilobytes: The number of kilobytes to be converted.
    :type kilobytes: float
    :return: The equivalent number of bits.
    :rtype: int

    This function uses the `bytes2bytes` function for the conversion, considering
    that 1 kilobyte equals 1024 bytes.
    """
    if kilobytes < 0:
        raise ValueError("kilobytes must be a positive float")
    try:
        kilobytes = float(kilobytes)
    except TypeError:
        raise TypeError("kilobytes must be a positive float")
    return int(kilobytes * 1024)


def megabytes2bytes(megabytes: float) -> int:
    """
    Convert a quantity from megabytes to bytes.

    :param megabytes: The number of megabytes to be converted.
    :type megabytes: float
    :return: The equivalent number of bits.
    :rtype: int

    This function uses the `kilobytes2bytes` function for the conversion, considering
    that 1 megabyte equals 1024 kilobytes.
    """
    return kilobytes2bytes(megabytes * 1024)


def gigabytes2bytes(gigabytes: float) -> int:
    """
    Convert a quantity from gigabytes to bytes.

    :param gigabytes: The number of gigabytes to be converted.
    :type gigabytes: float
    :return: The equivalent number of bits.
    :rtype: int

    This function uses the `megabytes2bytes` function for the conversion, considering
    that 1 gigabyte equals 1024 megabytes.
    """
    return megabytes2bytes(gigabytes * 1024)


def kilobytes2bits(kilobytes: float) -> int:
    """
    Convert a quantity from kilobytes to bits.

    :param kilobytes: The number of kilobytes to be converted.
    :type kilobytes: float
    :return: The equivalent number of bits.
    :rtype: int

    This function uses the `bytes2bits` function for the conversion, considering
    that 1 kilobyte equals 1024 bytes.
    """
    return bytes2bits(kilobytes2bytes(kilobytes))


def megabytes2bits(megabytes: float) -> int:
    """
    Convert a quantity from megabytes to bits.

    :param megabytes: The number of megabytes to be converted.
    :type megabytes: float
    :return: The equivalent number of bits.
    :rtype: int
    """
    return bytes2bits(megabytes2bytes(megabytes))


def gigabytes2bits(gigabytes: float) -> int:
    """
    Convert a quantity from gigabytes to bits.

    :param gigabytes: The number of gigabytes to be converted.
    :type gigabytes: float
    :return: The equivalent number of bits.
    :rtype: int

    """
    return bytes2bits(gigabytes2bytes(gigabytes))
