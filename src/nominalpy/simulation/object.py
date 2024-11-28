#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

from __future__ import annotations
from ..connection import Credentials, http_requests
from ..utils import printer, NominalException, helper
from .instance import Instance
from .behaviour import Behaviour
from .model import Model
from .message import Message


class Object (Instance):
    '''
    The Object class is able to define an instance that can exist within the simulation.
    An object will have a 3D representation within the simulation and can have behaviours
    and models attached to it. Objects can also have children objects attached to them.
    Objects will always have a position and rotation within the simulation and are the main
    structure for simulation object.
    '''

    __instances: dict = {}
    '''Defines all instances that have been connected to the object, by ID.'''

    __children: list = []
    '''Defines all children objects that are attached to the object.'''

    __behaviours: list = []
    '''Defines all behaviours that are attached to the object.'''

    __models: dict = {}
    '''Defines all models that are attached to the object, by type.'''

    __messages: dict = {}
    '''Defines all messages that are attached to the object, by name.'''

    __parent: Object = None
    '''Defines the parent object that the object is attached to.'''

    def __init__ (self, credentials: Credentials, id: str) -> None:
        '''
        Initialises the object with the credentials and the ID of the object.

        :param credentials:     The credentials to access the API
        :type credentials:      Credentials
        :param id:              The GUID ID of the object
        :type id:               str
        '''

        super().__init__(credentials, id)

        # Clear and reset the data
        self.__instances = {}
        self.__children = []
        self.__behaviours = []
        self.__models = {}
        self.__messages = {}
        self.__parent = None

    def _get_data (self) -> None:
        '''
        Overrides the base class method to fetch the data from the API and store it in the
        object. This is used to ensure that the data is fetched correctly and is up to date.
        Additionally, this function will also fetch all the children, behaviours, models and
        messages that are attached to the object.
        '''

        # Fetch the base data
        if not self._refresh_cache:
            return
        super()._get_data()
        
        # Loop through the behaviours
        for id in self.get("Behaviours"):
            if id not in self.__instances:
                behaviour = Behaviour(self._credentials, id)
                behaviour.__parent = self
                self.__instances[id] = behaviour
                self.__behaviours.append(behaviour)
                printer.log(f"Behaviour of type '{behaviour.get_type()}' was found and created successfully in the background.")
        
        # Loop through the children
        for id in self.get("Children"):
            if id not in self.__instances:
                child = Object(self._credentials, id)
                child.__parent = self
                self.__instances[id] = child
                self.__children.append(child)
                printer.log(f"Child object of type '{child.get_type()}' was found and created successfully in the background.")
        
        # Loop through the models
        for id in self.get("Models"):
            if id not in self.__instances:
                model = Model(self._credentials, id)
                model.__target = self
                self.__instances[id] = model
                self.__models[model.get_type()] = model
                printer.log(f"Model of type '{model.get_type()}' was found and created successfully in the background.")

    def _require_refresh (self) -> None:
        '''
        Overrides the base class method to set the flag for refreshing the cache to true.
        This will ensure that all sub-objects will also require a refresh.
        '''

        # Ensure all sub-objects require a refresh too
        for id, instance in self.__instances.items():
            instance._require_refresh()
        super()._require_refresh()

    def get_parent (self) -> Object:
        '''
        Returns the parent object that the object is attached to, if it exists.

        :returns:   The parent object that the object is attached to
        :rtype:     Object
        '''

        return self.__parent
    
    def get_instance_with_id (self, id: str) -> Instance:
        '''
        Returns the instance that is attached to the object with the specified ID. If the
        instance does not exist, None will be returned.

        :param id:  The ID of the instance to fetch
        :type id:   str

        :returns:   The instance that is attached to the object with the specified ID
        :rtype:     Instance
        '''

        if id not in self.__instances:
            return None
        return self.__instances[id]

    def add_child (self, type: str, **kwargs) -> Object:
        '''
        Adds a child object to the object with the specified type. The child object will
        be created and attached to the object and will be returned to the user.

        :param type:    The type of the child object to create
        :type type:     str
        :param kwargs:  Optional additional data to set on the child object when created
        :type kwargs:   dict

        :returns:       The child object that was created
        :rtype:         Object
        '''
            
        # Check the type and validate it
        type = helper.validate_type(type)

        # For each of the kwargs, serialize the data
        for key in kwargs:
            kwargs[key] = helper.serialize(kwargs[key])

        # Create the request
        request: dict = {"type": type, "meta": { "owner": self.id }}
        if len(kwargs) > 0:
            request["data"] = kwargs

        # Create the object using a post request
        result = http_requests.post(self._credentials, "object", request)
        if not result:
            raise NominalException("Failed to create object of type '%s'." % type)
        id: str = result["guid"]
        
        # Create the object
        object = Object(self._credentials, id)
        object.__parent = self
        self.__children.append(object)
        self.__instances[id] = object

        # Print the success message
        printer.success(f"Child object of type '{type}' created successfully.")
        return object

    def get_child (self, index: int) -> Object:
        '''
        Returns the child object at the specified index. If the index is invalid, an
        exception will be raised.

        :param index:   The index of the child object to fetch
        :type index:    int

        :returns:       The child object at the specified index
        :rtype:         Object
        '''

        # Fetch the child and perform a safety check
        if index < 0 or index >= len(self.__children):
            raise NominalException("Invalid index provided to get child object.")
        return self.__children[index]

    def get_children (self) -> list:
        '''
        Returns all of the children objects that are attached to the object.

        :returns:   All of the children objects that are attached to the object
        :rtype:     list
        '''

        return self.__children
    
    def get_children_of_type (self, type: str) -> list:
        '''
        Returns all of the children objects that are attached to the object of the specified
        type. If the type is not found, an empty list will be returned.

        :param type:    The type of the children objects to fetch
        :type type:     str

        :returns:       All of the children objects that are attached to the object of the specified type
        :rtype:         list
        '''
            
        # Check the type and validate it
        type = helper.validate_type(type)

        # Filter the children by type
        return [child for child in self.__children if child.get_type() == type]

    def add_behaviour (self, type: str, **kwargs) -> Behaviour:
        '''
        Adds a behaviour to the object with the specified type. The behaviour will be created
        and attached to the object and will be returned to the user.

        :param type:    The type of the behaviour to create
        :type type:     str
        :param kwargs:  Optional additional data to set on the behaviour when created
        :type kwargs:   dict

        :returns:       The behaviour that was created
        :rtype:         Behaviour
        '''
            
        # Check the type and validate it
        type = helper.validate_type(type)
        
        # For each of the kwargs, serialize the data
        for key in kwargs:
            kwargs[key] = helper.serialize(kwargs[key])

        # Create the request
        request: dict = {"type": type, "meta": { "owner": self.id }}
        if len(kwargs) > 0:
            request["data"] = kwargs

        # Create the behaviour using a post request
        result = http_requests.post(self._credentials, "object", request)
        if not result:
            raise NominalException("Failed to create behaviour of type '%s'." % type)
        id: str = result["guid"]
        
        # Create the behaviour
        behaviour = Behaviour(self._credentials, id)
        behaviour.__parent = self
        self.__behaviours.append(behaviour)
        self.__instances[id] = behaviour

        # Print the success message
        printer.success(f"Behaviour of type '{type}' created successfully.")
        return behaviour

    def get_behaviour (self, index: int) -> Behaviour:
        '''
        Gets the behaviour at the specified index. If the index is invalid, an exception
        will be raised.

        :param index:   The index of the behaviour to fetch
        :type index:    int

        :returns:       The behaviour at the specified index
        :rtype:         Behaviour
        '''
        
        # Fetch the child and perform a safety check
        if index < 0 or index >= len(self.__behaviours):
            raise NominalException("Invalid index provided to get behaviour.")
        return self.__behaviours[index]
    
    def get_behaviours (self) -> list:
        '''
        Returns all of the behaviours that are attached to the object.

        :returns:   All of the behaviours that are attached to the object
        :rtype:     list
        '''

        return self.__behaviours

    def get_behaviours_of_type (self, type: str) -> list:
        '''
        Returns all of the behaviours that are attached to the object of the specified type.
        If the type is not found, an empty list will be returned.

        :param type:    The type of the behaviours to fetch
        :type type:     str

        :returns:       All of the behaviours that are attached to the object of the specified type
        :rtype:         list
        '''
                
        # Check the type and validate it
        type = helper.validate_type(type)

        # Filter the children by type
        return [behaviour for behaviour in self.__behaviours if behaviour.get_type() == type]
    
    def get_model (self, type: str, **kwargs) -> Model:
        '''
        Attempts to get the model of the specified type that is attached to the object. If the
        model does not exist, it will be created and attached to the object. If the model cannot
        be created, an exception will be raised.

        :param type:    The type of the model to fetch
        :type type:     str
        :param kwargs:  The additional data to add to the model
        :type kwargs:   dict

        :returns:       The model of the specified type that is attached to the object
        :rtype:         Model
        '''

        # Check the type and validate it
        type = helper.validate_type(type)

        # For each of the kwargs, serialize the data
        for key in kwargs:
            kwargs[key] = helper.serialize(kwargs[key])

        # Check to see if the model exists
        if type in self.__models.keys():
            model: Model = self.__models[type]
            if len(kwargs) > 0:
                model.set(**kwargs)
            return model
        
        # Attempt to find or create the model
        id: str = http_requests.patch(self._credentials, "object", {"guid": self.id, "name": "GetModel", "args": [type]})
        if not helper.is_valid_guid(id):
            raise NominalException("Failed to create model of type '%s'." % type)
        
        # Create the model with the ID
        model = Model(self._credentials, id)
        model.__target = self
        self.__models[type] = model
        self.__instances[id] = model

        # Set the data if it exists
        if len(kwargs) > 0:
            model.set(**kwargs)
        
        # Print the success message
        printer.success(f"Model of type '{type}' created successfully.")
        return model

    def get_models (self) -> list:
        '''
        Returns all of the models that are attached to the object.

        :returns:   All of the models that are attached to the object
        :rtype:     list
        '''

        return self.__models.values()

    def get_message (self, name: str) -> Message:
        '''
        Attempts to get the message with the specified name that is attached to the object. If the
        message does not exist, it will be created and attached to the object. If the message cannot
        be created, an exception will be raised.

        :param name:    The name of the message to fetch
        :type name:     str

        :returns:       The message with the specified name that is attached to the object
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
        self.__instances[id] = message

        # Return the message of that name
        printer.success(f"Message with name '{name}' created successfully.")
        return message

    def get_messages (self) -> list:
        '''
        Returns all of the messages that are attached to the object. This will only include the
        messages that have currently been fetched.

        :returns:   All of the messages that are attached to the object
        :rtype:     list
        '''

        return self.__messages.values()