#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

from __future__ import annotations
import os, json
import pandas as pd
from .instance import Instance
from .message import Message
from .object import Object
from .behaviour import Behaviour
from .context import Context
from .model import Model
from .system import System
from ..connection import Client
from ..utils import NominalException, printer, helper, types
from ..data import SimulationData


# Define the systems used for extra functionality
TRACKING_SYSTEM = "NominalSystems.Universe.TrackingSystem"
EXTENSION_SYSTEM = "NominalSystems.Universe.ExtensionSystem"
SOLAR_SYSTEM = "NominalSystems.Universe.SolarSystem"


class Simulation(Context):
    """
    The Simulation class is the root object that is used to interact with the simulation.
    This can be used to create objects, behaviours, systems and messages within the simulation.
    Additionally, it can be used to track objects, query objects and save and load the state
    of the simulation. A simulation requires a client to be able to access the API. These
    clients are used to authenticate the user and ensure that the simulation is accessible.
    """

    __client: Client = None
    """Defines the client that is used to access the API."""

    __id: str = None
    """Defines the ID of the simulation. This is used to identify the simulation within the API."""

    __url: str = None
    """Defines the URL of the simulation. This is used to identify the simulation within the API."""

    __objects: list[Object] = []
    """Defines all objects that are created within the simulation, with the simulation root."""

    __behaviours: list[Behaviour] = []
    """Defines all behaviours that are created within the simulation, with the simulation root."""

    __systems: dict[str:System] = {}
    """Defines all systems that are created within the simulation, with the simulation root."""

    __messages: list[Message] = []
    """Defines all messages that are created within the simulation, with the simulation root."""

    __planets: dict[str:Object] = {}
    """Defines all planets that are created within the simulation, with the simulation root."""

    __time: float = 0.0
    """Defines the current time of the simulation."""

    __ticked: bool = False
    """Defines whether the simulation has been ticked or not."""

    def __init__(self, client: Client, id: str) -> None:
        """
        Initialises the simulation with the client and the ID of the simulation. If the ID is
        not provided, a new simulation will be created. If the reset flag is set to true, the simulation
        will be disposed and cleaned before initialising.

        :param client:          The client to access the API
        :type client:           Client
        :param id:              The ID of the simulation that exists
        :type id:               str
        """

        # Store a reference to the client
        self.__client: Client = client

        # If the client is are bad, throw an exception
        if not self.__client:
            raise NominalException(
                "Failed to create a simulation due to invalid client."
            )

        # Configure the root object
        self.__id = id

        # If the ID is not valid, throw an exception
        if not helper.is_valid_guid(self.__id):
            raise NominalException(
                "Failed to create a simulation due to invalid simulation ID."
            )

        # Reset the objects and systems
        self.__reset()

    @classmethod
    async def create(cls, client: Client) -> Simulation:
        """
        Creates a new simulation with the specified client. This will create a new simulation
        session with the API and return the simulation that has been created. If the client is
        invalid, an exception will be raised.

        :param client:          The client to access the API
        :type client:           Client

        :returns:               The simulation that has been created
        :rtype:                 Simulation
        """

        # Create a new simulation and return it
        id: str = await client.post("new", "NominalSystems.Simulation")
        sim: Simulation = Simulation(client, id=id)
        return sim

    @classmethod
    async def list(cls, client: Client) -> list[Simulation]:
        """
        Lists all the simulations that are currently running. This will return a list of
        simulations that are currently running and their IDs. If the client is invalid, an
        exception will be raised.

        :param client:          The client to access the API
        :type client:           Client

        :returns:               The list of simulations that are currently running
        :rtype:                 list[Simulation]
        """

        # Get the list of simulations from the API
        result = await client.get("")
        return [Simulation(client, id) for id in result]

    async def dispose(self) -> None:
        """
        Disposes of the simulation. This will dispose of the simulation and clear all objects,
        behaviours, systems and messages that have been created within the simulation. The
        simulation can no longer be used after this has been called.
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Dispose of the simulation and reset the state
        await self.__client.delete(f"{self.__id}")
        self.__reset()
        self.__id = None
        self.__client = None

    @classmethod
    async def dispose_all(cls, client: Client) -> None:
        """
        Disposes of all simulations that are currently running. This will dispose of all simulations
        and clear all objects, behaviours, systems and messages that have been created within the
        simulations. The simulations can no longer be used after this has been called.

        :param client:          The client to access the API
        :type client:           Client
        """

        # Dispose of all simulations
        simulations: list[Simulation] = await cls.list(client)
        for sim in simulations:
            await sim.dispose()

    def get_id(self) -> str:
        """
        Returns the ID of the simulation. This is used to identify the simulation within the API.

        :returns:   The ID of the simulation
        :rtype:     str
        """

        # Return the ID of the simulation, which should have been set by the API
        return self.__id

    def is_valid(self) -> bool:
        """
        Returns whether the simulation is valid or not. This will check if the simulation ID is
        valid and if the client is valid. If the simulation ID is not valid, an exception will be raised.

        :returns:   Whether the simulation is valid or not
        :rtype:     bool
        """

        # Check if the simulation ID is valid
        return (
            self.__id != None
            and helper.is_valid_guid(self.__id)
            and self.__client != None
        )

    def __require_refresh(self) -> None:
        """
        Ensures that the simulation requires a refresh. This will ensure that all objects, behaviours,
        systems and messages will also require a refresh.
        """

        # Ensure all sub-objects require a refresh too
        for object in self.__objects:
            object._require_refresh()
        for behaviour in self.__behaviours:
            behaviour._require_refresh()
        for system in self.__systems.values():
            system._require_refresh()
        for message in self.__messages:
            message._require_refresh()
        for planet in self.__planets.values():
            planet._require_refresh()

    def __find_instance(self, id: str) -> Instance:
        """
        Attempts to find the instance with the specified ID within the simulation. This will
        search through all objects, behaviours, systems and messages to find the instance. If
        the instance is not found, None will be returned.

        :param id:      The ID of the instance to find
        :type id:       str

        :returns:       The instance with the specified ID
        :rtype:         Instance
        """

        for object in self.__objects:
            if object.id == id:
                return object
            find: Instance = object.get_instance_by_id(id)
            if find != None:
                return find
        for behaviour in self.__behaviours:
            if behaviour.id == id:
                return behaviour
        for system in self.__systems.values():
            if system.id == id:
                return system
        for message in self.__messages:
            if message.id == id:
                return message
        return None

    async def add_object(self, type: str, **kwargs) -> Object:
        """
        Adds an object to the simulation with the specified type and data. This will create
        an object within the simulation and return the object that has been created. If the
        object cannot be created, an exception will be raised. This will add the object to the
        root of the simulation. An object will always have a position and orientation in the
        simulation.

        :param type:    The type of the object to create
        :type type:     str
        :param kwargs:  The optional data to set on the object
        :type kwargs:   dict

        :returns:       The object that has been created
        :rtype:         Object
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type)

        # Create the Object ID
        object_id: str = await self.__client.post(
            f"{self.__id}/ivk", ["AddObject", type]
        )

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(object_id):
            raise NominalException(f"Failed to create object of type '{type}'.")

        # Create the object and add it to the array
        object: Object = Object(self, object_id, type=type)
        self.__objects.append(object)

        # Set the data if the kwargs exist
        if len(kwargs) > 0:
            await object.set(**kwargs)

        # Print the success message
        printer.success(f"Successfully created object of type '{type}'.")

        # Return the object
        return object

    def get_object_by_id(self, id: str) -> Object:
        """
        Attempts to find an object in the simulation with a specified ID. This will look through all objects
        that exist and will attempt to find one that has been created. If the object does not exist, it will
        create a Python object with the ID and, provided it exists in the simulation already, the data will
        be fetched when used.

        :param id:  The ID of the object to create
        :type id:   str

        :returns:   The object that has been found or newly created.
        :rtype:     Object
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(id):
            raise NominalException(
                "Failed to create a object from an ID as the guid was incorrect."
            )

        # Validate if any of the current objects have the same ID
        for obj in self.__objects:
            if obj.id == id:
                return obj

            # Check children
            obj: Object = obj.get_child_by_id(id)
            if obj != None:
                return obj

        # Create the object and add it to the array
        obj = Object(self, id)
        self.__objects.append(obj)

        # Print the success message
        printer.success(f"Successfully created object with ID '{id}'.")
        return obj

    def get_objects(self, recurse: bool = True) -> list[Object]:
        """
        Returns all the objects that have been created within the simulation. This will return
        all the objects that have been created within the simulation. This will return the objects
        as a list. If the recurse flag is set to true, all children of the objects will be returned
        as well.

        :param recurse:     Whether to return all children of the objects
        :type recurse:      bool

        :returns:           The objects that have been created within the simulation
        :rtype:             list
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # If the recurse flag is set to true, return all objects
        if recurse:
            objects: list = []
            for obj in self.__objects:
                objects.append(obj)
                objects.extend(obj.get_children())
            return objects

        # Otherwise, return the objects
        return self.__objects

    async def add_behaviour(self, type: str, **kwargs) -> Behaviour:
        """
        Adds a behaviour to the simulation with the specified type and data. This will create
        a behaviour within the simulation and return the behaviour that has been created. If the
        behaviour cannot be created, an exception will be raised. This will add the behaviour to
        the root of the simulation. A behaviour is a type of object that can be attached to other
        objects to provide additional functionality, but has no physical representation.

        :param type:    The type of the behaviour to create
        :type type:     str
        :param kwargs:  The optional data to set on the behaviour
        :type kwargs:   dict

        :returns:       The behaviour that has been created
        :rtype:         Behaviour
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type)

        # Create the behaviour ID
        behaviour_id: str = await self.__client.post(
            f"{self.__id}/ivk", ["AddObject", type]
        )

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(behaviour_id):
            raise NominalException(f"Failed to create behaviour of type '{type}'.")

        # Create the behaviour and add it to the array
        behaviour: Behaviour = Behaviour(self, behaviour_id, type=type, parent=None)
        self.__behaviours.append(behaviour)

        # Set the data if the kwargs exist
        if len(kwargs) > 0:
            await behaviour.set(**kwargs)

        # Print the success message
        printer.success(f"Successfully created behaviour of type '{type}'.")

        # Return the behaviour
        return behaviour

    async def get_system(self, type: str, **kwargs) -> System:
        """
        Attempts to get the system with the specified type within the simulation. If the system
        does not exist, it will be created with the specified type and data. If the system cannot
        be created, an exception will be raised. This will add the system to the root of the simulation.

        :param type:    The type of the system to get or create
        :type type:     str
        :param kwargs:  The optional data to set on the system
        :type kwargs:   dict

        :returns:       The system with the specified type
        :rtype:         System
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type)

        # Check if the system exists and return it
        if type in self.__systems:
            system: System = self.__systems[type]

            # Update the values if there are any
            if len(kwargs) > 0:
                await system.set(**kwargs)
            return system

        # Attempt to find the object of type
        id: str = await self.__client.post(
            f"{self.__id}/ivk", ["FindObjectWithType", type]
        )
        if not helper.is_valid_guid(id):

            # Attempt to create the system
            id = await self.__client.post(f"{self.__id}/ivk", ["AddObject", type])

            # If the ID is not valid, raise an exception
            if not helper.is_valid_guid(id):
                raise NominalException(f"Failed to create system of type '{type}'.")

        # Create the system object from the ID
        system: System = System(self, id, type=type)
        self.__systems[type] = system

        # Print the success message
        printer.success(f"Successfully created system of type '{type}'.")
        return system

    async def add_message(self, type: str, **kwargs) -> Message:
        """
        Creates a message within the simulation with the specified type and data. This will create
        a message within the simulation and return the message that has been created. If the message
        cannot be created, an exception will be raised. This will add the message to the root of the
        simulation. A message is a type of object that can be used to communicate between objects and
        systems within the simulation.

        :param type:    The type of the message to create
        :type type:     str
        :param kwargs:  The optional data to set on the message
        :type kwargs:   dict

        :returns:       The message that has been created
        :rtype:         Message
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type)

        # Create the message ID
        message_id: str = await self.__client.post(
            f"{self.__id}/ivk", ["AddObject", type]
        )

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(message_id):
            raise NominalException(f"Failed to create message of type '{type}'.")

        # Create the message and add it to the array
        message: Message = Message(self, message_id, type=type)
        self.__messages.append(message)

        # Set the data if the kwargs exist
        if len(kwargs) > 0:
            await message.set(**kwargs)

        # Print the success message
        printer.success(f"Successfully created message of type '{type}'.")

        # Return the message
        return message

    def add_message_by_id(self, id: str) -> Message:
        """
        Adds a message to the simulation with the specified ID. This will create a message within
        the simulation and return the message that has been created. If the message cannot be created,
        an exception will be raised. This will add the message to the root of the simulation.

        :param id:  The ID of the message to create
        :type id:   str

        :returns:   The message that has been created
        :rtype:     Message
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(id):
            raise NominalException(
                "Failed to create a message from an ID as the guid was incorrect."
            )

        # Create the message and add it to the array
        message = Message(self, self.__c, id)
        self.__messages.append(message)

        # Print the success message
        printer.success(f"Successfully created message with ID '{id}'.")
        return message

    async def find_instance_of_type(self, type: str) -> Instance:
        """
        Searches for an instance of the specified type within the simulation. If the instance
        does not exist, it will be created and returned. If the instance cannot be created, None
        will be returned. This will search through all objects, behaviours, systems and messages
        within the simulation to find the instance.

        :param type:    The type of the instance to find
        :type type:     str

        :returns:       The instance of the specified type
        :rtype:         Instance
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type)

        # Create the request to the function
        id: str = await self.__client.post(
            f"{self.__id}/ivk", ["FindObjectWithType", type]
        )

        # If the result is not a valid GUID, return None
        if not helper.is_valid_guid(id):
            return None

        # Otherwise, check if the instance is already in the list
        instance: Instance = self.__find_instance(id)
        if instance != None:
            return instance

        # Otherwise, create the instance and return it
        return Instance(self, id, type)

    async def find_instances_of_type(self, type: str) -> list:
        """
        Finds all instances of the specified type within the simulation. This will search through
        all objects, behaviours, systems and messages within the simulation to find the instances.
        If the instances do not exist, an empty list will be returned.

        :param type:    The type of the instances to find
        :type type:     str

        :returns:       The instances of the specified type
        :rtype:         list
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type)

        # Create the request to the function
        result = await self.__client.post(
            f"{self.__id}/ivk", ["FindObjectsWithType", type]
        )

        # If the result is not a list or is empty, return a missing list
        if not isinstance(result, list) or len(result) == 0:
            return []

        # Loop through the list
        instances: list = []
        for i in range(len(result)):
            instance: Instance = self.__find_instance(result[i])
            if instance != None:
                instances.append(instance)
            else:
                instances.append(Instance(self, result[i], type))

        # Return the list
        return instances

    async def find_instance_with_id(self, id: str) -> Instance:
        """
        Searches for an instance of the specified ID within the simulation. If the instance
        does not exist, it will not be created. If the instance cannot be created, None
        will be returned. This will search through all objects, behaviours, systems and messages
        within the simulation to find the instance.

        :param id:    The ID of the instance to find
        :type id:     str

        :returns:       The instance of the specified ID
        :rtype:         Instance
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # See if the ID already exists in the local mapping
        if not helper.is_valid_guid(id):
            raise NominalException(
                "Failed to find a instance with an ID as the guid was incorrect."
            )

        # If the ID is already in the list, return it
        instance: Instance = self.__find_instance(id)
        if instance != None:
            return instance

        # Create the request to the function
        result_id: str = await self.__client.post(
            f"{self.__id}/ivk", ["FindObjectWithID", id]
        )

        # If the result is not a valid GUID, return None
        if not helper.is_valid_guid(result_id):
            return None

        # Otherwise, create the instance and return it
        return Instance(self, result_id)

    def get_root_objects(self) -> list[Object]:
        """
        Returns all the root objects that have been created within the simulation. This will
        return all the objects that have been created directly within the simulation and not
        part of any other object. This will return the objects as a list.

        :returns:   The root objects that have been created within the simulation
        :rtype:     list
        """

        return self.__objects

    def get_root_behaviours(self) -> list[Behaviour]:
        """
        Returns all the root behaviours that have been created within the simulation. This will
        return all the behaviours that have been created directly within the simulation and not
        part of any other object. This will return the behaviours as a list.

        :returns:   The root behaviours that have been created within the simulation
        :rtype:     list
        """

        return self.__behaviours

    def get_systems(self) -> list[System]:
        """
        Returns all the systems that have been created within the simulation. This will return
        all the systems that have been created within the simulation. This will return the systems
        as a list.

        :returns:   The systems that have been created within the simulation
        :rtype:     list
        """

        return list(self.__systems.values())

    async def get_time(self) -> float:
        """
        Returns the current time of the simulation. This will fetch the time from the API
        and return the time as a floating point number.

        :returns:   The current time of the simulation in seconds
        :rtype:     float
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # If the time is not zero, return the time
        if self.__time > 0:
            return self.__time

        # Get the extension system and grab the time
        system: System = await self.get_system(EXTENSION_SYSTEM)
        self.__time = float(await system.invoke("GetSimulationTime"))

        # Return the time
        return self.__time

    def __reset(self) -> None:
        """
        Resets the simulation. This will reset the simulation and clear all objects, behaviours,
        systems and messages that have been created within the simulation. This will also reset
        the time of the simulation to zero.
        """

        # Reset the objects and systems
        self.__objects = []
        self.__behaviours = []
        self.__systems = {}
        self.__messages = []
        self.__planets = {}
        self.__time = 0.0
        self.__ticked = False

    async def tick(self, step: float = 1e-1) -> None:
        """
        Ticks the simulation by the specified amount of time. This will invoke the tick function
        on the simulation and update the time by the specified amount. If the step is not provided,
        the default step of 0.1 seconds will be used.

        :param step:    The amount of time to tick the simulation by in seconds
        :type step:     float
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Tick the simulation by the specified amount of time
        await self.tick_duration(step, step)

    async def tick_duration(self, time: float, step: float = 1e-1) -> None:
        """
        Ticks the simulation by the specified amount of time. This will invoke the tick function
        on the simulation and update the time by the specified amount. If the step is not provided,
        the default step of 0.1 seconds will be used.

        :param time:    The totalamount of time to tick the simulation by in seconds
        :type time:     float
        :param step:    The time-step of the tick, used for physics calculations in seconds
        :type step:     float
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Get the extension system
        system: System = await self.get_system(EXTENSION_SYSTEM)

        # If the simulation has not been ticked yet, call a tick with 0.0 to initialise the tracking data
        if not self.__ticked:
            await system.invoke("InitializeSimulation")
            self.__ticked = True

        # Calculate the number of steps to take
        iterations = int(time / step)

        # While there are steps remaining, tick
        while iterations > 0:

            # Tick the iterations and get the amount of iterations completed
            result = await system.invoke("TickIterations", iterations, step)
            iterations -= result

            # Update the time
            self.__time += result * step

        # Ensure the refresh is required
        self.__require_refresh()

    async def get_state(self) -> dict:
        """
        Returns the state of the simulation. This will fetch the state from the API and return
        the state as a dictionary.

        :returns:   The state of the simulation
        :rtype:     dict
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Get the extension system
        system: System = await self.get_system(EXTENSION_SYSTEM)

        # Get the state of the simulation
        return await system.invoke("GetState")

    async def save_state(self, path: str) -> None:
        """
        Saves the state of the simulation to the specified path. This will save the state of the
        simulation to the path as a JSON file. If the path does not exist, an exception will be raised.

        :param path:    The path to save the state of the simulation to
        :type path:     str
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Get the state of the simulation
        state: dict = await self.get_state()

        # Save the state to the path
        with open(path, "w") as file:
            json.dump(state, file)

    async def set_state(self, state: dict, cache_all: bool = False) -> bool:
        """
        Sets the state of the simulation to the specified state. This will set the state of the
        simulation to the state provided and return whether the state was set successfully. This
        must be in a valid JSON dictionary form. If the cache_all flag is set to true, all objects
        in the simulation will be cached and pulled from the API, which may take some time.

        :param state:       The state to set the simulation to
        :type state:        dict
        :param cache_all:   Whether to cache all objects in the simulation.
        :type cache_all:    bool

        :returns:       Whether the state was set successfully
        :rtype:         bool
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Clear the current state
        await self.__reset()

        # Get the extension system
        system: System = await self.get_system(EXTENSION_SYSTEM)

        # Load the state of the simulation
        success: bool = await system.invoke("SetState", state)
        if not success:
            return False

        # Only do the following if the cache is required
        if cache_all:

            # Get the extension system
            system: System = await self.get_system(EXTENSION_SYSTEM)

            # Fetch all root objects using 'GetRootObjects'
            objects: list = await system.invoke("GetRootObjects", helper.empty_guid())
            for id in objects:
                if helper.is_valid_guid(id):

                    # Create the root object
                    obj: Object = Object(self, id)
                    self.__objects.append(obj)

                    # Register it properly
                    await self.__load_object(obj)

            # Fetch all root behaviours
            behaviours: list = await system.invoke(
                "GetRootBehaviours", helper.empty_guid()
            )
            for id in behaviours:
                if helper.is_valid_guid(id):

                    # Create the root behaviour
                    beh: Behaviour = Behaviour(self, id, parent=None)
                    beh.get_messages()
                    self.__behaviours.append(beh)

        # Ensure the refresh is required
        self.__require_refresh()

        # Return the success
        return True

    async def __load_object(self, parent: Object) -> None:
        """
        Loads the object and its children from the API. This will load the object,
        all its children, and all behaviours in the simulation.

        :param parent:  The parent object to load the children from
        :type parent:   Object
        """

        # If the object is missing, skip
        if parent == None:
            return

        # Get the extension system
        system: System = self.get_system(EXTENSION_SYSTEM)

        # Fetch all children objects using 'GetRootObjects'
        children: list = system.invoke("GetRootObjects", parent.id)
        for id in children:
            if helper.is_valid_guid(id):
                obj: Object = parent._Object__register_child_with_id(id)
                self.__load_object(obj)

        # Fetch all behaviours
        behaviours: list = system.invoke("GetRootBehaviours", parent.id)
        for id in behaviours:
            if helper.is_valid_guid(id):
                behaviour: Behaviour = parent._Object__register_behaviour_with_id(id)
                behaviour.get_messages()

        # Fetch all models
        models: list = parent.invoke("GetModels")
        for id in models:
            if helper.is_valid_guid(id):
                model: Model = parent._Object__register_model_with_id(id)
                model.get_messages()

        # Cache all messages and load them into memory
        parent.get_messages()

    async def load_state(self, path: str, cache_all: bool = False) -> bool:
        """
        Loads the state of the simulation from the specified path. This will load the state of the
        simulation from the path as a JSON file and return whether the state was loaded successfully.
        If the path does not exist, an exception will be raised. If the cache_all flag is set to true,
        all objects in the simulation will be cached and pulled from the API, which may take some time.

        :param path:        The path to load the state of the simulation from
        :type path:         str
        :param cache_all:   Whether to cache all objects in the simulation.
        :type cache_all:    bool

        :returns:       Whether the state was loaded successfully
        :rtype:         bool
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Check if the path exists
        if not os.path.exists(path):
            raise NominalException(f"Path '{path}' does not exist.")

        # Load the state from the path
        with open(path, "r") as file:
            state: dict = json.load(file)
            return await self.set_state(state, cache_all)

    async def track_object(self, instance: Instance, isAdvanced: bool = False) -> None:
        """
        Starts tracking the object within the simulation. This will start tracking the object
        which will store the object's data and state every specified tick in a local database.
        This can be used to retrieve the object's data at a later time.

        :param instance:    The instance to track within the simulation
        :type instance:     Instance
        :param isAdvanced:  Whether the advanced variables are also being tracked
        :type isAdvanced:   bool
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Get the tracking system
        system: System = await self.get_system(TRACKING_SYSTEM)

        # Check if the ID is a string and a valid GUID, as the GUID could be passed in
        # to the function instead.
        if type(instance) is str and helper.is_valid_guid(instance):
            await system.invoke("TrackObject", instance, isAdvanced)
        elif isinstance(instance, Instance):
            await system.invoke("TrackObject", instance.id, isAdvanced)
        else:
            raise NominalException(
                "Failed to track object as the instance was not a valid type."
            )

    async def set_tracking_interval(self, interval: float) -> None:
        """
        Updates the tracking interval for all the objects that have been tracked. This will
        be an interval in simulation seconds and will be the same across all objects. The
        default value is 10.0 seconds.

        :param interval:    The interval to track the objects by in seconds
        :type interval:     float
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Get the tracking system
        system: System = await self.get_system(TRACKING_SYSTEM)

        # Invoke the set track interval
        await system.set(Interval=interval)

    async def query_object(self, instance: Instance) -> SimulationData:
        """
        Queries the object within the simulation. This will query the object and return the data
        that has been stored for the object. This will return the data as a data frame. If there
        is no data for the object, or if the object has not yet been tracked, an empty data frame
        will be returned. Due to the API having a maximum limit of data, this will also fetch the
        data in pages before pre-compiling the data into a single data frame.

        :param instance:    The instance to query within the simulation
        :type instance:     Instance

        :returns:           The data that has been stored for the object
        :rtype:             DataFrame
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Get the tracking system
        system: System = await self.get_system(TRACKING_SYSTEM)

        # Store the total data and the current page being called
        data: dict = {}
        page_count: int = 1
        page: int = 0

        # Loop through all pages (which is at least 1)
        while page < page_count:

            # Get the instance ID, based on whether it is an instance or a string
            id: str = instance.id if isinstance(instance, Instance) else instance

            # Invoke the query object on the API, with the current page
            page_data: dict = await system.invoke("ExportToAPI", id, page)
            if page_data == None:
                return None

            # If the first page, then store the page data including the metadata
            if page == 0:
                data = page_data

            # Otherwise, simply extend the data from the next pages
            else:
                data["Data"].extend(page_data["Data"])

            # Update the page count
            # Handle the case where the page count is not present in the page data
            if "Count" not in page_data:
                raise NominalException(
                    "No data can be retrieved for this query. Make sure the data was subscribed to."
                )
            page_count = page_data["Count"]
            page += 1

        # Remove the page information as it is not needed
        del data["Page"]
        del data["Count"]

        # Create and return the data frame
        return SimulationData(data)

    async def get_planet(self, name: str) -> Object:
        """
        Returns the planet with the specified name within the simulation. This will return the
        planet object that has been created within the simulation. If the planet does not exist,
        it will be created and returned. If the planet cannot be created, None will be returned.

        :param name:    The name of the planet to get or create
        :type name:     str

        :returns:       The planet with the specified name
        :rtype:         Object
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Check if the planet already exists
        if name.lower() in self.__planets:
            return self.__planets[name.lower()]

        # Fetch the solar system
        system: System = await self.get_system(SOLAR_SYSTEM)

        # Grab the planet by invoking the method
        id = await system.invoke("GetBody", name)
        if not helper.is_valid_guid(id):
            return None

        # Construct the object
        object: Object = Object(self, id, types.CELESTIAL_BODY)
        self.__planets[name.lower()] = object
        self.__objects.append(object)

        # Return the object
        return object

    async def query_dataframe(self, instance: Instance) -> pd.DataFrame:
        """
        Queries the object within the simulation. This will query the object and return the data
        that has been stored for the object. This will return the data as a data frame. If there
        is no data for the object, or if the object has not yet been tracked, an empty data frame
        will be returned.

        :param instance:    The instance to query within the simulation
        :type instance:     Instance

        :returns:           The data that has been stored for the object
        :rtype:             DataFrame
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        # Create and return the data frame
        return (await self.query_object(instance=instance)).to_dataframe()

    async def get_function_library(self) -> Instance:
        """
        Returns the function library for the simulation. This will return the function library
        that is used to access the API and authenticate the user.

        :returns:   The function library for the simulation
        :rtype:     Instance
        """

        # Throw exception if the simulation is not valid
        if not self.is_valid():
            raise NominalException(
                "Failed to call function on an invalid or deleted simulation."
            )

        return await self.get_system(EXTENSION_SYSTEM)

    def get_client(self) -> Client:
        """
        Returns the client for the simulation. This will return the client that are
        used to access the API and authenticate the user.

        :returns:   The client for the simulation
        :rtype:     Client
        """
        return self.__client

    '''
    @classmethod
    def get_sessions(cls, credentials: Credentials) -> dict:
        """
        Returns the active sessions that are currently running on the API for the user's
        credentials. This will return a list of session IDs that are currently active. If
        there are no active sessions, an empty list will be returned.

        :param credentials:     The credentials to access the API
        :type credentials:      Credentials

        :returns:   The dictionary of sessions and whether they are active or not
        :rtype:     dict
        """

        # Get the sessions from the API and throw an error if there are no sessions
        result: list = http_requests.get(credentials, "session")
        sessions: dict = {}
        for r in result:
            sessions[r["guid"]] = r["status"] == "RUNNING"
        return sessions

    @classmethod
    def create_session(cls, credentials: Credentials) -> str:
        """
        Attempts to create a new session with the public API. This will create a new session
        with the API and return the session ID. If the session cannot be created, an exception
        will be raised.

        :param credentials:     The credentials to access the API
        :type credentials:      Credentials

        :returns:   The session ID of the new session
        :rtype:     str
        """

        # Output information about creating a sessiojn
        printer.warning(
            "Attempting to create a new session with your API key. This may take up to a minute."
        )

        # Create a new session from the API
        data = {"version": credentials.version, "duration": 7200}
        response = http_requests.post(credentials, "session", data=data)

        # Check if there was no session, throw an error with the message
        if "guid" not in response:
            raise NominalException(
                "Failed to create session. Message: %s" % str(response)
            )

        # Return the session
        return response["guid"]

    @classmethod
    def get(
        cls, credentials: Credentials, index: int = 0, reset: bool = True
    ) -> Simulation:
        """
        This will attempt to create a simulation that is connected to the current session. If
        the session does not exist, a new session will be created. Assuming that the simulation
        is not running locally, it will use your access key to fetch the most recent simulation
        or attempt to create one. Optionally, an index can be set to define which session to use.
        If the index does not exist, it will attempt to create it.

        :param credentials:     The credentials to access the API
        :type credentials:      Credentials
        :param index:           The index of the session to use
        :type index:            int
        :param reset:           Whether to reset the simulation before initialising
        :type reset:            bool

        :returns:   The simulation that has been created
        :rtype:     Simulation
        """

        # If the credentials are bad, throw an exception
        if not credentials:
            raise NominalException(
                "Invalid Credentials: No credentials passed into the Simulation."
            )
        if not credentials.is_valid():
            raise NominalException(
                "Invalid Credentials: The credentials are missing information."
            )

        # Check for local credentials and return a local simulation
        if credentials.is_local:
            simulation: Simulation = Simulation(credentials, "localhost")
            if reset:
                simulation.reset()
            return simulation

        # Fetch the sessions
        sessions: dict = Simulation.get_sessions(credentials)

        # If no sessions, create a new one
        if sessions == None or len(sessions) <= index:
            session = Simulation.create_session(credentials)
            return Simulation(credentials, session_id=session)

        # Otherwise, get the first active session found
        else:
            active_sessions: str = [s for s in sessions.keys() if sessions[s]]
            if len(active_sessions) <= index:
                session = list(sessions.keys())[index]
            else:
                session = active_sessions[index]

            # Create the simulation and reset it if the parameter is passed through
            simulation: Simulation = Simulation(credentials, session_id=session)
            if reset:
                simulation.reset()
            return simulation

            '''
