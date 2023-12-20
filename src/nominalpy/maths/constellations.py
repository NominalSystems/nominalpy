from abc import ABC, abstractmethod

import numpy as np

from ..maths.astro import classical_to_vector_elements


def state_vectors(method):
    """
    Decorator to convert a collection of orbital elements into their equivalent inertial state vectors
    :param method: the method to be decorated
    :return: the decorated method
    """
    def wrapper(self, *args, **kwargs):
        orbital_elements = method(self, *args, **kwargs)
        # use dictionary comprehension to efficiently convert the state vectors to classical orbital elements
        return {
            i: classical_to_vector_elements(
                semi_major_axis=elements[0],
                eccentricity=elements[1],
                inclination=elements[2],
                right_ascension=elements[3],
                argument_of_periapsis=elements[4],
                true_anomaly=elements[5],
                *args,
                **kwargs
            ) for i, elements in orbital_elements.items()
        }
    return wrapper


class Constellation(ABC):

    _spacecraft: dict = None

    # the number of satellites in the constellation. There must be at least one spacecraft in the constellation
    _num_satellites: int = None

    # the semi-major axis of every spacecraft in the co-planar constellation
    _semi_major_axis: float = None
    # the eccentricity of every spacecraft in the co-planar constellation
    _eccentricity: float = 0.0
    # the inclination of every spacecraft in the co-planar constellation
    _inclination: float = None
    # the right ascension of every spacecraft in the co-planar constellation
    _right_ascension: float = 0.0
    # the argument of periapsis of every spacecraft in the co-planar constellation
    _argument_of_periapsis: float = 0.0
    # the reference true anomaly offset of every spacecraft in the co-planar constellation
    _true_anomaly_offset: float = 0.0

    @property
    def num_satellites(self) -> int:
        """
        get the number of satellites in the constellation
        :return: the number of satellites in the constellation
        :rtype: int
        """
        return self._num_satellites

    @num_satellites.setter
    def num_satellites(self, num_satellites: int):
        """
        set the number of satellites in the constellation
        :param num_satellites: the number of satellites in the constellation
        :type num_satellites: int
        """
        try:
            num_satellites = int(num_satellites)
        except Exception as e:
            raise TypeError
        # ensure the number of satellites is greater than 0
        if num_satellites < 1:
            raise ValueError
        self._num_satellites = num_satellites

    @property
    def semi_major_axis(self) -> float:
        """
        get the semi-major axis of every spacecraft in the constellation
        :return: the semi-major axis of every spacecraft in the constellation
        :rtype: float
        """
        if self._semi_major_axis is None:
            raise ValueError
        return self._semi_major_axis

    @semi_major_axis.setter
    def semi_major_axis(self, semi_major_axis: float):
        """
        set the semi-major axis of every spacecraft in the constellation
        :param semi_major_axis: the semi-major axis of every spacecraft in the constellation
        :type semi_major_axis: float
        """
        try:
            semi_major_axis = float(semi_major_axis)
        except Exception as e:
            raise TypeError
        # ensure the semi-major axis is greater than 0
        if semi_major_axis < 0:
            raise ValueError
        self._semi_major_axis = semi_major_axis

    @property
    def eccentricity(self) -> float:
        """
        get the eccentricity of every spacecraft in the constellation
        :return: the eccentricity of every spacecraft in the constellation
        :rtype: float
        """
        if self._eccentricity is None:
            raise ValueError
        return self._eccentricity

    @eccentricity.setter
    def eccentricity(self, eccentricity: float):
        """
        set the eccentricity of every spacecraft in the constellation
        :param eccentricity: the eccentricity of every spacecraft in the constellation
        :type eccentricity: float
        """
        try:
            eccentricity = float(eccentricity)
        except Exception as e:
            raise TypeError
        # ensure the eccentricity is greater than 0
        if eccentricity < 0:
            raise ValueError
        self._eccentricity = eccentricity

    @property
    def inclination(self) -> float:
        """
        get the inclination of every spacecraft in the constellation
        :return: the inclination of every spacecraft in the constellation [rad]
        :rtype: float
        """
        if self._inclination is None:
            raise ValueError
        return self._inclination

    @inclination.setter
    def inclination(self, inclination: float):
        """
        set the inclination of every spacecraft in the constellation
        :param inclination: the inclination of every spacecraft in the constellation [rad]
        :type inclination: float
        """
        try:
            inclination = float(inclination)
        except Exception as e:
            raise TypeError
        self._inclination = inclination

    @property
    def right_ascension(self) -> float:
        """
        get the right ascension of every spacecraft in the constellation
        :return: the right ascension of every spacecraft in the constellation [rad]
        :rtype: float
        """
        if self._right_ascension is None:
            raise ValueError
        return self._right_ascension

    @right_ascension.setter
    def right_ascension(self, right_ascension: float):
        """
        set the right ascension of every spacecraft in the constellation
        :param right_ascension: the right ascension of every spacecraft in the constellation [rad]
        :type right_ascension: float
        """
        try:
            right_ascension = float(right_ascension)
        except Exception as e:
            raise TypeError
        self._right_ascension = right_ascension

    @property
    def argument_of_periapsis(self) -> float:
        """
        get the argument of periapsis of every spacecraft in the constellation
        :return: the argument of periapsis of every spacecraft in the constellation [rad]
        :rtype: float
        """
        if self._argument_of_periapsis is None:
            raise ValueError
        return self._argument_of_periapsis

    @argument_of_periapsis.setter
    def argument_of_periapsis(self, argument_of_periapsis: float):
        """
        set the argument of periapsis of every spacecraft in the constellation
        :param argument_of_periapsis: the argument of periapsis of every spacecraft in the constellation [rad]
        :type argument_of_periapsis: float
        """
        try:
            argument_of_periapsis = float(argument_of_periapsis)
        except Exception as e:
            raise TypeError
        self._argument_of_periapsis = argument_of_periapsis

    @property
    def true_anomaly_offset(self) -> float:
        """
        get the true anomaly offset of every spacecraft in the constellation
        :return: the true anomaly offset of every spacecraft in the constellation [rad]
        :rtype: float
        """
        if self._true_anomaly_offset is None:
            raise ValueError
        return self._true_anomaly_offset

    @true_anomaly_offset.setter
    def true_anomaly_offset(self, true_anomaly_offset: float):
        """
        set the true anomaly offset of every spacecraft in the constellation
        :param true_anomaly_offset: the true anomaly offset of every spacecraft in the constellation [rad]
        :type true_anomaly_offset: float
        """
        try:
            true_anomaly_offset = float(true_anomaly_offset)
        except Exception as e:
            raise TypeError
        self._true_anomaly_offset = true_anomaly_offset

    @property
    def spacecraft(self) -> dict:
        """
        get the spacecraft in the constellation
        :return: the spacecraft in the constellation
        :rtype: dict
        """
        return self._spacecraft

    @spacecraft.setter
    def spacecraft(self, spacecraft: dict):
        """
        set the spacecraft in the constellation
        :param spacecraft: the spacecraft in the constellation
        :type spacecraft: dict
        """
        if not isinstance(spacecraft, dict):
            raise TypeError
        self._spacecraft = spacecraft

    def __init__(self, **kwargs):
        super().__init__()
        self.num_satellites = kwargs.get("num_satellites", 1)
        if "semi_major_axis" in kwargs:
            self.semi_major_axis = kwargs.get("semi_major_axis")
        if "eccentricity" in kwargs:
            self.eccentricity = kwargs.get("eccentricity")
        if "inclination" in kwargs:
            self.inclination = kwargs.get("inclination")
        if "right_ascension" in kwargs:
            self.right_ascension = kwargs.get("right_ascension")
        if "argument_of_periapsis" in kwargs:
            self.argument_of_periapsis = kwargs.get("argument_of_periapsis")
        if "true_anomaly_offset" in kwargs:
            self.true_anomaly_offset = kwargs.get("true_anomaly_offset")
        self.spacecraft = kwargs.get("spacecraft", {})

    @abstractmethod
    def init_orbital_elements(self, *args, **kwargs):
        """
        initialize the orbital elements for every spacecraft in the constellation
        :return:
        """
        raise NotImplementedError

    @state_vectors
    def init_state_vectors(self, *args, **kwargs):
        """
        initialize the inertial state vectors for every spacecraft in the constellation
        :return:
        """
        return self.init_orbital_elements()

    def __iter__(self):
        """
        iterate over the spacecraft in the constellation
        :return: an iterator over the spacecraft in the constellation
        """
        return iter(self._spacecraft.items())

    def __getitem__(self, item):
        """
        get a spacecraft in the constellation
        :param item: the spacecraft id
        :return: the spacecraft
        """
        return self._spacecraft[item]

    def __setitem__(self, key, value):
        """
        set a spacecraft in the constellation
        :param key: the spacecraft id
        :param value: the spacecraft
        """
        self._spacecraft[key] = value

    def __delitem__(self, key):
        """
        delete a spacecraft in the constellation
        :param key: the spacecraft id
        """
        del self._spacecraft[key]

    def __len__(self):
        """
        get the number of spacecraft in the constellation
        :return: the number of spacecraft in the constellation
        """
        return len(self._spacecraft)

    def __contains__(self, item):
        """
        check if a spacecraft is in the constellation
        :param item: the spacecraft id
        :return: true if the spacecraft is in the constellation, false otherwise
        """
        return item in self._spacecraft

    def __str__(self):
        """
        get the string representation of the constellation
        :return: the string representation of the constellation
        """
        return str(self._spacecraft)

    def __repr__(self):
        """
        get the string representation of the constellation
        :return: the string representation of the constellation
        """
        return repr(self._spacecraft)

    def __eq__(self, other):
        """
        check if two constellations are equal
        :param other: the other constellation
        :return: true if the two constellations are equal, false otherwise
        """
        raise NotImplementedError

    def __ne__(self, other):
        """
        check if two constellations are not equal
        :param other: the other constellation
        :return: true if the two constellations are not equal, false otherwise
        """
        return not self.__eq__(other)

    def __hash__(self):
        """
        get the hash of the constellation
        :return: the hash of the constellation
        """
        return hash(self._spacecraft)

    def __bool__(self):
        """
        check if the constellation is not empty
        :return: true if the constellation is not empty, false otherwise
        """
        return bool(self._spacecraft)


