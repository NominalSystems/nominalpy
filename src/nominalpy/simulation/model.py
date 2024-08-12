#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

from ..utils import printer, NominalException, helper
from ..connection import Credentials
from .instance import Instance
from .message import Message


class Model (Instance):
    '''
    The model class cannot exist in the simulation by itself, but can be used to
    attach to a simulation object. Each object can have up to 1 model of a specific
    type attach and allows for extended functionality to be added to the object.
    '''

    __target: Instance = None
    '''Defines the target object that the model is attached to.'''

    __messages: dict = {}
    '''Defines all messages that are attached to the object, by name.'''

    def __init__ (self, credentials: Credentials, id: str) -> None:
        '''
        Initialises the model with the credentials and the ID of the model.

        :param credentials:     The credentials to access the API
        :type credentials:      Credentials
        :param id:              The GUID ID of the model
        :type id:               str
        '''

        super().__init__(credentials, id)

        # Clear and reset the data
        self.__target = None
        self.__messages = {}
    
    def get_target (self) -> Instance:
        '''
        Returns the target object that the model is attached to.

        :returns:   The target object that the model is attached to
        :rtype:     Object
        '''

        return self.__target

    def _require_refresh (self) -> None:
        '''
        Overrides the base class method to set the flag for refreshing the cache to true.
        This will ensure that all messages will also require a refresh.
        '''

        # Ensure all messages require a refresh too
        for message in self.__messages.values():
            message._require_refresh()
        super()._require_refresh()
    
    def get_message (self, name: str) -> Message:
        '''
        Attempts to get the message with the specified name that is attached to the model. If the
        message does not exist, it will be created and attached to the model. If the message cannot
        be created, an exception will be raised.

        :param name:    The name of the message to fetch
        :type name:     str

        :returns:       The message with the specified name that is attached to the model
        :rtype:         Message
        '''

        # Check if the name is within the message structure and return that
        if name in self.__messages.keys():
            return self.__messages[name]
        
        # Fetch the data
        id = self.get(name)
        if not helper.is_valid_guid(id):
            raise NominalException("Failed to find message '%s'." % name)
        
        # Create the message object with the ID
        message = Message(self._credentials, id)
        self.__messages[name] = message

        # Return the message of that name
        printer.success(f"Message with name '{name}' created successfully.")
        return message

    def get_messages (self) -> list:
        '''
        Returns all of the messages that are attached to the model. This will only include the
        messages that have currently been fetched.

        :returns:   All of the messages that are attached to the model
        :rtype:     list
        '''
        
        return self.__messages.values()