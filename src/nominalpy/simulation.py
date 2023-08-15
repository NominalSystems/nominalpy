'''
        [ NOMINAL SYSTEMS ]
TODO
'''

from .object import Object
from .component import Component
from .request_helper import *
from .credentials import Credentials
from .message_old import Message
from .system import System
from .value import Value
from .printer import *

class Simulation:

    '''
    Specifies the credentials for accessing the API correctly.
    '''
    __credentials: Credentials = None

    '''
    Defines a list of components added to the simulation. This will be populated
    by adding components to the simulation.
    '''
    __components: list = []

    
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
            self.delete()

    def get_component_types (self) -> list:
        '''
        This will return a list of all component types available in the simulation
        that can be created. This includes components, component models and
        simulation subsystems. This will include the full name of every component
        inside a list.
        '''

        # Create the get request
        return get_request(self.__credentials, "object/types")

    def add_component (self, type: str, owner: Component = None, **kwargs) -> Component:
        '''
        Attempts to add a new component to the simulation. This component
        can be added to an owner, if the owning component is passed in,
        or it can be added to the simulation as the base type. Additionally,
        initialisation parameters can be passed in to set on create
        with the keyword arguments. If the component is invalid or the type
        is incorrect, a None component will be returned. Otherwise, a component
        will be initialised with the ID from the call.
        '''

        # Sanitise the type
        if "NominalSystems" not in type:
            if "." not in type:
                type = "NominalSystems.Classes." + type
            else:
                type = "NominalSystems." + type
       
        # Construct the JSON body
        body: dict = {
            "type": type
        }
        
        # Add in owner to the body
        if owner != None and isinstance(owner, Component):
            body["owner"] = owner.id

        # If there are keyword arguments
        if len(kwargs) > 0:
            body["data"] = kwargs

        # Create the data
        request_data: str = jsonify(body, True)

        # Create the response from the PUT request and get the IDs
        response = put_request(self.__credentials, "objects", data=request_data)
        log("Attempted to create %d components with IDs: \n\t%s" % (len(response), response))

        # Skip on empty list
        if len(response) == 0: return None

        # Check the GUID and return a new component with that ID or a None component
        guid: str = response[0]
        if is_valid_guid(guid):
            success("Component of type '%s' created." % type)
            obj: Component = Component(self.__credentials, guid)
            self.__components.append(obj)
            return obj
        
        # Throw an error if no object or valid ID
        error("Could not construct object of class '%s'" % type)
        return None
    
    def get_system (self, type: str, **kwargs) -> Object:
        '''
        Fetches a particular simulation system that is valid
        from the simulation and returns it as an object.
        '''
        return self.add_component(type, **kwargs)
    
    def get_message_types (self) -> list:
        '''
        This will return a list of all message types available in the simulation
        that can be created. This will include the full name of every message
        inside a list.
        '''

        # Create the get request
        return get_request(self.__credentials, "message/types")
    
    def tick (self, step: float = 1e-3, iterations: int = 1) -> None:
        '''
        Attempts to tick the simulation by a certain amount. This will
        tick the simulation with some step size, in the form of a time
        span, and the iterations. The iterations are ticked on the
        simulation side and will tick with the same step size.
        '''

        # Get the timespan
        step = float(step)
        timespan: str = Value.timespan(0, 0, 0, int(step), int(step * 1000) - int(step) * 1000)
        
        # Construct the JSON body
        request_data: str = jsonify(
            {
                "timestep": timespan,
                "iterations": iterations
            }
        )

        # Create the response from the POST request on the timeline
        post_request(self.__credentials, "timeline/tick", data=request_data)
        success('Ticked the simulation %.3fs %d time(s).' % (step, iterations))

        # Update all objects so their data needs to be fetched
        for obj in self.__components:
            obj.__require_update__()
    
    def delete (self) -> None:
        '''
        Deletes and resets the simulation. All components, data
        and messages associated with the timeline on the simulation
        will be deleted.
        '''
        delete_request(self.__credentials, "timeline")
        self.__components = []