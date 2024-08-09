#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

'''
This modules assists with some helper functions for defining what values
can be turned into JSON and whether GUID IDs are valid. This also includes
some methods for serializing and deserializing JSON data to standard formats.
'''

from ..utils import NominalException

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
    if guid == None: return False
    if guid == empty: return False
    if len(guid) != len(empty): return False
    if guid[8] != empty[8]: return False
    if guid[13] != empty[13]: return False
    if guid[18] != empty[18]: return False
    if guid[23] != empty[23]: return False
    return True

def validate_type (type: str, namespace: str = "Classes") -> str:
    '''
    Validates the type of the object and ensures that it is in the correct format.
    This will return the correct type with the namespace if it is not already present.

    :param type:        The type of the object to validate
    :type type:         str
    :param namespace:   The namespace to use for the type
    :type namespace:    str

    :returns:           The validated type with the namespace
    :rtype:             str
    '''

    # Check for an invalid or missing
    if type == None or type == "":
        raise NominalException("Invalid Type: No instance type passed when constructing an instance.")

    # Make sure the type is pascal cased
    type = type[0].upper() + type[1:]

    # Ensure the type has the namespace
    if "NominalSystems" not in type:
        if "." not in type:
            return f"NominalSystems.{namespace}." + type
        return "NominalSystems." + type

    # Return the correct type
    return type