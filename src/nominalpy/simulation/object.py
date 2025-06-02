#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

from __future__ import annotations
from ..utils import printer, NominalException, helper
from .instance import Instance
from .behaviour import Behaviour
from .model import Model
from .message import Message
from .context import Context


class Object(Instance):
    """
    The Object class is able to define an instance that can exist within the simulation.
    An object will have a 3D representation within the simulation and can have behaviours
    and models attached to it. Objects can also have children objects attached to them.
    Objects will always have a position and rotation within the simulation and are the main
    structure for simulation object.
    """

    __instances: dict = {}
    """Defines all instances that have been connected to the object, by ID."""

    __children: list = []
    """Defines all children objects that are attached to the object."""

    __behaviours: list = []
    """Defines all behaviours that are attached to the object."""

    __models: dict = {}
    """Defines all models that are attached to the object, by type."""

    __messages: dict = {}
    """Defines all messages that are attached to the object, by name."""

    __parent: Object = None
    """Defines the parent object that the object is attached to."""

    def __init__(
        self, context: Context, id: str, type: str = None, parent: Object = None
    ) -> None:
        """
        Initialises the object with the context and the ID of the object.

        :param context:         The context of the object
        :type context:          Context
        :param id:              The GUID ID of the object
        :type id:               str
        :param type:            The type of the system, if applicable
        :type type:             str
        :param parent:          The parent object that the object is attached to, if applicable
        :type parent:           Object
        """

        super().__init__(context, id, type)

        # Clear and reset the data
        self.__instances = {}
        self.__children = []
        self.__behaviours = []
        self.__models = {}
        self.__messages = {}
        self.__parent = parent

    @classmethod
    def from_instance(cls, instance: Instance) -> Object:
        """
        Converts the instance object to an object object.

        :param instance:    The instance object to convert
        :type instance:     Instance

        :returns:           The object object that was created
        :rtype:             Object
        """

        # Create the object and set the data
        object = Object(instance._context, instance.id, instance.get_type(), None)
        object.__dict__ = instance.__dict__
        object._Instance__data = instance._Instance__data
        object._refresh_cache = instance._refresh_cache

        # Return the object
        return object

    async def _get_data(self) -> None:
        """
        Overrides the base class method to fetch the data from the API and store it in the
        object. This is used to ensure that the data is fetched correctly and is up to date.
        Additionally, this function will also fetch all the children, behaviours, models and
        messages that are attached to the object.
        """

        # Fetch the base data
        if not self._refresh_cache:
            return
        await super()._get_data()

        # Loop through the behaviours
        for id in await self.get("Behaviours"):
            if id not in self.__instances:
                behaviour = Behaviour(self._context, id, parent=self)
                self.__instances[id] = behaviour
                self.__behaviours.append(behaviour)
                printer.log(
                    f"Successfully created child behaviour of type '{behaviour.get_type()}' in the background."
                )

        # Loop through the children
        for id in await self.get("Children"):
            if id not in self.__instances:
                child = Object(self._context, id, parent=self)
                self.__instances[id] = child
                self.__children.append(child)
                printer.log(
                    f"Successfully created child object of type '{child.get_type()}' in the background."
                )

        # Loop through the models
        for id in await self.get("Models"):
            if id not in self.__instances:
                model = Model(self._context, id, None, target=self)
                self.__instances[id] = model
                self.__models[model.get_type()] = model
                printer.log(
                    f"Successfully created model of type '{model.get_type()}' in the background."
                )

    def _require_refresh(self) -> None:
        """
        Overrides the base class method to set the flag for refreshing the cache to true.
        This will ensure that all sub-objects will also require a refresh.
        """

        # Ensure all sub-objects require a refresh too
        for _, instance in self.__instances.items():
            instance._require_refresh()
        super()._require_refresh()

    def get_parent(self) -> Object:
        """
        Returns the parent object that the object is attached to, if it exists.

        :returns:   The parent object that the object is attached to
        :rtype:     Object
        """

        return self.__parent

    def get_instance_by_id(self, id: str) -> Instance:
        """
        Returns the instance that is attached to the object with the specified ID. If the
        instance does not exist, None will be returned.

        :param id:  The ID of the instance to fetch
        :type id:   str

        :returns:   The instance that is attached to the object with the specified ID
        :rtype:     Instance
        """

        if id not in self.__instances:
            return None
        return self.__instances[id]

    async def add_child(self, type: str, **kwargs) -> Object:
        """
        Adds a child object to the object with the specified type. The child object will
        be created and attached to the object and will be returned to the user.

        :param type:    The type of the child object to create
        :type type:     str
        :param kwargs:  Optional additional data to set on the child object when created
        :type kwargs:   dict

        :returns:       The child object that was created
        :rtype:         Object
        """

        # Check the type and validate it
        type = helper.validate_type(type)

        # Get the function library
        function_library = await self._context.get_function_library()
        if function_library is None:
            raise NominalException("Failed to get function library for the simulation.")

        # Invoke the function library to create the object
        child_id: str = await function_library.invoke("AddObject", type, self.id)

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(child_id):
            raise NominalException(f"Failed to create child object of type '{type}'.")

        # Create the object and add it to the array
        child: Object = self.__register_child_with_id(child_id, type)
        if child is None:
            raise NominalException(f"Failed to create child object of type '{type}'.")

        # If there are any kwargs, set them on the child object
        if len(kwargs) > 0:
            await child.set(**kwargs)

        # Regsiter the child object with the ID
        return child

    def __register_child_with_id(self, id: str, type: str = "") -> Object:
        """
        Registers a child object to the object with the specified ID. The child object will
        be created and attached to the object and will be returned to the user.

        :param id:  The ID of the child object to create
        :type id:   str
        :param type:    The type of the child object to create
        :type type:     str

        :returns:   The child object that was created
        :rtype:     Object
        """

        # Create the object
        object = Object(self._context, id, type, parent=self)
        object.__type = type
        self.__children.append(object)
        self.__instances[id] = object

        # Print the success message
        printer.success(f"Successfully created child object of type '{type}'.")
        return object

    def get_child(self, index: int) -> Object:
        """
        Returns the child object at the specified index. If the index is invalid, an
        exception will be raised.

        :param index:   The index of the child object to fetch
        :type index:    int

        :returns:       The child object at the specified index
        :rtype:         Object
        """

        # Fetch the child and perform a safety check
        if index < 0 or index >= len(self.__children):
            raise NominalException("Invalid index provided to get child object.")
        return self.__children[index]

    def get_children(self) -> list:
        """
        Returns all of the children objects that are attached to the object.

        :returns:   All of the children objects that are attached to the object
        :rtype:     list
        """

        return self.__children

    def get_children_of_type(self, type: str) -> list:
        """
        Returns all of the children objects that are attached to the object of the specified
        type. If the type is not found, an empty list will be returned.

        :param type:    The type of the children objects to fetch
        :type type:     str

        :returns:       All of the children objects that are attached to the object of the specified type
        :rtype:         list
        """

        # Check the type and validate it
        type = helper.validate_type(type)

        # Filter the children by type
        return [child for child in self.__children if child.get_type() == type]

    def get_child_by_id(self, id: str, recurse: bool = True) -> Object:
        """
        Returns the child object that is attached to the object with the specified ID. If the
        child object does not exist, None will be returned. This will also look down the chain
        of instances to find the child object, if specified.

        :param id:  The ID of the child object to fetch
        :type id:   str
        :param recurse:  Whether to look down the chain of instances to find the child object
        :type recurse:   bool

        :returns:   The child object that is attached to the object with the specified ID
        :rtype:     Object
        """

        # Start by looking at the children for the ID
        for child in self.__children:
            if child.id == id:
                return child

        # If recurse is enabled, look down the chain of instances
        if recurse:
            for child in self.__children:
                result = child.get_child_by_id(id, recurse)
                if result:
                    return result

        # Return None if the child object is not found
        return None

    async def add_behaviour(self, type: str, **kwargs) -> Behaviour:
        """
        Adds a behaviour to the object with the specified type. The behaviour will be created
        and attached to the object and will be returned to the user.

        :param type:    The type of the behaviour to create
        :type type:     str
        :param kwargs:  Optional additional data to set on the behaviour when created
        :type kwargs:   dict

        :returns:       The behaviour that was created
        :rtype:         Behaviour
        """

        # Check the type and validate it
        type = helper.validate_type(type)

        # Get the function library
        function_library = await self._context.get_function_library()
        if function_library is None:
            raise NominalException("Failed to get function library for the simulation.")

        # Invoke the function library to create the behaviour
        behaviour_id: str = await function_library.invoke("AddBehaviour", type, self.id)

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(behaviour_id):
            raise NominalException(
                f"Failed to create child behaviour of type '{type}'."
            )

        # Create the behaviour and add it to the array
        behaviour: Behaviour = self.__register_behaviour_with_id(behaviour_id, type)
        if behaviour is None:
            raise NominalException(
                f"Failed to create child behaviour of type '{type}'."
            )

        # If there are any kwargs, set them on the child behaviour
        if len(kwargs) > 0:
            await behaviour.set(**kwargs)

        # Regsiter the child behaviour with the ID
        return behaviour

    def __register_behaviour_with_id(self, id: str, type: str = "") -> Behaviour:
        """
        Registers a child behaviour to the object with the specified ID. The child behaviour will
        be created and attached to the behaviour and will be returned to the user.

        :param id:  The ID of the child behaviour to create
        :type id:   str
        :param type:    The type of the child behaviour to create
        :type type:     str

        :returns:   The child behaviour that was created
        :rtype:     Object
        """

        # Create the behaviour
        behaviour = Behaviour(self._context, id, type, parent=self)
        behaviour.__type = type
        self.__behaviours.append(behaviour)
        self.__instances[id] = behaviour

        # Print the success message
        printer.success(f"Successfully created child behaviour of type '{type}'.")
        return behaviour

    def get_behaviour(self, index: int) -> Behaviour:
        """
        Gets the behaviour at the specified index. If the index is invalid, an exception
        will be raised.

        :param index:   The index of the behaviour to fetch
        :type index:    int

        :returns:       The behaviour at the specified index
        :rtype:         Behaviour
        """

        # Fetch the child and perform a safety check
        if index < 0 or index >= len(self.__behaviours):
            raise NominalException("Invalid index provided to get behaviour.")
        return self.__behaviours[index]

    def get_behaviours(self) -> list:
        """
        Returns all of the behaviours that are attached to the object.

        :returns:   All of the behaviours that are attached to the object
        :rtype:     list
        """

        return self.__behaviours

    def get_behaviours_of_type(self, type: str) -> list:
        """
        Returns all of the behaviours that are attached to the object of the specified type.
        If the type is not found, an empty list will be returned.

        :param type:    The type of the behaviours to fetch
        :type type:     str

        :returns:       All of the behaviours that are attached to the object of the specified type
        :rtype:         list
        """

        # Check the type and validate it
        type = helper.validate_type(type)

        # Filter the children by type
        return [
            behaviour for behaviour in self.__behaviours if behaviour.get_type() == type
        ]

    async def get_model(self, type: str, **kwargs) -> Model:
        """
        Attempts to get the model of the specified type that is attached to the object. If the
        model does not exist, it will be created and attached to the object. If the model cannot
        be created, an exception will be raised.

        :param type:    The type of the model to fetch
        :type type:     str
        :param kwargs:  The additional data to add to the model
        :type kwargs:   dict

        :returns:       The model of the specified type that is attached to the object
        :rtype:         Model
        """

        # Check the type and validate it
        type = helper.validate_type(type)

        # For each of the kwargs, serialize the data
        for key in kwargs:
            kwargs[key] = helper.serialize(kwargs[key])

        # Check to see if the model exists
        if type in self.__models.keys():
            model: Model = self.__models[type]
            if len(kwargs) > 0:
                await model.set(**kwargs)
            return model

        # Attempt to find or create the model
        id: str = await self._context.get_client().post(
            f"{self.id}/ivk", ["GetModel", type]
        )
        if not helper.is_valid_guid(id):
            raise NominalException(f"Failed to create model of type '{type}'.")

        # Create the model with the ID
        model = self.__register_model_with_id(id, type)

        # Set the data if it exists
        if len(kwargs) > 0:
            await model.set(**kwargs)
        return model

    def __register_model_with_id(self, id: str, type: str = "") -> Model:
        """
        Registers a model to the object with the specified ID. The modelr will
        be created and attached to the object and will be returned to the user.

        :param id:      The ID of the model to create
        :type id:       str
        :param type:    The type of the model to create
        :type type:     str

        :returns:   The model that was created
        :rtype:     Object
        """

        # Create the model with the ID
        model = Model(self._context, id, type, self)
        self.__models[type] = model
        self.__instances[id] = model

        # Print the success message
        printer.success(f"Successfully created model of type '{type}'.")
        return model

    def get_models(self) -> list:
        """
        Returns all of the models that are attached to the object.

        :returns:   All of the models that are attached to the object
        :rtype:     list
        """

        return self.__models.values()

    async def get_message(self, name: str) -> Message:
        """
        Attempts to get the message with the specified name that is attached to the object. If the
        message does not exist, it will be created and attached to the object. If the message cannot
        be created, an exception will be raised.

        :param name:    The name of the message to fetch
        :type name:     str

        :returns:       The message with the specified name that is attached to the object
        :rtype:         Message
        """

        # Check if the name is within the message structure and return that
        if name in self.__messages.keys():
            return self.__messages[name]

        # Fetch the data
        message_id: str = await self.get(name)
        if not helper.is_valid_guid(message_id):
            raise NominalException(f"Failed to find message with name '{name}'.")

        # Create the message object with the ID
        message = Message(self._context, message_id)
        self.__messages[name] = message
        self.__instances[id] = message

        # Return the message of that name
        printer.success(f"Successfully created message with name '{name}'.")
        return message

    def get_messages(self) -> list:
        """
        Returns all of the messages that are attached to the object. This will only include the
        messages that have currently been fetched.

        :returns:   All of the messages that are attached to the object
        :rtype:     list
        """

        # Fetch all values on the object
        data: dict = self.get_all()

        # If any data starts with 'Out_', then it is a message
        for key in data.keys():
            if str(key).startswith("Out_"):
                self.get_message(key)

        # Return all the messages
        return self.__messages.values()
