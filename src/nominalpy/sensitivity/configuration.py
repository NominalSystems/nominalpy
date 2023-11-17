#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2023.

from abc import ABC, abstractmethod
from ..objects import Component, Message, Object, Simulation
from ..connection import Credentials
from ..utils import NominalException


class SensitivityConfiguration (ABC):
    '''
    The Configuration class allows for a custom simulation configuration
    to be created and iterated upon. This allows for an external runner
    to use the configuration and perform Monte-Carlo simulations with
    the specified configuration. For this to work correctly, all *CHANGING*
    components must be made public in the class (using the self keyword)
    and the configuration must be implemented in the 'configure' method.
    '''

    __credentials: Credentials = None
    '''Specifies the credentials for accessing the API correctly.'''

    def __init__ (self, credentials: Credentials = None) -> None:
        '''
        This initialiases the configuration. This will not perform
        any tasks by itself.
        
        :param credentials: The credentials used in the API calls
        :type credenitals:  Credentials
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

        :param step:        The simulation tick step in simulation seconds
        :type step:         float
        :param iterations:  The number of iterations with the desired step to run
        :type iterations:   int

        :returns:           Whether the simulation is available and valid
        :rtype:             bool
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

        :returns:   Whether the simulation has been reset correctly
        :rtype:     bool
        '''

        # Get the simulation and return if it does not exists
        simulation: Simulation = self.get_simulation()
        if simulation == None:
            return False
        
        # Reset the simulation
        simulation.reset()
        return True
    
    def find_object (self, name: str, type: type = None) -> object:
        '''
        Attempts to find an object of a particular name (not case sensitive)
        as part of the self. parameters. Only objects that have been associated
        with the class object will be found. This can also ensure the types
        match if the optional type is passed.

        :param name:    The name of the object to find within the configuration
        :type name:     str
        :param type:    The type of object to search for if required
        :type type:     type

        :returns:       The Python object if it is found of the correct type
        :rtype:         object
        '''

        name = name.lower()
        for param, value in vars(self).items():
            if param.lower() == name:
                if type == None:
                    return value
                elif isinstance(value, type):
                    return value
        return None
    
    def find_object_of_type (self, type: type) -> object:
        '''
        Attempts to find an object of a particular type on the class-level
        of the object. Only objects that have been associated with the class 
        object will be found.

        :param type:    The type of object to search for in the class's variables
        :type type:     type

        :returns:       The Python object if it is found of the correct type
        :rtype:         object
        '''

        for _, value in vars(self).items():
            if isinstance(value, type):
                return value
        return None
    
    def get_simulation (self) -> Simulation:
        '''
        Attempts to get the simulation from the class based on the
        objects within the class. This will ensure that a simulation
        object exists within the simulation.

        :returns:   The simulation that exists within the object
        :rtype:     Simulation
        '''
        return self.find_object_of_type(Simulation)
    
    def get_id (self) -> str:
        '''
        Returns the ID of the simulation before the simulation is reset.

        :returns:   The unique ID of the simulation
        :rtype:     str
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

        :param object:  The name of the object that should be modified
        :type object:   str
        :param param:   The name of the parameter within the object that should be modified
        :type param:    str
        :param value:   The new value of the parameter that should be updated in the analysis
        :type value:    str

        :returns:       A successful write process for setting the value
        :rtype:         bool
        '''

        # Attempt to find the object of the name
        obj: Object = self.find_object(object, Object)
        
        # Skip if no object found
        if obj == None:
            raise NominalException("Failed to find object '%s' on component. Check that it exists in the configuration class using the self. keyword." % object)
        
        # Set the value
        return obj.set_value(param, value)

    def subscribe (self, object: str, message: str, interval: float = 10.0) -> str:
        '''
        Attempts to subscribe to a message of a particular name on an object
        of a particular name that exists within the configuration. This will
        return the ID of the message.

        :param object:      The name of the object that should be searched for in the analysis
        :type object:       str
        :param message:     The name of the message that should be subscribed to in the object
        :type message:      str
        :param interval:    The time interval that data should be captured at in simulation seconds
        :type interval:     float

        :returns:           The ID of the message that is subscribed to
        :rtype:             str
        '''

        # Attempt to find the object of the name
        obj: Component = self.find_object(object, Component)

        # Skip if no object found
        if obj == None:
            raise NominalException("Failed to find object '%s' on component. Check that it exists in the configuration class using the self. keyword." % object)

        # Fetch the message
        msg: Message = obj.get_message(message)
        if msg == None:
            raise NominalException("Failed to find message '%s' on component '%s'. Please check the documentation for valid message names." % (message, object))

        # Subscribe to the message
        msg.subscribe(interval)

        # Return the ID
        return msg.id
    
    def add_credentials (self, credentials: Credentials) -> None:
        '''
        Sets the credentials of the configuration based on the values
        passed in.

        :param credentials: The application credentials for calling the API
        :type credentials:  Credentials
        '''

        self.__credentials = credentials
    
    def get_credentials (self) -> Credentials:
        '''
        Returns the current credentials of the configuration based on
        what has been passed in.

        :returns:   The credentials associated with the current configuration
        :rtype:     Credentials
        '''
        
        return self.__credentials