class Coplanar(Constellation):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def init_orbital_elements(self, *args, **kwargs):
        """
        initialize the orbital elements for every spacecraft in the constellation
        :return:
        """
        relative_phase: float = 2 * np.pi / self.num_satellites
        # use dictionary comprehension to efficiently initialize the orbital elements for every spacecraft in the
        #   constellation
        self._spacecraft = {
            i: (
                self.semi_major_axis,
                self.eccentricity,
                self.inclination,
                self.right_ascension,
                self.argument_of_periapsis,
                self.true_anomaly_offset + i * relative_phase
            ) for i in range(self.num_satellites)
        }
        return self._spacecraft


class CoplanarCircular(Coplanar):

    _eccentricity = 0.0

    @property
    def eccentricity(self) -> float:
        return 0.0

    @eccentricity.setter
    def eccentricity(self, eccentricity: float):
        self._eccentricity = 0.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.eccentricity = 0


class Walker(Constellation):
    """
    A Walker constellation is a constellation of satellites that are evenly spaced in a Walker pattern.
    """

    _num_planes: int = 1

    @property
    def num_planes(self) -> int:
        """
        get the number of planes in the constellation
        :return: the number of planes in the constellation
        :rtype: int
        """
        return self._num_planes

    @num_planes.setter
    def num_planes(self, num_planes: int):
        """
        set the number of planes in the constellation
        :param num_planes: the number of planes in the constellation
        :type num_planes: int
        """
        try:
            num_planes = int(num_planes)
        except Exception as e:
            raise TypeError
        # ensure the number of planes is greater than 0
        if num_planes < 1:
            raise ValueError
        self._num_planes = num_planes

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num_planes = kwargs.get("num_planes", 1)


