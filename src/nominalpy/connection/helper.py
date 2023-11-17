#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2023.

'''
This modules assists with some helper functions for defining what values
can be turned into JSON and whether GUID IDs are valid.
'''

import json

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