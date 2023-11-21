#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2023.

'''
This modules assists with some helper functions for defining what values
can be turned into JSON and whether GUID IDs are valid. This also includes
some methods for serializing and deserializing JSON data to standard formats,
including numpy ndarrays and datetimes.
'''

import json, numpy as np
from datetime import datetime
from ..maths import value
from ..utils import printer

def jsonify (data: dict, array: bool = False) -> str:
    '''
    Converts a particular data as a dictionary to string
    using the JSON payload and has an optional parameter
    to wrap the data inside of an array.
    
    :param data:    The raw set of dictionary data that will be returned to a JSON string
    :type data:     dict
    :param array:   A flag whether to transform the data within an array framework
    :type array:    bool

    :returns:       The JSON data in a string form
    :rtype:         str
    '''

    if array:
        return "[%s]" %  json.dumps(data)
    return json.dumps(data)

def serialize (params: dict) -> dict:
    '''
    Attempts to create a JSON dictionary based on a series of
    parameters that are parsed in from the user. This will
    construct the data from numpy arrays and other data formats
    that need to be serialized correctly.

    :param params:  A list of arguments from the object that should be serialized
    :type params:   dict

    :returns:       A full dictionary in a JSON format of the serialized data
    :rtype:         dict
    '''

    # Create the dictionary of data
    data: dict = {}

    # Loops through each keyword argument
    for key in params:
        data[key] = serialize_object(params[key])

    # Returns the final output
    return data

def serialize_object (obj: object) -> dict:
    '''
    Attempts to create a JSON serialized object based on a
    single object that is parsed into the system. This will
    check based on standard python types including numpy
    arrays and datetimes.

    :param obj: An object to be serialized
    :type obj:  object

    :returns:   A full dictionary in a JSON format of the serialized data
    :rtype:     dict
    
    '''

    if isinstance(obj, np.ndarray):  # Mathematical arrays
        shape = obj.shape
        if shape == (3,):       # Vector3
            return value.vector3(obj[0], obj[1], obj[2])
        elif shape == (3,3):    # Matrix3x3
           return value.matrix33(obj[0], obj[1], obj[2])
        else:
            printer.error("Unsupported numpy array shape: %s." % str(shape))
            return {}
    elif isinstance(obj, datetime):   # DateTimes
        return value.datetime(obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second)
    else:   # All other values
        return obj

def deserialize (param: object) -> object:
    '''
    Attempts to deserialize a particular object based on the data
    within the dictionary and returns the data in a specific way
    that is expected within Python. This means that numpy arrays
    will be returned if they contain the correct data.

    :params param:  The parameter that should be deserialized
    :type param:    object

    :returns:       The object from the deserialization
    :rtype:         object
    '''

    # Handle dictionaries or skip
    if isinstance(param, dict):
        if contains(param, "X", "Y", "Z"):
            return np.array([param["X"], param["Y"], param["Z"]])

    # Handles arrays for matricies
    if isinstance(param, list):
        if len(param) == 9:
            return np.array([param[0:3], param[3:6], param[6:9]])

    # Return whatever the parameter was
    return param

def contains (data: dict, *args) -> bool:
    '''
    Determines if a particular set of parameter names exist within
    a dictionary and returns whether all arguments exist.

    :param data:    The raw dictionary data containing some arguments
    :type data:     dict
    :param args:    A list of argument names to check within the dictionary
    :type args:     list

    :returns:       A flag indicating that all the arguments exist within the dictionary
    :rtype:         bool
    '''

    # Loop through all the arguments
    for arg in args:
        if not arg in data:
            return False

    # Returns a success
    return True

def is_valid_guid (guid: str) -> bool:
    '''
    Determines if a parsed GUID, as a string,
    is valid. This will ensure that it is of
    the correct format.

    :param guid:    The unique GUID of the object, in the correct form
    :type guid:     str

    :returns:       A flag whether the GUID is valid
    :rtype:         bool
    '''

    empty: str = "00000000-0000-0000-0000-000000000000"
    if guid == empty: return False
    if len(guid) != len(empty): return False
    if guid[8] != empty[8]: return False
    if guid[13] != empty[13]: return False
    if guid[18] != empty[18]: return False
    if guid[23] != empty[23]: return False
    return True