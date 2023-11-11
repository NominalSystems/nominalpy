'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

This file contains public static class methods that can be used to 
convert standard types to the correct JSON format. It also includes
methods that can filter JSON data by a particular parameter for use 
of data analysis. This class should not be instantiated.
'''

import datetime as dt
import numpy as np
from .. import printer


def vector3(x: float, y: float, z: float) -> np.ndarray:
    '''
    Defines a way for specifying a particular value based
    on a Vector3 structure.
    '''
    value: np.ndarray = np.array([x, y, z], dtype=np.float64)
    return value


def matrix33(m1: tuple, m2: tuple, m3: tuple) -> np.ndarray:
    '''
    Defines a way for specifying a particular value based
    on a Matrix3x3 structure.
    '''
    value: np.ndarray = np.array(
        [[m1[0], m1[1], m1[2]],
         [m2[0], m2[1], m2[2]],
         [m3[0], m3[1], m3[2]]],
        dtype=np.float64
    )
    return value


def datetime(year: int, month: int, day: int, hour: int = 0, min: int = 0, sec: int = 0) -> dict:
    '''
    Defines a way of specifying a particular value based on
    a DateTime structure.
    '''
    date: dt.datetime = dt.datetime(year, month, day, hour, min, sec)
    value: dict = {'Year': date.year, 'Month': date.month, 'Day': date.day, 'Hour': date.hour, 'Minute': date.minute, 'Second': date.second}
    return value


def timespan(days: int = 0, hours: int = 0, mins: int = 0, secs: int = 0, milliseconds: int = 0) -> dict:
    '''
    Defines a way of specifying a particular value based on
    a TimeSpan structure
    '''
    value: dict = {'Days': days, 'Hours': hours, 'Minutes': mins, 'Seconds': secs, 'Milliseconds': milliseconds}
    return value


def get_array (data: list, param: str, field: str = None, index: int = None) -> list:
    '''
    Attempts to fetch a particular set of data from a returned
    set of data over time. This assumes the format is of the
    type [{ "data": {} }] as JSON. The field parameter specifies a
    sub-parameter within the data.
    '''
    try:
        if len(data) == 0:
            raise Exception("Data has a length of 0.")
        
        # In the case the param is in the dictionary
        if param in data[0]:
            if field != None and field != "":
                return [_[param][field] for _ in data]
            elif index != None:
                return [_[param][index] for _ in data]
            else:
                return [_[param] for _ in data]
            
        # In the case there is data
        else:
            if field != None and field != "":
                return [_["data"][param][field] for _ in data]
            elif index != None:
                return [_["data"][param][index] for _ in data]
            else:
                return [_["data"][param] for _ in data]
        
    # Catch the exception
    except Exception as ex:
        printer.error("Failed to fetch array from fetched data. Error reason: %s" % str(ex))
        return []