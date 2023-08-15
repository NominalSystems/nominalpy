from .request_helper import *
from .credentials import Credentials
from .printer import *
from .message import Message
from .object import Object

class Component (Object):

    # TODO
    messages: list = []

    def __init__(self, credentials: Credentials, id: str) -> None:
        '''
        TODO
        '''
        super().__init__(credentials, id)

    def __require_update__ (self) -> None:
        '''
        TODO
        '''
        super().__require_update__()
        for msg in self.messages:
            msg.__require_update__()
    
    def get_message (self, name: str) -> Message:
        '''
        TODO
        '''
        id: str = self.get_value(name)
        if id == None:
            return None
        
        # Check if the ID already has a message
        for msg in self.messages:
            if msg.id == id:
                return msg
            
        # Create a new message otherwise
        msg: Message = Message(self._Object__credentials, id)
        
        # Add the message to the array for tracking
        self.messages.append(msg)
        return msg