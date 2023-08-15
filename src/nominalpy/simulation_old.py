'''
        [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems
to aid with communication to the public API.
'''

from .request_helper import *
from .component import Component
from .credentials import Credentials
from .message_old import Message
from .system import System

'''
Defines the simulation handler that can handle creating any
of the simulation properties and functions for the classes.
This requires proper credential access that must be passed
into the simulation.
'''
class SimulationOld:

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
            self.reset()

    def get_current_time (self) -> float:
        '''
        Returns the current time of the simulation in seconds since
        the simulation has started.
        '''
        data = get_request(self.__credentials, "simulation/time")
        return float(data)
    
    def get_is_running (self) -> bool:
        '''
        Returns whether the simulation is currently running
        and is still being executed.
        '''
        data = get_request(self.__credentials, "simulation/is_running")
        return bool(data)  

    def get_components (self) -> list:
        '''
        Returns a list of all components that have been added
        to the simulation as a list of IDs.
        '''
        data = get_request(self.__credentials, "simulation/components")
        if data == None: return []
        return data.replace('"', "")[1:-1].split(",")

    def get_num_components (self) -> int:
        '''
        Returns the number of components that exist within
        the simulation.
        '''
        return len(self.get_components())

    def tick (self, delta: float, iterations: int = 1) -> None:
        '''
        Ticks the simulation with a delta time in seconds
        and updates all of the components in the simulation. This
        can also pass in iterations of number of simulation ticks.
        '''
        post_request(self.__credentials, "simulation/tick", params={"step": delta, "iterations": iterations})

    def execute (self, time: float, step: float = 0.1, display: bool = True) -> None:
        '''
        Executes the simulation for a specific amount of time and with
        a specific step-size that will call Tick until the simulation
        ends.
        '''
        if display:
            STEPS: int = 5
            split: float = time / float(STEPS)
            print("Simulating...")
            print("%s 0/%d" % ("." * STEPS, time))
            for i in range(1, STEPS + 1):
                iterations: int = (int)(split / float(step))
                self.tick(step, iterations)
                print("%s%s %d/%d" % ("=" * i, "." * (STEPS - i), split * i, time), flush=True)
        else:
            iterations: int = (int)(time / float(step))
            self.tick(step, iterations)

    def reset (self) -> None:
        '''
        Resets the simulation and removes all of the current
        components in the library.
        '''
        post_request(self.__credentials, "simulation/reset")

    def set_message_frequency (self, period: float) -> None:
        '''
        Defines the time, in simulation seconds, between writing intervals of
        messages that have been registered in the database system to be written
        to the database file. By default, this is 10s if the method has not been
        called.
        '''
        post_request(self.__credentials, "simulation/message_freq", params = {"period": period})

    def add_spacecraft (self) -> Component:
        '''
        Creates a spacecraft in the simulation and attaches it to the
        simulation. This will also ensure that the credentials are passed
        through correctly to the object created. The spacecraft will have
        no initial properties. If invalid, this will return a None type.
        '''

        # Call the POST request.
        id: str = post_request(
            self.__credentials, 
            "simulation/add_component", 
            params={"type": "NominalSystems.Universe.Spacecraft", "parent":""}
        )

        # Check if null id
        if id == None:
            return None

        # Create the component
        return Component(self.__credentials, id)  

    def add_ground_station (self) -> Component:
        '''
        Creates a ground station in the simulation and attaches it to the
        simulation. This will also ensure that the credentials are passed
        through correctly to the object created. The ground station will have
        no initial properties. If invalid, this will return a None type.
        '''

        # Call the POST request.
        id: str = post_request(
            self.__credentials, 
            "simulation/add_component", 
            params={"type": "NominalSystems.Universe.GroundStation", "parent":""}
        )

        # Check if null id
        if id == None:
            return None

        # Create the component
        return Component(self.__credentials, id)

    def create_message (self, name: str) -> Message:
        '''
        Constructs a simulation message of a particular message name
        and returns the new message with the passed credentials. If
        the message is invalid, it will return an invalid message.
        '''

        # Format the message
        if "NominalSystems.Messages" not in name:
            name = "NominalSystems.Messages.%s" % (name)

        # Call the POST request.
        id: str = post_request(
            self.__credentials, 
            "message/create",
            params={"type": name}
        )

        # Check if null id
        if id == None:
            return None

        # Construct the message
        return Message(self.__credentials, id)  

    def get_system (self, name: str) -> System:
        '''
        Fetches a simulation system with a particular name. If
        the name is invalid, then the simulation system will
        return a None value.
        '''

        # Ensure the name is valid
        if name == "":
            return None

        # Construct the simulation system with credentials
        return System(self.__credentials, name)