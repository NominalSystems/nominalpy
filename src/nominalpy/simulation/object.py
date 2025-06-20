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

    __instances: dict[str:Instance] = {}
    """Defines all instances that have been connected to the object, by ID."""

    __children: list[Object] = []
    """Defines all children objects that are attached to the object."""

    __behaviours: list[Behaviour] = []
    """Defines all behaviours that are attached to the object."""

    __models: dict[str:Model] = {}
    """Defines all models that are attached to the object, by type."""

    __messages: dict[str:Message] = {}
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
        object = Object(
            instance._context, instance.get_id(), instance._Instance__type, None
        )
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
                    f"Successfully created child behaviour of type '{await behaviour.get_type()}' in the background."
                )

        # Loop through the children
        for id in await self.get("Children"):
            if id not in self.__instances:
                child = Object(self._context, id, parent=self)
                self.__instances[id] = child
                self.__children.append(child)
                printer.log(
                    f"Successfully created child object of type '{await child.get_type()}' in the background."
                )

        # Loop through the models
        for id in await self.get("Models"):
            if id not in self.__instances:
                model = Model(self._context, id, None, parent=self)
                self.__instances[id] = model
                self.__models[await model.get_type()] = model
                printer.log(
                    f"Successfully created model of type '{await model.get_type()}' in the background."
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

    def find_instance_with_id(self, id: str, recurse: bool = False) -> Instance:
        """
        Returns the instance that is attached to the object with the specified ID. If the
        instance does not exist, None will be returned.

        :param id:  The ID of the instance to fetch
        :type id:   str
        :param recurse:  Whether to look down the chain of children to find the instance
        :type recurse:   bool

        :returns:   The instance that is attached to the object with the specified ID
        :rtype:     Instance
        """

        # Start by looking at the instances for the ID
        if id in self.__instances:
            return self.__instances[id]

        # If recurse is enabled, look down the chain of children
        if recurse:
            for child in self.__children:
                result = child.find_instance_with_id(id, recurse)
                if result:
                    return result
            for behaviour in self.__behaviours:
                result = behaviour.find_instance_with_id(id)
                if result:
                    return result
            for model in self.__models.values():
                result = model.find_instance_with_id(id)
                if result:
                    return result

        # Return None if the instance is not found
        return None

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
        function_library: Instance = await self._context.get_function_library()
        if function_library is None:
            raise NominalException("Failed to get function library for the simulation.")

        # Invoke the function library to create the object
        child_id: str = await function_library.invoke("AddObject", type, self.get_id())

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(child_id):
            raise NominalException(f"Failed to create child object of type '{type}'.")

        # Create the object and add it to the array
        child: Object = self.__register_child(child_id, type)
        if child is None:
            raise NominalException(f"Failed to create child object of type '{type}'.")

        # If there are any kwargs, set them on the child object
        if len(kwargs) > 0:
            await child.set(**kwargs)

        # Regsiter the child object with the ID
        return child

    def __register_child(self, id: str, type: str = "") -> Object:
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
            raise IndexError(f"Failed to get child object at index: {index}.")
        return self.__children[index]

    def get_children(self) -> list[Object]:
        """
        Returns all of the children objects that are attached to the object.

        :returns:   All of the children objects that are attached to the object
        :rtype:     list[Object]
        """

        return self.__children

    def get_children_with_type(self, type: str) -> list[Object]:
        """
        Returns all of the children objects that are attached to the object of the specified
        type. If the type is not found, an empty list will be returned.

        :param type:    The type of the children objects to fetch
        :type type:     str

        :returns:       All of the children objects that are attached to the object of the specified type
        :rtype:         list[Object]
        """

        # Check the type and validate it
        type = helper.validate_type(type)

        # Filter the children by type
        return [child for child in self.__children if child._Instance__type == type]

    def get_child_with_id(self, id: str, recurse: bool = True) -> Object:
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
            if child.get_id() == id:
                return child

        # If recurse is enabled, look down the chain of instances
        if recurse:
            for child in self.__children:
                result = child.get_child_with_id(id, recurse)
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
        function_library: Instance = await self._context.get_function_library()
        if function_library is None:
            raise NominalException("Failed to get function library for the simulation.")

        # Invoke the function library to create the behaviour
        behaviour_id: str = await function_library.invoke(
            "AddBehaviour", type, self.get_id()
        )

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(behaviour_id):
            raise NominalException(
                f"Failed to create child behaviour of type '{type}'."
            )

        # Create the behaviour and add it to the array
        behaviour: Behaviour = self.__register_behaviour(behaviour_id, type)
        if behaviour is None:
            raise NominalException(
                f"Failed to create child behaviour of type '{type}'."
            )

        # If there are any kwargs, set them on the child behaviour
        if len(kwargs) > 0:
            await behaviour.set(**kwargs)

        # Regsiter the child behaviour with the ID
        return behaviour

    def __register_behaviour(self, id: str, type: str = "") -> Behaviour:
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
            raise IndexError(f"Failed to get behaviour at index: {index}.")
        return self.__behaviours[index]

    def get_behaviours(self) -> list[Behaviour]:
        """
        Returns all of the behaviours that are attached to the object.

        :returns:   All of the behaviours that are attached to the object
        :rtype:     list[Behaviour]
        """

        return self.__behaviours

    def get_behaviours_with_type(self, type: str) -> list[Behaviour]:
        """
        Returns all of the behaviours that are attached to the object of the specified type.
        If the type is not found, an empty list will be returned.

        :param type:    The type of the behaviours to fetch
        :type type:     str

        :returns:       All of the behaviours that are attached to the object of the specified type
        :rtype:         list[Behaviour]
        """

        # Check the type and validate it
        type = helper.validate_type(type)

        # Filter the children by type
        return [
            behaviour
            for behaviour in self.__behaviours
            if behaviour._Instance__type == type
        ]

    def get_behaviour_with_id(self, id: str, recurse: bool = True) -> Behaviour:
        """
        Returns the behaviour that is attached to the object with the specified ID. If the
        behaviour does not exist, None will be returned. This will also look down the chain
        of children to find the behaviour, if specified.

        :param id:  The ID of the behaviour to fetch
        :type id:   str
        :param recurse:  Whether to look down the chain of children to find the behaviour
        :type recurse:   bool

        :returns:   The behaviour that is attached to the object with the specified ID
        :rtype:     Behaviour
        """

        # Start by looking at the behaviours for the ID
        for behaviour in self.__behaviours:
            if behaviour.get_id() == id:
                return behaviour

        # If recurse is enabled, look down the chain of children
        if recurse:
            for child in self.__children:
                result = child.get_behaviour_with_id(id, recurse)
                if result:
                    return result

        # Return None if the behaviour is not found
        return None

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
            f"{self.get_id()}/ivk", ["GetModel", type], id=self._context.get_id()
        )
        if not helper.is_valid_guid(id):
            raise NominalException(f"Failed to create model of type '{type}'.")

        # Create the model with the ID
        model = self.__register_model(id, type)

        # Set the data if it exists
        if len(kwargs) > 0:
            await model.set(**kwargs)
        return model

    def __register_model(self, id: str, type: str = "") -> Model:
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
        model = Model(self._context, id, type, parent=self)
        self.__models[type] = model
        self.__instances[id] = model

        # Print the success message
        printer.success(f"Successfully created model of type '{type}'.")
        return model

    def get_models(self) -> list[Model]:
        """
        Returns all of the models that are attached to the object.

        :returns:   All of the models that are attached to the object
        :rtype:     list[Model]
        """

        return list(self.__models.values())

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
        self.__instances[message_id] = message

        # Return the message of that name
        printer.success(f"Successfully created message with name '{name}'.")
        return message

    async def get_messages(self) -> list[Message]:
        """
        Returns all of the messages that are attached to the object. This will only include the
        messages that have currently been fetched.

        :returns:   All of the messages that are attached to the object
        :rtype:     list[Message]
        """

        # Fetch all values on the object
        data: dict = await self.get_all()

        # If any data starts with 'Out_', then it is a message
        for key in data.keys():
            if str(key).startswith("Out_"):
                await self.get_message(key)
            if str(key).startswith("In_"):
                if helper.is_valid_guid(data[key]):
                    await self.get_message(key)

        # Return all the messages
        return self.__messages.values()
