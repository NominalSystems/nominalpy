#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2023.

'''
This module contains public static class methods that can be used to 
convert standard types to the correct JSON format. It also includes
methods that can filter JSON data by a particular parameter for use 
of data analysis. This class should not be instantiated.
'''

import datetime as dt
import numpy as np
from ..utils import printer


def vector3 (x: float, y: float, z: float) -> dict:
    '''
    Defines a way for specifying a particular value based
    on a Vector3 structure.

    :param x:   The X value of the vector
    :type x:    float
    :param y:   The Y value of the vector
    :type y:    float
    :param z:   The Z value of the vector
    :type z:    float

    :returns:   The JSON dictionary of the vector
    :rtype:     dict
    '''

    value: dict = {"X": float(x), "Y": float(y), "Z": float(z)}
    return value

def matrix33 (m1: tuple, m2: tuple, m3: tuple) -> list:
    '''
    Defines a way for specifying a particular value based
    on a Matrix3x3 structure.
    
    :param m1:  The first row of three elements to add to the matrix
    :type m1:   tuple
    :param m2:  The second row of three elements to add to the matrix
    :type m2:   tuple
    :param m3:  The third row of three elements to add to the matrix
    :type m3:   tuple

    :returns:   A matrix3x3 list of data in the correct format
    :rtype:     list
    '''

    value: list = [[float(m1[0]), float(m1[1]), float(m1[2])], 
        [float(m2[0]), float(m2[1]), float(m2[2])], 
        [float(m3[0]), float(m3[1]), float(m3[2])]]
    return value

def datetime (year: int, month: int, day: int, hour: int = 0, min: int = 0, sec: int = 0) -> dict:
    '''
    Defines a way of specifying a particular value based on
    a DateTime structure.

    :param year:    The year parameter of the datetime
    :type year:     int
    :param month:   The month parameter of the datetime
    :type month:    int
    :param day:     The day parameter of the datetime
    :type day:      int
    :param hour:    The hour parameter of the datetime
    :type hour:     int
    :param min:     The minute parameter of the datetime
    :type min:      int
    :param sec:     The second parameter of the datetime
    :type sec:      int

    :returns:       A correctly formatted dictionary of JSON values with the data
    :rtype:         dict
    '''

    date: dt.datetime = dt.datetime(year, month, day, hour, min, sec)
    value: dict = {'Year': date.year, 'Month': date.month, 'Day': date.day, 'Hour': date.hour, 'Minute': date.minute, 'Second': date.second}
    return value

def timespan (days: int = 0, hours: int = 0, mins: int = 0, secs: int = 0, millis: int = 0) -> dict:
    '''
    Defines a way of specifying a particular value based on
    a TimeSpan structure.

    :param days:    The number of days in the timespan
    :type days:     int
    :param hours:   The number of hours in the timespan
    :type hours:    int
    :param mins:    The number of minutes in the timespan
    :type mins:     int
    :param secs:    The number of seconds in the timespan
    :type secs:     int
    :param millis:  The number of milliseconds in the timespan
    :type millis:   int

    :returns:       A correctly formatted dictionary of JSON values with the data
    :rtype:         dict
    '''

    value: dict = {'Days': days, 'Hours': hours, 'Minutes': mins, 'Seconds': secs, 'Milliseconds': millis}
    return value

def get_array (data: list, param: str, field: str = None, index: int = None) -> np.ndarray:
    '''
    Attempts to fetch a particular set of data from a returned
    set of data over time. This assumes the format is of the
    type [{ "data": {} }] as JSON. The field parameter specifies a
    sub-parameter within the data.

    :param data:    A list of raw data containing all the data that needs to be formatted
    :type data:     list
    :param param:   A specific parameter to search for in the data
    :type param:    str
    :param field:   An optional field parameter within the parameter to search for
    :type field:    str
    :param index:   The index of the data within the parameter to fetch
    :type index:    int

    :returns:       A list of the data in the correct formatted type
    :rtype:         list
    '''

    try:
        if len(data) == 0:
            raise Exception("Data has a length of 0.")
        
        array: list = []
        
        # In the case the param is in the dictionary
        if param in data[0]:
            if field != None and field != "":
                array = [_[param][field] for _ in data]
            elif index != None:
                array = [_[param][index] for _ in data]
            else:
                array = [_[param] for _ in data]
            
        # In the case there is data
        else:
            if field != None and field != "":
                array = [_["data"][param][field] for _ in data]
            elif index != None:
                array = [_["data"][param][index] for _ in data]
            else:
                array = [_["data"][param] for _ in data]
        
        # Return the array as a numpy array
        return np.array(array)
        
    # Catch the exception
    except Exception as ex:
        printer.error("Failed to fetch array from fetched data. Error reason: %s" % str(ex))
        return np.array([[]])