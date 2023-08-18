'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

The Configuration class allows for a custom simulation configuration
to be created and iterated upon. This allows for an external runner
to use the configuration and perform Monte-Carlo simulations with
the specified configuration. For this to work correctly, all *CHANGING*
components must be made public in the class (using the self keyword)
and the configuration must be implemented in the 'configure' method.
'''

from .credentials import Credentials
from .component import Component
from .message import Message
from .simulation import Simulation
from .object import Object
from abc import ABC, abstractmethod

class SensitivityConfiguration (ABC):

    '''
    Specifies the credentials for accessing the API correctly.
    '''
    __credentials: Credentials = None

    def __init__ (self, credentials: Credentials = None) -> None:
        '''
        This initialiases the configuration. This will not perform
        any tasks by itself.
        '''
        self.__credentials = credentials

    @abstractmethod
    def configure (self) -> None:
        '''
        This method must be overridden by the base class and will ensure
        that the scenario is configured correctly. This is an abstract
        method and cannot be called manually on the base class.
        '''
        pass

    def tick (self, step: float = 1e-3, iterations: int = 1) -> bool:
        '''
        Attempts to tick the simulation found within the configuration
        with some time-step and some iterations. This will be done by
        attempting to fetch the simulation object from the class object,
        if it does exist.
        '''
        
        # Get the simulation and return if it does not exist
        simulation: Simulation = self.get_simulation()
        if simulation == None:
            return False

        # Tick the simulation
        simulation.tick(step, iterations)
        return True
    
    def reset (self) -> bool:
        '''
        Attempts to reset the simulation and send through the configuration
        of the spacecraft and components again.
        '''

        # Get the simulation and return if it does not exists
        simulation: Simulation = self.get_simulation()
        if simulation == None:
            return False
        
        # Reset the simulation
        simulation.reset()
        return True
    
    def get_simulation (self) -> Simulation:
        '''
        Attempts to get the simulation from the class based on the
        objects within the class. This will ensure that a simulation
        object exists within the simulation.
        '''
        for name, value in vars(self).items():
            if isinstance(value, Simulation):
                return value
        return None
    
    def get_id (self) -> str:
        '''
        Returns the ID of the simulation before the simulation is
        reset.
        '''

        # Get the simulation and return if it does not exist
        simulation: Simulation = self.get_simulation()
        if simulation == None:
            return None
        return self.get_simulation().id
    
    def set_value (self, object: str, param: str, value: str) -> bool:
        '''
        Adjusts a particular parameter on an object that can be searched
        for within the simulation. This will find an object, of a certain
        name (provided that the object is a self. object) and will attempt
        to set a parameter with a value. This will also return a boolean
        that is the success result of setting the parameter value.
        '''

        # Attempt to find the object of the name
        obj: Object = None
        for name, val in vars(self).items():
            if object == name and isinstance(val, Object):
                obj = val
                break
        
        # Skip if no object found
        if obj == None:
            return False
        
        # Set the value
        return obj.set_value(param, value)

    def subscribe (self, object: str, message: str, interval: float = 10.0) -> str:
        '''
        Attempts to subscribe to a message of a particular name on an object
        of a particular name that exists within the configuration. This will
        return the ID of the message.
        '''

        # Attempt to find the object of the name
        obj: Component = None
        for name, val in vars(self).items():
            if object == name and isinstance(val, Component):
                obj = val
                break

        # Skip if no object found
        if obj == None:
            return None
        
        # Fetch the message
        msg: Message = obj.get_message(message)
        if msg == None:
            return None

        # Subscribe to the message
        msg.subscribe(interval)

        # Return the ID
        return msg.id
    
    def add_credentials (self, credentials: Credentials) -> None:
        '''
        Sets the credentials of the configuration based on the values
        passed in.
        '''
        self.__credentials = credentials
    
    def get_credentials (self) -> Credentials:
        '''
        Returns the current credentials of the configuration based on
        what has been passed in.
        '''
        return self.__credentials