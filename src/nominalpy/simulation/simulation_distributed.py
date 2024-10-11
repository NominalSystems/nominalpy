import asyncio
import json
import os
from typing import Dict, List, Tuple, Any
import time
from importlib.metadata import version
import pandas as pd

from .. import NominalException, Object, Instance, Behaviour, System, Message
# from .simulation import Simulation
from ..connection import Credentials, http_async
from ..data import SimulationData
from ..utils import helper, printer


# Define the systems used for extra functionality
TRACKING_SYSTEM  = "NominalSystems.Universe.TrackingSystem"
EXTENSION_SYSTEM = "NominalSystems.Universe.ExtensionSystem"
SOLAR_SYSTEM     = "NominalSystems.Universe.SolarSystem"


class Simulation:
    
    # Specifies the credentials for accessing the API correctly.
    __credentials: Credentials = None

    # Defines all objects that are created within the simulation, with the simulation root.
    __objects: list = []

    # Defines all behaviours that are created within the simulation, with the simulation root.
    __behaviours: list = []

    # Defines all systems that are created within the simulation, with the simulation root.
    __systems: dict = {}

    # Defines all messages that are created within the simulation, with the simulation root.
    __messages: list = []

    # Defines all planets that are created within the simulation, with the simulation root.
    __planets: dict = {}

    # Defines the current time of the simulation.
    __time: float = 0.0

    # Defines whether the simulation has been ticked or not.
    __ticked: bool = False

    # Defines the session ID for the current working session, stored for public API keys.
    __session_id: str = None

    def __init__(self, credentials: Credentials, session_id: str = "") -> None:
        """
        Initialises the simulation with the credentials and the ID of the simulation. If the ID is
        not provided, a new simulation will be created. If the reset flag is set to true, the simulation
        will be disposed and cleaned before initialising.

        :param credentials:     The credentials to access the API
        :type credentials:      Credentials
        :param session_id:      The session ID for the current working session
        :type session_id:       str
        """

        # Configure the root object
        self.__credentials = credentials.copy()
        self.__session_id = session_id

        # If the credentials are bad, throw an exception
        if not self.__credentials:
            raise NominalException("Invalid Credentials: No credentials passed into the Simulation.")
        if not self.__credentials.is_valid():
            raise NominalException("Invalid Credentials: The credentials are missing information.")

        # If the API is not local, then start creating a session
        if not self.__credentials.is_local:
            if self.__session_id == "" or self.__session_id is None:
                raise NominalException("Invalid Session: No session ID passed into the Simulation.")

            # Fetch if the session is active
            first: bool = True
            while True:
                sessions: dict = Simulation.get_sessions(self.__credentials)
                if self.__session_id not in sessions:
                    raise NominalException("Invalid Session: The session ID is not valid.")
                if sessions[self.__session_id]:
                    break

                # Repeat until the session is ready
                time.sleep(3.0)
                if first:
                    first = False
                    printer.warning(
                        "API session is in a pending state as the instance is starting. This may take up to 1 minute.")
                else:
                    printer.log("Waiting for session to be active...")

            # Set the session ID in the credentials
            self.__credentials.set_session_id(self.__session_id)

        # Reset the objects and systems
        self.__objects = []
        self.__behaviours = []
        self.__systems = {}
        self.__messages = []
        self.__planets = {}
        self.__time = 0.0
        self.__ticked = False

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

        for obj in self.__objects:
            if obj.id == id:
                return obj
            find: Instance = obj.get_instance_with_id(id)
            if find is not None:
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

    async def add_object(self, obj_type: str, **kwargs):
        # Check if the type is missing 'NominalSystems' and add it
        obj_type = helper.validate_type(obj_type)
        # For each of the kwargs, serialize the data
        for key in kwargs:
            kwargs[key] = helper.serialize(kwargs[key])
        # Create the request
        request = {"type": obj_type}
        if kwargs:
            request["data"] = kwargs
        # Create the object using a post request
        result = await http_async.post_async(self.__credentials, "object", request)
        # Check if the result is None
        if result is None:
            raise NominalException(f"Failed to create object of type '{obj_type}'.")
        # Create the object and add it to the array
        obj = Object(self.__credentials, result["guid"])
        self.__objects.append(obj)
        # Print the success message
        printer.success(f"Object of type '{obj_type}' created successfully.")
        return obj

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

        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type)

        # For each of the kwargs, serialize the data
        for key in kwargs:
            kwargs[key] = helper.serialize(kwargs[key])

        # Create the request
        request: dict = {"type": type}
        if len(kwargs) > 0:
            request["data"] = kwargs

        # Create the behaviour using a post request
        result = await http_async.post_async(self.__credentials, "object", request)
        if result is None:
            raise NominalException(f"Failed to create behaviour of type {type}.")

        # Create the behaviour and add it to the array
        behaviour = Behaviour(self.__credentials, result["guid"])
        self.__behaviours.append(behaviour)

        # Print the success message
        printer.success(f"Behaviour of type '{type}' created successfully.")
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

        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type)

        # For each of the kwargs, serialize the data
        for key in kwargs:
            kwargs[key] = helper.serialize(kwargs[key])

        # Check if the system exists and return it
        if type in self.__systems:
            system: System = self.__systems[type]

            # Update the values if there are any
            if len(kwargs) > 0:
                system.set(**kwargs)
            return system

        # Otherwise, check if the system already exists
        id: str = await http_async.patch_async(
            self.__credentials,
            "simulation",
            {"name": "FindObject", "args": [type]}
        )
        if not helper.is_valid_guid(id):

            # Create the request
            request = {"type": type}
            if len(kwargs) > 0:
                request["data"] = kwargs

            # Attempt to create the system
            response = await http_async.post_async(self.__credentials, "object", request)
            if response is None:
                raise NominalException(f"Failed to create system of type {type}.")
            id = response["guid"]

        # Create the system object from the ID
        system: System = System(self.__credentials, id)
        self.__systems[type] = system

        # Print the success message
        printer.success(f"System of type '{type}' created successfully.")
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

        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type, "Messages")

        # For each of the kwargs, serialize the data
        for key in kwargs:
            kwargs[key] = helper.serialize(kwargs[key])

        # Create the request
        request: dict = {"type": type}
        if len(kwargs) > 0:
            request["data"] = kwargs

        # Create the behaviour using a post request
        result = await http_async.post_async(self.__credentials, "object", request)
        if result is None:
            raise NominalException(f"Failed to create message of type {type}.")

        # Create the message and add it to the array
        message = Message(self.__credentials, result["guid"])
        self.__messages.append(message)

        # Print the success message
        printer.success(f"Message of type '{type}' created successfully.")
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

        # If the ID is not valid, raise an exception
        if not helper.is_valid_guid(id):
            raise NominalException("Failed to create a message from an ID as the guid was incorrect.")

        # Create the message and add it to the array
        message = Message(self.__credentials, id)
        self.__messages.append(message)

        # Print the success message
        printer.success(f"Message with ID '{id}' created successfully.")
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

        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type)

        # Create the request to the function
        result = await http_async.patch_async(self.__credentials, "simulation", {"name": "FindObject", "args": [type]})

        # If the result is not a valid GUID, return None
        if not helper.is_valid_guid(result):
            return None

        # Otherwise, check if the instance is already in the list
        instance: Instance = self.__find_instance(result)
        printer.debug(result)
        if instance is not None:
            return instance

        # Otherwise, create the instance and return it
        return Instance(self.__credentials, result)

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

        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type)

        # Create the request to the function
        result = await http_async.patch_async(self.__credentials, "simulation", {"name": "FindObjects", "args": [type]})

        # If the result is not a list or is empty, return a missing list
        if not isinstance(result, list) or len(result) == 0:
            return []

        # Loop through the list
        instances: list = []
        for i in range(len(result)):
            instance: Instance = self.__find_instance(result[i])
            if instance is not None:
                instances.append(instance)
            else:
                instances.append(Instance(self.__credentials, result[i]))

        # Return the list
        return instances

    async def get_time(self) -> float:
        """
        Returns the current time of the simulation. This will fetch the time from the API
        and return the time as a floating point number.

        :returns:   The current time of the simulation in seconds
        :rtype:     float
        """

        # If the time is not zero, return the time
        if self.__time > 0:
            return self.__time

        # Get the extension system and grab the time
        system: System = await self.get_system(EXTENSION_SYSTEM)
        self.__time = float(system.invoke("GetSimulationTime"))

        # Return the time
        return self.__time

    async def reset(self) -> None:
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

        # Ensure the simulation is reset
        await http_async.patch_async(self.__credentials, "simulation", {"name": "Dispose"})

    # In Simulation class
    async def tick(self, step: float = 1e-1):
        # Prepare the request payload
        # If the simulation has not been ticked yet, call a tick with 0.0 to initialise the tracking data
        if not self.__ticked:
            system: System = await self.get_system(EXTENSION_SYSTEM)
            system.invoke("InitializeSimulation")
            self.__ticked = True

        request = {"name": "TickSeconds", "args": [step]}
        result = await http_async.patch_async(self.__credentials, "simulation", request)

        # Update the time
        self.__time += step
        # Ensure the refresh is required
        self.__require_refresh()

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

        # Get the extension system
        system: System = await self.get_system(EXTENSION_SYSTEM)

        # If the simulation has not been ticked yet, call a tick with 0.0 to initialise the tracking data
        if not self.__ticked:
            system.invoke("InitializeSimulation")
            self.__ticked = True

        # Calculate the number of steps to take
        iterations = int(time / step)

        # While there are steps remaining, tick
        while iterations > 0:
            # Tick the iterations and get the amount of iterations completed
            result = system.invoke("TickIterations", iterations, step)
            iterations -= result

            # Update the time
            self.__time += result * step

        # handle any residual time that was truncated when calculating the iterations
        # TODO: create an API end point for tick duration that ticks through the iterations and residual time
        step_residual = time - self.__time
        # if there is a residual, tick the simulation by the residual time
        if step_residual > 1e-9:
            # the residual should be definition be less than a step, but we check just in case
            if step_residual > step or step_residual < 0:
                raise NominalException(f"Residual time is greater than the step size: {step_residual} > {step}")
            # tick the simulation by the residual time noting that the tick method should update the __time
            await self.tick(step_residual)

        # Ensure the refresh is required
        self.__require_refresh()

    async def get_state(self) -> dict:
        """
        Returns the state of the simulation. This will fetch the state from the API and return
        the state as a dictionary.

        :returns:   The state of the simulation
        :rtype:     dict
        """

        # Get the extension system
        system: System = await self.get_system(EXTENSION_SYSTEM)

        # Get the state of the simulation
        return system.invoke("GetState")

    async def save_state(self, path: str) -> None:
        """
        Saves the state of the simulation to the specified path. This will save the state of the
        simulation to the path as a JSON file. If the path does not exist, an exception will be raised.

        :param path:    The path to save the state of the simulation to
        :type path:     str
        """

        # Get the state of the simulation
        state: dict = await self.get_state()

        # Save the state to the path
        with open(path, 'w') as file:
            json.dump(state, file)

    async def set_state(self, state: dict) -> bool:
        """
        Sets the state of the simulation to the specified state. This will set the state of the
        simulation to the state provided and return whether the state was set successfully. This
        must be in a valid JSON dictionary form.

        :param state:   The state to set the simulation to
        :type state:    dict

        :returns:       Whether the state was set successfully
        :rtype:         bool
        """

        # Get the extension system
        system: System = await self.get_system(EXTENSION_SYSTEM)

        # Load the state of the simulation
        success: bool = system.invoke("SetState", state)

        # Ensure the refresh is required
        self.__require_refresh()

        # Return the success
        return success

    async def load_state(self, path: str) -> bool:
        """
        Loads the state of the simulation from the specified path. This will load the state of the
        simulation from the path as a JSON file and return whether the state was loaded successfully.
        If the path does not exist, an exception will be raised.

        :param path:    The path to load the state of the simulation from
        :type path:     str

        :returns:       Whether the state was loaded successfully
        :rtype:         bool
        """

        # Check if the path exists
        if not os.path.exists(path):
            raise NominalException(f"Path '{path}' does not exist.")

        # Load the state from the path
        with open(path, 'r') as file:
            state: dict = json.load(file)
            return await self.set_state(state)

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

        # Get the tracking system
        system: System = await self.get_system(TRACKING_SYSTEM)

        # Invoke the track object
        system.invoke("TrackObject", instance.id, isAdvanced)

    async def set_tracking_interval(self, interval: float) -> None:
        """
        Updates the tracking interval for all the objects that have been tracked. This will
        be an interval in simulation seconds and will be the same across all objects. The
        default value is 10.0 seconds.

        :param interval:    The interval to track the objects by in seconds
        :type interval:     float
        """

        # Get the tracking system
        system: System = await self.get_system(TRACKING_SYSTEM)

        # Invoke the set track interval
        system.set(Interval=interval)

    async def query_object(self, instance: Instance) -> SimulationData:
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

        # Get the tracking system
        system: System = await self.get_system(TRACKING_SYSTEM)

        # Invoke the query object
        data = system.invoke("ExportToJSON", instance.id)

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

        # Check if the planet already exists
        if name.lower() in self.__planets:
            return self.__planets[name.lower()]

        # Fetch the solar system
        system: System = await self.get_system(SOLAR_SYSTEM)

        # Grab the planet by invoking the method
        id = system.invoke("GetBody", name)
        if not helper.is_valid_guid(id):
            return None

        # Construct the object
        object: Object = Object(self.__credentials, id)
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
        # Create and return the data frame
        return await self.query_object(instance=instance).to_dataframe()

    def get_credentials(self) -> Credentials:
        """
        Returns the credentials for the simulation. This will return the credentials that are
        used to access the API and authenticate the user.

        :returns:   The credentials for the simulation
        :rtype:     Credentials
        """
        return self.__credentials

    @classmethod
    async def get_sessions(cls, credentials: Credentials) -> dict:
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
        result: list = await http_async.get_async(credentials, "session")
        sessions: dict = {}
        for r in result:
            sessions[r['guid']] = (r['status'] == "RUNNING")
        return sessions

    @classmethod
    async def create_session(cls, credentials: Credentials) -> str:
        """
        Creates a new session with the API for the user's credentials. This will create a new
        session and return the session ID (guid) for the session that has been created. If the
        session cannot be created, an exception will be raised.

        :param credentials:     The credentials to access the API
        :type credentials:      Credentials

        :returns:   The session ID for the session that has been created
        :rtype:     str
        """
        # Fetch the package version
        package_version = version('nominalpy')
        package_version = package_version[:package_version.rfind(".")]

        # Prepare the request payload
        data = {
            'version': package_version,
            'duration': 7200  # Session duration in seconds
        }

        # Make the asynchronous HTTP POST request using the http module
        result = await http_async.post_async(credentials, "session", data=data)

        # Check if the response contains 'guid'
        if result is None or 'guid' not in result:
            raise NominalException(f"Failed to create session. Message: {result}")

        # Return the session ID (guid)
        return result["guid"]

    @classmethod
    async def get(cls, credentials: Credentials, index: int = 0, reset: bool = True):
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
            raise NominalException("Invalid Credentials: No credentials passed into the Simulation.")
        if not credentials.is_valid():
            raise NominalException("Invalid Credentials: The credentials are missing information.")

        # Check for local credentials and return a local simulation
        if credentials.is_local:
            simulation: Simulation = Simulation(credentials, "localhost")
            if reset:
                await simulation.reset()
            return simulation

        # Fetch the sessions
        sessions: dict = await Simulation.get_sessions(credentials)

        # If no sessions, create a new one
        if sessions is None or len(sessions) <= index:
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
                await simulation.reset()
            return simulation

    @classmethod
    async def create(cls, credentials: Credentials):
        """
        Creates a new simulation with the specified credentials. This will create a new simulation
        session with the API and return the simulation that has been created. If the credentials are
        invalid, an exception will be raised.

        :param credentials:     The credentials to access the API
        :type credentials:      Credentials

        :returns:   The simulation that has been created
        :rtype:     Simulation
        """

        # If the credentials are bad, throw an exception
        if not credentials:
            raise NominalException("Invalid Credentials: No credentials passed into the Simulation.")
        if not credentials.is_valid():
            raise NominalException("Invalid Credentials: The credentials are missing information.")

        # Create a new session and return it
        session: str = await Simulation.create_session(credentials)
        return Simulation(credentials, session_id=session)


