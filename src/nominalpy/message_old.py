'''
        [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems
to aid with communication to the public API.
'''

from .request_helper import *
from .value_old import Value
import json

'''
The message class is used for storing data about a particular
set of parameters using the inbuilt Messaging system.
'''
class Message:

    # Stores the ID of the message
    id: str = None

    '''
    Stores the credentials to the message that is defined by the
    simulation that creates it.
    '''
    __credentials: Credentials = None


    def __init__(self, credentials: Credentials, id: str) -> None:
        '''
        Defines the constructor for the message that
        sets the ID of the message
        '''
        self.__credentials = credentials
        self.id = id

    def get_value (self, property: str) -> Value:
        '''
        Returns the value of a particular property as a string using
        the GET request.
        '''
        value = get_request(self.__credentials, "message/property", params={"id": self.id, "name": property})
        return Value(value)

    def set_value (self, property: str, value: Value) -> bool:
        '''
        Sets the value of a property to a specific value and returns
        a flag whether it was updated correctly.
        '''
        response = post_request(self.__credentials, "message/property", params={"id": self.id, "name": property, "value": value})
        return response != None
    
    def register (self) -> bool:
        '''
        Registers a particular message to be tracked by the database system
        within the simulation to be pulled from later.
        '''
        response = post_request(self.__credentials, "message/register", params={"id": self.id})
        return response != None
    
    def get_properties (self) -> list:
        '''
        Returns a list of all properties that can be updated or read
        from this message.
        '''
        data = get_request(self.__credentials, "message/properties", params={"id": self.id})
        if data == None: return []
        return data.replace('"', "")[1:-1].split(",")
    
    def __str__(self) -> str:
        '''
        Returns the ID of the message that is stored within the database.
        This ID is unique per message.
        '''
        return self.id
    
    def request_values (self, property: str) -> dict:
        '''
        Requests a series of a specific parameter from the message that was
        stored in a database and is identitified by the time it was entered
        in the database at.
        '''
        value = post_request(self.__credentials, "message/request", params={"id": self.id, "name": property})
        if value == None: return {}
        data = value.replace('{', '{"').replace(':', '": ').replace(',', ', "').replace(' ', '')
        try: return json.loads(data)
        except: return {}
    
    def request_values_vector3 (self, property: str) -> dict:
        '''
        Requests a series of a specific parameter from the message that was
        stored in a database and is identitified by the time it was entered
        in the database at. This will convert the data into a vector3 tuple
        format.
        '''
        values: dict = self.request_values(property)
        if values == {}: return {}
        out: dict = {}
        for v in values.keys():
            out[v] = (values[v]["X"], values[v]["Y"], values[v]["Z"])
        return out