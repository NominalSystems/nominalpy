#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

from ..connection import Credentials, helper, http
from ..utils import printer, NominalException
from .message import Message
from .object import Object


class Component (Object):
    '''
    The Component class is a base object that can be attached to the
    simulation or to other objects within the simulation. Components 
    have messages that can store data.
    '''

    __messages: dict = {}
    '''Defines a list of messages associated with a particular property for easy fetching'''

    __models: dict = {}
    '''Defines a list of component models associated with a particular name for easy fetching'''

    __children: list = []
    '''Defines a list of all child components that have been added to this particular object'''

    def __init__ (self, credentials: Credentials, id: str) -> None:
        '''
        Initialises the component with a set of credentials and a
        unique GUID identifier for the object.

        :param credentials: The Credentials object that is used for the API
        :type credentials:  Credentials
        :param id:          The unique identifier for the Entity in a GUID format
        :type id:           str
        '''

        self.__messages = {}
        self.__models = {}
        self.__children = []

        super().__init__(credentials, id)

    def _require_update (self) -> None:
        '''
        This method will ensure that all data cached on the object
        require a new update when fetched. This will also ensure any
        cached messages require an update too.
        '''

        # Force all child components to get an update
        super()._require_update()
        for msg in self.__messages.values():
            msg._require_update()
        for model in self.__models.values():
            model._require_update()
    
    def get_model (self, type: str, **kwargs) -> Object:
        '''
        Attempts to add or return a component model from the current
        component based on the type of the object it should be. If the
        component model exists, the model will be attached to the object
        and tracked correctly. This can also take some optional arguments
        that will initialise the model with some starting parameters.

        :param type:    The full namespace and type of the model to add / get
        :type type:     str
        :param kwargs:  Additional parameters to intialise on the simulation model
        :type kwargs:   dict

        :returns:       A component model if it exists in the cache or added to the object
        :rtype:         Object
        '''

        # Sanitise the type
        if "NominalSystems.Classes" not in type:
            type = "NominalSystems.Classes." + type
        
        # Attempts to find the model if it exists
        if type.lower() in self.__models.keys():
            return self.__models[type.lower()]
       
        # Construct the JSON body
        body: dict = {
            "Type": type,
            "Owner": self.id
        }

        # If there are keyword arguments
        if len(kwargs) == 0:
            kwargs["IsEnabled"] = True
        body["Data"] = helper.serialize(kwargs)

        # Create the data
        request_data: str = helper.jsonify(body, True)

        # Create the response from the PUT request and get the IDs
        response = http.put_request(self._credentials, "objects", data=request_data)
        printer.log("Attempted to fetch component model of type '%s'." % type)

        # Skip on empty list
        if len(response) == 0: return None

        # Check the GUID and return a new component with that ID or a None component
        guid: str = response[0]
        if helper.is_valid_guid(guid):
            printer.success("Component model of type '%s' added." % type)
            obj: Object = Object(self._credentials, guid)
            self.__models[type.lower()] = obj
            return obj
        
        # Throw an error if no object or valid ID
        raise NominalException("Could not add component model of type '%s'." % type)
    
    def get_message (self, name: str) -> Message:
        '''
        Returns a message with a particular name, if it exists, on
        the object. If the message does not exist, it will return
        a None object. The message is a wrapper for data stored on
        components.

        :param name:    The name of the message as a parameter on the component
        :type name:     str

        :returns:       The message reference that exists from the message in the parameter
        :rtype:         Message
        '''

        # Check if the message exists
        if name.lower() in self.__messages.keys():
            return self.__messages[name.lower()]

        # Fetch the ID from the message and create the message object
        id: str = self.get_value(name)
        msg: Message = Message(self._credentials, id)
        
        # Add the message to the array for caching
        self.__messages[name.lower()] = msg
        return msg

    def invoke (self, method: str, *args: list) -> str:
        '''
        Attempts to invoke a public method that exists on the object.
        This passes in some parameters of some types and is able to
        invoke a particular method. If the method does not exist or
        the parameters do not match, then an error will be thrown.

        :param method:  The name of the method to invoke on the object
        :type method:   str
        :param args:    A list of arguments that are in a JSON format
        :type args:     list

        :returns:       The JSON value from the result of the message
        :rtype:         str
        '''
        
        # Construct the JSON body
        body: dict = {
            "ID": self.id,
            "Method": method,
            "Params": [helper.serialize_object(arg) for arg in args]
        }
        
        # Create the data
        request_data: str = helper.jsonify(body)

        # Create the response from the PATCH request and get the IDs
        response = http.post_request(self._credentials, "method", data=request_data)
        
        # Update the flag for needing to get values
        self._require_update()
        return response

    def get_child (self, index: int) -> Object:
        '''
        Attempts to fetch a child that has been added to this
        class based on the index of the child that was added.
        If the index is out of range, then a None object will
        be returned.

        :param index:   The integer index of the child that is stored
        :type index:    int

        :returns:       The component reference if it exists
        :rtype:         Component
        '''

        # Check if the index is out of range
        if index >= len(self.__children):
            raise NominalException(f"Invalid index '{index}' when getting a child from component.")
        
        # Return the child
        return self.__children[index]
    
    def get_children (self, type: str) -> list:
        '''
        Attempts to fetch the list of children that have
        been added to this component that match the specific
        type specified. If there are no children that match,
        then an empty array will be returned.

        :param type:    The Nominal type of the object to search for
        :type type:     str

        :returns:       A list of all children objects that match the type
        :rtype:         list
        '''

        # Construct the list
        children: list = []

        # Filter the type
        type = type.split(".")[-1]

        # Check for matching type
        for child in self.__children:
            c_type: str = child.get_type().split(".")[-1]
            if c_type == type:
                children.append(child)

        # Return the list
        return children
