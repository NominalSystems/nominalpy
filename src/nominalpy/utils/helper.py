#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

'''
This modules assists with some helper functions for defining what values
can be turned into JSON and whether GUID IDs are valid. This also includes
some methods for serializing and deserializing JSON data to standard formats.
'''

import numpy as np
from datetime import datetime
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
            type = f"NominalSystems.{namespace}." + type
        else:
            type = "NominalSystems." + type
    
    # For certain types, ensure the namespace is correct
    universe_types: list = ["UniverseObject", "UniverseModel", "UniverseBehaviour", "UniverseSystem",
        "ExtensionSystem", "MaritimeSystem", "SolarSystem", "TrackingSystem", "CelestialBody",
        "PhysicalObject", "DynamicEffector", "StateEffector", "GroundObject", "GroundStation",
        "Vehicle", "Vessel", "Rover", "Spacecraft", "StarSphere", "BodyEffector", "AlbedoPlanetModel", 
        "AlbedoModel", "AtmosphereModel", "AtmospherePlanetModel", "AtmosphereExponentialPlanetModel",
        "AtmosphereNRLMSISPlanetModel", "ElectromagneticModel", "GravityModel", "MagneticFieldPlanetModel",
        "MagneticFieldCenteredDipolePlanetModel", "MagneticFieldWMMPlanetModel", "MagneticModel",
        "SolarModel", "SphericalHarmonicsModel", "StateModel", "ThermalModel"]
    
    # If the type is a universe type, ensure the namespace is correct
    small_type: str = type.split(".")[-1]
    if small_type in universe_types:
        return "NominalSystems.Universe." + small_type

    # Return the correct type
    return type

def serialize (value: any) -> any:
    '''
    Serializes the value into a JSON serializable format. This will
    convert the value into a list if it is a numpy array or a datetime
    into a string.

    :param value:   The value to serialize
    :type value:    any

    :returns:       The serialized value
    :rtype:         any
    '''

    # Check if the value is a numpy array
    if isinstance(value, np.ndarray):
        # Check if the numpy array contains numbers
        if np.issubdtype(value.dtype, np.number):
            return value.tolist()  # Convert to list or list of lists
        return value
        
    # Check if the value is a datetime
    if isinstance(value, datetime):
        return value.strftime('%Y/%m/%d %H:%M:%S.%f')
    
    # Check if the value is a simulation instance
    if hasattr(value, 'id') and hasattr(value, 'get_type'):
        return value.id
    
    # Return the value as is for other types
    return value

def deserialize (value: any) -> any:
    '''
    Deserializes the value from a JSON serializable format. This will
    convert the value into a numpy array if it is a list of numbers or
    a datetime string into a datetime object.

    :param value:   The value to deserialize
    :type value:    any

    :returns:       The deserialized value
    :rtype:         any
    '''

    # Check if the value is a list
    if isinstance(value, list):

        # Attempt to convert list of numbers to a numpy array
        try:
            array = np.array(value)
            if np.issubdtype(array.dtype, np.number):
                return array
        except:
            pass

        # If conversion fails or is not a list of numbers, return the list as is
        return value
    
    # Check if the value is a datetime string
    if isinstance(value, str):
        try:
            # Handle datetime string with variable microseconds length
            date_part, time_part = value.split(" ")
            if '.' in time_part:
                time_main, microseconds = time_part.split(".")
                if len(microseconds) > 6:
                    microseconds = microseconds[:6]  # Truncate to 6 digits
                value = f"{date_part} {time_main}.{microseconds}"
            return datetime.strptime(value, '%Y/%m/%d %H:%M:%S.%f')
        except ValueError:
            return value
        
    # Return the value as is for other types
    return value