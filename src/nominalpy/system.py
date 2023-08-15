'''
        [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems
to aid with communication to the public API.
'''

from .request_helper import *
from .value_old import Value
from .credentials import Credentials

'''
Defines a handler for set properties on a specific simulation system
and will be able to manipulate the system.
'''
class System:

    '''
    Defines the name of the simulation system that must be the
    full Nominal Systems system name.
    '''
    __name: str = ""

    '''
    Stores the internal credentials passed from the simulation
    object.
    '''
    __credentials: Credentials = None


    def __init__(self, credentials: Credentials, name: str) -> None:
        '''
        Default construct for the simulation system that takes in the
        credentials passed from the simulation and the full system
        name of the simulation system type.
        '''
        self.__credentials = credentials
        self.__name = name     
    
    def get_value (self, property: str) -> Value:
        '''
        Returns the value of a particular property as a string using
        a GET request. This requires the property name.
        '''
        value = get_request(self.__credentials, "system/property", {"system": self.__name, "name": property})
        return Value(value)
    
    def set_value (self, property: str, value: Value) -> bool:
        '''
        Sets the value of a property to a specific value and returns
        a flag whether it was updated correctly.
        '''
        response = post_request(self.__credentials, "system/property", {"system": self.__name, "name": property, "value": value})
        return response != None