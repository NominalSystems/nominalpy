#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2023.

from ..connection import Credentials


class Entity:
    '''
    The Entity class contains some basic parameters for storing the public
    API credentials of the current session along with a unqique identifier
    for this entity. It has not functionality and is inherited from a number
    of actual simulation objects.
    '''

    id: str = None
    '''Defines the unique GUID identifier of the object. This needs to be in the correct GUID format.'''

    _credentials: Credentials = None
    '''Specifies the credentials for accessing the API correctly.'''

    def __init__ (self, credentials: Credentials, id: str):
        '''
        Basic constructor for the Entity class, initialising the credentials and 
        the identifier.

        :param credentials: The Credentials object that is used for the API
        :type credentials:  Credentials
        :param id:          The unique identifier for the Entity in a GUID format
        :type id:           str
        '''
        
        self.id = id
        self._credentials = credentials