class WalkerDelta(Walker):
    """
    A Walker Delta constellation is a constellation of satellites that are evenly spaced in a Walker Delta pattern.
    """

    _relative_spacing = 1.0

    @property
    def relative_spacing(self) -> float:
        """
        get the relative spacing of the constellation
        :return: the relative spacing of the constellation
        :rtype: float
        """
        return self._relative_spacing

    @relative_spacing.setter
    def relative_spacing(self, relative_spacing: float):
        """
        set the relative spacing of the constellation
        :param relative_spacing: the relative spacing of the constellation
        :type relative_spacing: float
        """
        try:
            relative_spacing = float(relative_spacing)
        except Exception as e:
            raise TypeError
        # ensure the relative spacing is greater than 0
        if relative_spacing < 0:
            raise ValueError
        self._relative_spacing = relative_spacing

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.relative_spacing = kwargs.get("relative_spacing", 1.0)

    def init_orbital_elements(self, *args, **kwargs):
        """
        initialize the orbital elements for every spacecraft in the constellation
        :param args:
        :param kwargs:
        :return:
        """
        if self.num_planes > self.num_satellites:
            self.num_planes = self.num_satellites
        # define the full rotation
        full_rotation = 2*np.pi
        # get the relative spacing parameter which must be within 0 and the number of planes
        relative_spacing = min(max(abs(self.relative_spacing), 0), self.num_planes)
        # calculate the relative phase which will determine the phase offset in true anomaly of spacecraft in every
        #   plane
        relative_phase = relative_spacing * full_rotation / self.num_satellites
        # perform integer division to get the number of satellites per plane as a discrete number
        num_satellites_plane = self.num_satellites // self.num_planes
        # calculate the relative anomaly which will determine the difference in true anomaly between every spacecraft
        relative_anom = full_rotation / num_satellites_plane
        # raise an exception if the number of satellites isn't perfectly divisible into the number of planes
        if self.num_satellites % self.num_planes != 0:
            raise ValueError("The number of satellites should be divisible by the number of planes")
        # set the initial orbital elements for each spacecraft in the constellation
        for i in range(self.num_planes):
            for j in range(num_satellites_plane):
                true_anom = relative_phase * i + relative_anom * j + self.true_anomaly_offset
                raan = full_rotation / self.num_planes * i + self.right_ascension
                index = i * num_satellites_plane + j
                self._spacecraft[index] = (
                    self.semi_major_axis,
                    self.eccentricity,
                    self.inclination,
                    raan,
                    self.argument_of_periapsis,
                    true_anom
                )
        # return the orbital elements
        return self._spacecraft
