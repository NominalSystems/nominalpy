#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

import os, json
from .instance import Instance
from .message import Message
from .object import Object
from .behaviour import Behaviour
from .system import System
from ..connection import Credentials, http
from ..utils import NominalException, printer, helper
from ..data import DataFrame


# Define the systems used for extra functionality
TRACKING_SYSTEM  = "NominalSystems.Universe.TrackingSystem"
EXTENSION_SYSTEM = "NominalSystems.Universe.ExtensionSystem"

class Simulation ():
    '''
    The Simulation class is the root object that is used to interact with the simulation.
    This can be used to create objects, behaviours, systems and messages within the simulation.
    Additionally, it can be used to track objects, query objects and save and load the state
    of the simulation. A simulation requires credentials to be able to access the API. These
    credentials are used to authenticate the user and ensure that the simulation is accessible.
    '''
    
    __credentials: Credentials = None
    '''Specifies the credentials for accessing the API correctly.'''

    __objects: list = []
    '''Defines all objects that are created within the simulation, with the simulation root.'''

    __behaviours: list = []
    '''Defines all behaviours that are created within the simulation, with the simulation root.'''

    __systems: dict = {}
    '''Defines all systems that are created within the simulation, with the simulation root.'''
    
    __messages: list = []
    '''Defines all messages that are created within the simulation, with the simulation root.'''

    __time: float = 0.0
    '''Defines the current time of the simulation.'''

    def __init__ (self, credentials: Credentials, reset: bool = True) -> None:
        '''
        Initialises the simulation with the credentials and the ID of the simulation. If the ID is
        not provided, a new simulation will be created. If the reset flag is set to true, the simulation
        will be disposed and cleaned before initialising.

        :param credentials:     The credentials to access the API
        :type credentials:      Credentials
        :param reset:           Whether to reset the simulation or not
        :type reset:            bool
        '''

        # Configure the root object
        self.__credentials = credentials

        # If the credentials are bad, throw an exception
        if not self.__credentials:
            raise NominalException("Invalid Credentials: No credentials passed into the Simulation.")
        if not self.__credentials.is_valid():
            raise NominalException("Invalid Credentials: The credentials are missing information.")
        
        # If resetting, make sure that the simulation is disposed and cleaned
        if reset:
            http.patch(self.__credentials, "simulation", {"name": "Dispose"})

        # Reset the objects and systems
        self.__objects = []
        self.__behaviours = []
        self.__systems = {}
        self.__messages = []
        self.__time = 0.0
    
    def __require_refresh (self) -> None:
        '''
        Ensures that the simulation requires a refresh. This will ensure that all objects, behaviours,
        systems and messages will also require a refresh.
        '''

        # Ensure all sub-objects require a refresh too
        for object in self.__objects:
            object._require_refresh()
        for behaviour in self.__behaviours:
            behaviour._require_refresh()
        for system in self.__systems.values():
            system._require_refresh()
        for message in self.__messages:
            message._require_refresh()

    def __find_instance (self, id: str) -> Instance:
        '''
        Attempts to find the instance with the specified ID within the simulation. This will
        search through all objects, behaviours, systems and messages to find the instance. If
        the instance is not found, None will be returned.

        :param id:      The ID of the instance to find
        :type id:       str

        :returns:       The instance with the specified ID
        :rtype:         Instance
        '''

        for object in self.__objects:
            if object.id == id:
                return object
            find: Instance = object.get_instance_with_id(id)
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

    def add_object (self, type: str, **kwargs) -> Object:
        '''
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
        '''
        
        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type)

        # For each of the kwargs, serialize the data
        for key in kwargs:
            kwargs[key] = helper.serialize(kwargs[key])

        # Create the request
        request: dict = {"type": type}
        if len(kwargs) > 0:
            request["data"] = kwargs

        # Create the object using a post request
        result = http.post(self.__credentials, "object", request)
        if result == None:
            raise NominalException("Failed to create object of type '%s'." % type)
        
        # Create the object and add it to the array
        object = Object(self.__credentials, result["guid"])
        self.__objects.append(object)

        # Print the success message
        printer.success(f"Object of type '{type}' created successfully.")
        return object

    def add_behaviour (self, type: str, **kwargs) -> Behaviour:
        '''
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
        '''

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
        result = http.post(self.__credentials, "object", request)
        if result == None:
            raise NominalException("Failed to create behaviour of type '%s'." % type)
        
        # Create the behaviour and add it to the array
        behaviour = Behaviour(self.__credentials, result["guid"])
        self.__behaviours.append(behaviour)

        # Print the success message
        printer.success(f"Behaviour of type '{type}' created successfully.")
        return behaviour

    def get_system (self, type: str, **kwargs) -> System:
        '''
        Attempts to get the system with the specified type within the simulation. If the system
        does not exist, it will be created with the specified type and data. If the system cannot
        be created, an exception will be raised. This will add the system to the root of the simulation.

        :param type:    The type of the system to get or create
        :type type:     str
        :param kwargs:  The optional data to set on the system
        :type kwargs:   dict

        :returns:       The system with the specified type
        :rtype:         System
        '''

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
        id: str = http.patch(self.__credentials, "simulation", {"name": "FindObject", "args": [type]})
        if not helper.is_valid_guid(id):

            # Create the request
            request = {"type": type}
            if len(kwargs) > 0:
                request["data"] = kwargs
            
            # Attempt to create the system
            response = http.post(self.__credentials, "object", request)
            if response == None:
                raise NominalException("Failed to create system of type '%s'." % type)
            id = response["guid"]
        
        # Create the system object from the ID
        system: System = System(self.__credentials, id)
        self.__systems[type] = system

        # Print the success message
        printer.success(f"System of type '{type}' created successfully.")
        return system
    
    def add_message (self, type: str, **kwargs) -> Message:
        '''
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
        '''

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
        result = http.post(self.__credentials, "object", request)
        if result == None:
            raise NominalException("Failed to create message of type '%s'." % type)
        
        # Create the message and add it to the array
        message = Message(self.__credentials, result["guid"])
        self.__messages.append(message)

        # Print the success message
        printer.success(f"Message of type '{type}' created successfully.")
        return message

    def find_instance_of_type (self, type: str) -> Instance:
        '''
        Searches for an instance of the specified type within the simulation. If the instance
        does not exist, it will be created and returned. If the instance cannot be created, None
        will be returned. This will search through all objects, behaviours, systems and messages
        within the simulation to find the instance.

        :param type:    The type of the instance to find
        :type type:     str

        :returns:       The instance of the specified type
        :rtype:         Instance
        '''

        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type)

        # Create the request to the function
        result = http.patch(self.__credentials, "simulation", {"name": "FindObject", "args": [type]})

        # If the result is not a valid GUID, return None
        if not helper.is_valid_guid(result):
            return None
        
        # Otherwise, check if the instance is already in the list
        instance: Instance = self.__find_instance(result)
        printer.debug(result)
        if instance != None:
            return instance
        
        # Otherwise, create the instance and return it
        return Instance(self.__credentials, result)

    def find_instances_of_type (self, type: str) -> list:
        '''
        Finds all instances of the specified type within the simulation. This will search through
        all objects, behaviours, systems and messages within the simulation to find the instances.
        If the instances do not exist, an empty list will be returned.

        :param type:    The type of the instances to find
        :type type:     str

        :returns:       The instances of the specified type
        :rtype:         list
        '''
            
        # Check if the type is missing 'NominalSystems' and add it
        type = helper.validate_type(type)

        # Create the request to the function
        result = http.patch(self.__credentials, "simulation", {"name": "FindObjects", "args": [type]})

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
                instances.append(Instance(self.__credentials, result[i]))
        
        # Return the list
        return instances
        
    def get_time (self) -> float:
        '''
        Returns the current time of the simulation. This will fetch the time from the API
        and return the time as a floating point number.

        :returns:   The current time of the simulation in seconds
        :rtype:     float
        '''

        # If the time is not zero, return the time
        if self.__time > 0:
            return self.__time
        
        # Get the extension system and grab the time
        system: System = self.get_system(EXTENSION_SYSTEM)
        self.__time = float(system.invoke("GetSimulationTime"))

        # Return the time
        return self.__time
    
    def tick (self, step: float = 1e-1) -> None:
        '''
        Ticks the simulation by the specified amount of time. This will invoke the tick function
        on the simulation and update the time by the specified amount. If the step is not provided,
        the default step of 0.1 seconds will be used.

        :param step:    The amount of time to tick the simulation by in seconds
        :type step:     float
        '''

        # Invoke the tick function on the simulation
        http.patch(self.__credentials, "simulation", {"name": "TickSeconds", "args": [step]})

        # Update the time
        self.__time += step

        # Ensure the refresh is required
        self.__require_refresh()

    def tick_duration (self, time: float, step: float = 1e-1) -> None:
        '''
        Ticks the simulation by the specified amount of time. This will invoke the tick function
        on the simulation and update the time by the specified amount. If the step is not provided,
        the default step of 0.1 seconds will be used.

        :param time:    The totalamount of time to tick the simulation by in seconds
        :type time:     float
        :param step:    The time-step of the tick, used for physics calculations in seconds
        :type step:     float
        '''

        # Get the extension system
        system: System = self.get_system(EXTENSION_SYSTEM)

        # Calculate the number of steps to take
        iterations = int(time / step)

        # While there are steps remaining, tick
        while iterations > 0:

            # Tick the iterations and get the amount of iterations completed
            result = system.invoke("TickIterations", iterations, step)
            iterations -= result

            # Update the time
            self.__time += result * step
        
        # Ensure the refresh is required
        self.__require_refresh()

    def get_state (self) -> dict:
        '''
        Returns the state of the simulation. This will fetch the state from the API and return
        the state as a dictionary.

        :returns:   The state of the simulation
        :rtype:     dict
        '''

        # Get the extension system
        system: System = self.get_system(EXTENSION_SYSTEM)

        # Get the state of the simulation
        return system.invoke("GetState")

    def save_state (self, path: str) -> None:
        '''
        Saves the state of the simulation to the specified path. This will save the state of the
        simulation to the path as a JSON file. If the path does not exist, an exception will be raised.

        :param path:    The path to save the state of the simulation to
        :type path:     str
        '''
            
        # Get the state of the simulation
        state: dict = self.get_state()

        # Save the state to the path
        with open(path, 'w') as file:
            json.dump(state, file)
    
    def set_state (self, state: dict) -> bool:
        '''
        Sets the state of the simulation to the specified state. This will set the state of the
        simulation to the state provided and return whether the state was set successfully. This
        must be in a valid JSON dictionary form.

        :param state:   The state to set the simulation to
        :type state:    dict

        :returns:       Whether the state was set successfully
        :rtype:         bool
        '''

        # Get the extension system
        system: System = self.get_system(EXTENSION_SYSTEM)

        # Load the state of the simulation
        success: bool = system.invoke("SetState", state)

        # Ensure the refresh is required
        self.__require_refresh()

        # Return the success
        return success
    
    def load_state (self, path: str) -> bool:
        '''
        Loads the state of the simulation from the specified path. This will load the state of the
        simulation from the path as a JSON file and return whether the state was loaded successfully.
        If the path does not exist, an exception will be raised.

        :param path:    The path to load the state of the simulation from
        :type path:     str

        :returns:       Whether the state was loaded successfully
        :rtype:         bool
        '''

        # Check if the path exists
        if not os.path.exists(path):
            raise NominalException(f"Path '{path}' does not exist.")

        # Load the state from the path
        with open(path, 'r') as file:
            state: dict = json.load(file)
            return self.set_state(state)

    def track_object (self, instance: Instance, isAdvanced: bool = False) -> None:
        '''
        Starts tracking the object within the simulation. This will start tracking the object
        which will store the object's data and state every specified tick in a local database.
        This can be used to retrieve the object's data at a later time.

        :param instance:    The instance to track within the simulation
        :type instance:     Instance
        :param isAdvanced:  Whether the advanced variables are also being tracked
        :type isAdvanced:   bool
        '''

        # Get the tracking system
        system: System = self.get_system(TRACKING_SYSTEM)

        # Invoke the track object
        system.invoke("TrackObject", instance.id, isAdvanced)
    
    def query_object (self, instance: Instance) -> DataFrame:
        '''
        Queries the object within the simulation. This will query the object and return the data
        that has been stored for the object. This will return the data as a data frame. If there
        is no data for the object, or if the object has not yet been tracked, an empty data frame 
        will be returned.

        :param instance:    The instance to query within the simulation
        :type instance:     Instance

        :returns:           The data that has been stored for the object
        :rtype:             DataFrame
        '''

        # Get the tracking system
        system: System = self.get_system(TRACKING_SYSTEM)

        # Invoke the query object
        data = system.invoke("ExportToJSON", instance.id)

        # Create and return the data frame
        return DataFrame(data)