'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

The Component class is a base object that can be attached to the
simulation or to other objects within the simulation. Components 
have messages that can store data.
'''

from ..connection import Credentials
from .message import Message
from .object import Object


class Component (Object):

    '''
    Defines a list of messages associated with this component. Any
    message that is requested will be added to this list to be
    returned if requested again.
    '''
    messages: list = []

    def __init__(self, credentials: Credentials, id: str) -> None:
        '''
        Initialises the component with a set of credentials and a
        unique GUID identifier for the object.
        '''
        super().__init__(credentials, id)

    def __require_update__ (self) -> None:
        '''
        This method will ensure that all data cached on the object
        require a new update when fetched. This will also ensure any
        cached messages require an update too.
        '''
        super().__require_update__()
        for msg in self.messages:
            msg.__require_update__()
    
    def get_message (self, name: str) -> Message:
        '''
        Returns a message with a particular name, if it exists, on
        the object. If the message does not exist, it will return
        a None object. The message is a wrapper for data stored on
        components.
        '''

        # Fetch the ID from the message
        id: str = self.get_value(name)
        if id == None:
            return None
        
        # Check if the ID already has a message
        for msg in self.messages:
            if msg.id == id:
                return msg
            
        # Create a new message otherwise
        msg: Message = Message(self._credentials, id)
        
        # Add the message to the array for caching
        self.messages.append(msg)
        return msg