class DistributedSimulation:
    """
    Manager for distributed simulations running across multiple sessions.

    The `DistributedSimulation` class provides functionality to manage multiple
    `Simulation` instances, each associated with a unique session ID. It allows
    users to create sessions asynchronously, assign objects to specific sessions,
    and run simulations in parallel. This class is particularly useful for
    simulating large-scale systems that require distribution across multiple
    processors or nodes.

    :param credentials: Credentials for accessing the simulation API.
    :type credentials: Credentials
    """

    def __init__(self, credentials: Credentials):
        """
        Initialize the DistributedSimulation manager.

        Sets up the necessary data structures for managing multiple simulations
        and initializes the asynchronous event loop.

        :param credentials: Credentials for accessing the simulation API.
        :type credentials: Credentials
        """
        self.__credentials = credentials
        # Add the port to the local ports if the credentials are local
        self.local_ports = set()
        if credentials.is_local:
            self.local_ports.add(self._allocate_port())
        self.sessions: Dict[str, Simulation] = {}
        self.loop = asyncio.get_event_loop()

    def connect(self, host="localhost", port=8080) -> Simulation:
        """
        Connects to a simulation session.

        :returns: The `Simulation` instance.
        :rtype: Simulation
        """

        # generate a unique session id
        session_id = f"http://{host}:{port}"

        # connect to a local simulation
        simulation = Simulation(Credentials(f"http://{host}", port), session_id)

        # register simulation to session map
        self.sessions[session_id] = simulation

        # return simulation instance
        return simulation

    def _allocate_port(self) -> int:
        """
        Allocate a new port for a local simulation.

        Allocates a new port for a local simulation session and adds it to the
        set of allocated ports. This method is used internally to ensure that
        each local simulation has a unique port number.
        """
        port = self.__credentials.port
        if self.__credentials.is_local:
            while port in self.local_ports:
                port += 1
        return port

    async def create_session(self) -> Simulation:
        """
        Create a new simulation session asynchronously.

        Asynchronously creates a new session using the provided credentials and
        initializes a `Simulation` instance associated with that session. The
        new session is added to the internal sessions dictionary.

        :returns: The `Simulation` instance associated with the new session.
        :rtype: Simulation
        """
        # Create a new session ID asynchronously
        session_id = await Simulation.create_session(self.__credentials)
        # Store the simulation in the sessions dictionary
        simulation = Simulation(self.__credentials, session_id=session_id)
        # Allocate a new port if the credentials are local
        if self.__credentials.is_local:
            port = self._allocate_port()
            self.local_ports.add(port)
            # the Simulation creates a copy of the credentials, so we can safely update the simulation's port
            simulation.get_credentials().port = port
        # Store the simulation in the sessions dictionary
        self.sessions[session_id] = simulation
        return simulation

    async def create_sessions(self, count: int) -> Tuple[Any]:
        """
        Initialize multiple simulation sessions asynchronously.

        Creates the specified number of sessions concurrently and stores the
        `Simulation` instances in the sessions dictionary.

        :param count: The number of sessions to create.
        :type count: int
        """
        # Create a list of tasks for session creation
        tasks = [self.create_session() for _ in range(count)]
        # Await the completion of all session creation tasks
        simulations = await asyncio.gather(*tasks)
        return simulations

    @classmethod
    def get(cls, credentials: Credentials, count: int = 1):
        """
        Initialize the distributed simulation manager asynchronously.

        This method creates a new instance of the `DistributedSimulation` class
        and returns it to the caller. The method is asynchronous to allow for
        the creation of multiple simulation sessions concurrently.
        """
        ds = cls(credentials=credentials)
        ds.loop.run_until_complete(ds.create_sessions(count=count))
        # Create a new instance of the DistributedSimulation class
        return ds

    def add_object_to_session(self, session_id: str, obj_type: str, **kwargs):
        """
        Add an object to a specific simulation session.

        Adds an object to the specified session by running the asynchronous
        `add_object_async` method within the event loop. This method is
        synchronous from the caller's perspective but executes the object
        creation asynchronously.

        :param session_id: The ID of the session to which the object will be added.
        :type session_id: str
        :param obj_type: The type of the object to add.
        :type obj_type: str
        :param kwargs: Additional keyword arguments for object creation.
        :raises ValueError: If the specified session ID does not exist.
        :returns: The created object instance.
        """
        # Retrieve the simulation associated with the session ID
        simulation = self.sessions.get(session_id)
        if simulation:
            # Run the asynchronous add_object method in the event loop
            return self.loop.run_until_complete(simulation.add_object(obj_type, **kwargs))
        else:
            raise ValueError(f"Session {session_id} does not exist.")

    # TODO: Additional methods for managing simulations...

    def add_objects(self, obj_type: str, **kwargs) -> List[Object]:
        """
        Add an object to the sessions within the simulation.

        Adds an object to each session in the simulation by running the asynchronous
        `add_object_async` method within the event loop. This method is synchronous
        from the caller's perspective but executes the object creation asynchronously.

        :param obj_type: The type of the object to add.
        :type obj_type: str
        :param kwargs: Additional keyword arguments for object creation.
        :returns: The list of created object instances.
        :rtype: List[Object]
        """
        # Create a list of tasks for adding objects to sessions
        tasks = [ self.sessions[key].add_object(obj_type, **kwargs) for key in self.sessions ]

        # Run all object creation tasks until completion    
        return self.loop.run_until_complete(asyncio.gather(*tasks))

    # async def assign_objects(self, objects: List[Dict], strategy: str = 'round_robin'):
    #     """
    #     Assign objects to sessions based on a specified distribution strategy.
    #
    #     Distributes a list of objects across the available sessions using the
    #     specified strategy. Currently supports 'round_robin' distribution.
    #
    #     :param objects: A list of objects to assign. Each object is a dictionary
    #                     with keys 'type' and optionally 'kwargs'.
    #     :type objects: List[Dict]
    #     :param strategy: The distribution strategy to use ('round_robin' or 'custom').
    #     :type strategy: str
    #     :raises ValueError: If an unknown distribution strategy is specified.
    #     """
    #     if strategy == 'round_robin':
    #         # Get the list of session IDs
    #         session_ids = list(self.sessions.keys())
    #         # Distribute objects across sessions in a round-robin fashion
    #         for idx, obj in enumerate(objects):
    #             session_id = session_ids[idx % len(session_ids)]
    #             obj_type = obj['type']
    #             obj_kwargs = obj.get('kwargs', {})
    #             await self.add_object_to_session(session_id, obj_type, **obj_kwargs)
    #     elif strategy == 'custom':
    #         # TODO: Implement custom distribution logic here
    #         pass
    #     else:
    #         raise ValueError(f"Unknown strategy '{strategy}'.")

    def get_credentials(self) -> Credentials:
        """
        Get the credentials associated with the distributed simulation.

        :returns: The credentials used to access the simulation API.
        :rtype: Credentials
        """
        return self.__credentials

    def get_systems(self, type: str, **kwargs) -> List[System]:
        """
        Get the systems associated with the distributed simulation asynchronously.

        :param type: The type of the systems to retrieve.
        :type type: str
        :returns: The list of systems associated with the distributed simulation.
        :rtype: List[System]
        """
        # Create a list of tasks for fetching systems from each session
        tasks = [simulation.get_system(type=type, **kwargs) for simulation in self.sessions.values()]
        # Run all system retrieval tasks until completion
        return self.loop.run_until_complete(asyncio.gather(*tasks))

    def subscribe(self, message: Message):
        """

        """

        raise NotImplementedError

    def tick(self, step: float = 1e-1):
        """
        Run simulations in all sessions asynchronously.

        Initiates the execution of simulations in all sessions by running their
        `run_async` methods within the event loop. This method blocks until all
        simulations have completed.

        :param step: The time step for each simulation tick.
        :type step: float
        """
        # Create a list of tasks for running simulations asynchronously
        tasks = [simulation.tick(step=step) for simulation in self.sessions.values()]
        # Run all simulation tasks until completion
        self.loop.run_until_complete(asyncio.gather(*tasks))

    def tick_duration(self, time: float, step: float = 1e-1):
        """
        Run simulations for a specified duration asynchronously.

        Initiates the execution of simulations in all sessions for the specified
        duration by running their `run_duration_async` methods within the event loop.
        This method blocks until all simulations have completed.

        :param time: The total duration for which to run the simulations.
        :type time: float
        :param step: The time step for each simulation tick.
        :type step: float
        """
        # Create a list of tasks for running simulations asynchronously
        tasks = [simulation.tick_duration(time, step=step) for simulation in self.sessions.values()]
        # Run all simulation tasks until completion
        self.loop.run_until_complete(asyncio.gather(*tasks))

    def __getitem__(self, item):
        """
        Retrieve a simulation session by its session ID or positional index. Assume an input int is an index.

        :param item: The session ID of the simulation to retrieve.
        :type item: str, int
        :returns: The simulation associated with the specified session ID.
        :rtype: Simulation
        """
        if isinstance(item, int):
            return list(self.sessions.values())[item]
        else:
            return self.sessions[item]
