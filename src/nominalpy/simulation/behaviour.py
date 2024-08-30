#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

from ..utils import printer, NominalException, helper
from ..connection import Credentials
from .instance import Instance
from .message import Message

class Behaviour (Instance):
    '''
    The Behaviour class can define an instance that can exist within the simulation.
    Behaviours can be added to both the simulation or to an object that exists. They
    have no physical representation (no position or rotation) and purely exist as a
    way to serve abstract functionality. Examples of behaviours include flight software
    and power modules.
    '''

    __parent: Instance = None
    '''Defines the parent object that the behaviour is attached to.'''

    __messages: dict = {}
    '''Defines all messages that are attached to the object, by name.'''

    def __init__ (self, credentials: Credentials, id: str) -> None:
        '''
        Initialises the behaviour with the credentials and the ID of the behaviour.

        :param credentials:     The credentials to access the API
        :type credentials:      Credentials
        :param id:              The GUID ID of the behaviour
        :type id:               str
        '''

        super().__init__(credentials, id)

        # Clear and reset any data
        self.__parent = None
        self.__messages = {}
    
    def get_parent (self) -> Instance:
        '''
        Returns the parent object that the behaviour is attached to.

        :returns:   The parent object that the behaviour is attached to
        :rtype:     Object
        '''

        return self.__parent
    
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
        Attempts to get the message with the specified name that is attached to the behaviour. If the
        message does not exist, it will be created and attached to the behaviour. If the message cannot
        be created, an exception will be raised.

        :param name:    The name of the message to fetch
        :type name:     str

        :returns:       The message with the specified name that is attached to the behaviour
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
        Returns all of the messages that are attached to the behaviour. This will only include the
        messages that have currently been fetched.

        :returns:   All of the messages that are attached to the behaviour
        :rtype:     list
        '''
        
        return self.__messages.values()