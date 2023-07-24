'''
        [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems
to aid with communication to the public API.
'''

from .request_helper import *
from .message import Message
from .value import Value
from .credentials import Credentials

'''
The component class is able to handle updating data on
the component and handling calling any data.
'''
class Component:

    # Stores the ID of the component
    id: str = None

    # Stores the crendetials for the message
    __credentials: Credentials = None

 
    def __init__(self, credentials: Credentials, id: str) -> None:
        '''
        Defines the constructor for the component that
        sets the ID of the component
        '''
        self.__credentials = credentials
        self.id = id
  
    def get_value (self, property: str) -> Value:
        '''
        Returns the value of a particular property as a string using
        the GET request.
        '''
        value = get_request(self.__credentials, "component/property", params={"id": self.id, "name": property})
        return Value(value)
    
    def get_message (self, message: str) -> Message:
        '''
        Returns the message as an GUID from the simulation as a parameter
        from the component passed.
        '''
        id = get_request(self.__credentials, "component/message", params={"id": self.id, "name": message})
        return Message(self.__credentials, id)

    def set_value (self, property: str, value: Value) -> bool:
        '''
        Sets the value of a property to a specific value and returns
        a flag whether it was updated correctly.
        '''
        response = post_request(self.__credentials, "component/property", params={"id": self.id, "name": property, "value": value})
        return response != None
    
    def set_messsage (self, property: str, msg: Message) -> bool:
        '''
        Sets the value of a message in a component to a specific message
        based on the ID of the message.
        '''
        response = post_request(self.__credentials, "component/message", params={"id": self.id, "name": property, "value": msg.id})
        return response != None
    
    def add_component (self, type_name: str):
        '''
        Adds a component to the current component as a child
        and returns the ID of the component if it is valid.
        By default it will use a Class library.
        '''
        if "NominalSystems" not in type_name:
            type_name = "NominalSystems.Classes." + type_name
        
        id = post_request(self.__credentials, "simulation/add_component", params={"type": type_name, "parent": self.id})
        if id != None:
            return Component(self.__credentials, id)
        return None
        
    def get_properties (self) -> list:
        '''
        Returns a list of all properties that can be updated or read
        from this component
        '''
        data = get_request(self.__credentials, "component/properties", params={"id": self.id})
        if data == None: return []
        return data.replace('"', "")[1:-1].split(",")
    
    def __str__(self) -> str:
        '''
        Returns the ID of the component that is stored within the database.
        This ID is unique per component.
        '''
        return self.id