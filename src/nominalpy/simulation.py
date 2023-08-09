'''
        [ NOMINAL SYSTEMS ]
TODO
'''

from .object import Object
from .request_helper import *
from .component import Component
from .credentials import Credentials
from .message import Message
from .system import System
from .printer import *


class Simulation:

    '''
    Specifies the credentials for accessing the API
    correctly.
    '''
    __credentials: Credentials = None

    
    def __init__(self, credentials: Credentials, reset: bool = True) -> None:
        '''
        Default constructor for the simulation handler which takes 
        in the credentials to access the API. The reset flag will attempt
        to reset the simulation when initialised by default.
        '''
        self.__credentials = credentials
        if self.__credentials == None:
            raise NominalException("Invalid Credentials: No credentials passed into the Simulation.")
        
        # Attempt a simple request
        if not self.__credentials.is_local:
            validate_credentials(self.__credentials)

        # Reset the simulation if valid credentials
        if reset and self.__credentials != None:
            pass
            #self.reset()



    def add_object (self, type: str, owner: Object = None, **kwargs) -> Object:
        '''
        Attempts to add a new object to the simulation. This object
        can be added to an owner, if the owning object is passed in,
        or it can be added to the simulation as the base type. Additionally,
        initialisation parameters can be passed in to set on create
        with the keyword arguments. If the object is invalid or the type
        is incorrect, a None object will be returned. Otherwise, an object
        will be initialised with the ID from the call.
        '''

        # Sanitise the type
        if "NominalSystems" not in type:
            if "." not in type:
                type = "NominalSystems.Classes." + type
            else:
                type = "NominalSystems." + type
       
        # Construct the JSON body
        body: dict = {
            "type": type
        }
        
        # Add in owner to the body
        if owner != None and isinstance(owner, Object):
            body["owner"] = owner.id

        # If there are keyword arguments
        if len(kwargs) > 0:
            body["values"] = kwargs

        # Create the data
        request_data: str = jsonify(body)
        log("Attempting a PUT request with data: \n\t%s" % request_data)

        # Create the response from the PUT request and get the IDs
        response = put_request(self.__credentials, "objects", data=request_data)
        ids = str_to_list(response)
        log("Attempted to create %d objects with IDs: \n\t%s" % (len(ids), response))

        # Skip on empty list
        if len(ids) == 0: return None

        # Check the GUID and return a new Object with that ID or a None object
        guid: str = ids[0]
        if is_valid_guid(guid):
            success("Object of type '%s' created." % type)
            return Object(self.__credentials, guid)
        error("Could not construct object of class '%s'" % type)
        return None