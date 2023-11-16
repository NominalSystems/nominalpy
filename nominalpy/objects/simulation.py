'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

The Simulation class allows for a simulation to be constructed using
the API and for objects to be added to the simulation. All objects
need to be created via the simulation and the simulation can also
tick all objects within the simulation.
'''

import time

from ..objects.object import Object
from ..objects.object import Entity
from ..objects.component import Component
from ..request_helper import *
from ..credentials import Credentials
from ..maths import value
from ..printer import *
from ..objects.message import Message
from ..image.visualiser import Visualiser
from ..types import UNIVERSE


class Simulation(Entity):

    '''
    Defines a list of components added to the simulation. This will be 
    populated by adding components to the simulation.
    '''
    __components: list = []

    '''
    Defines the current simulation since starting the simulation. This is
    calculated based on the number of ticks that have occurred.
    '''
    __time: float = 0.0

    '''
        Defines the image visualiser if it has been created and initialised
        with a particular object connected to MQTT.
        '''
    __visualiser: Visualiser = None

    '''
    Defines the Cesium configuration for the image request that can be
    sent through to the system.
    '''
    __cesium: dict = {}

    def __init__ (self, credentials: Credentials, reset: bool = True) -> None:
        '''
        Default constructor for the simulation handler which takes 
        in the credentials to access the API. The reset flag will attempt
        to reset the simulation when initialised by default.
        '''
        super().__init__(credentials=credentials, id=None)

        self.__credentials = credentials
        if self.__credentials == None:
            raise NominalException("Invalid Credentials: No credentials passed into the Simulation.")
        
        # Attempt a simple request
        if not self.__credentials.is_local:
            validate_credentials(self.__credentials)

        # Resets the simulation if valid credentials
        if reset and self.__credentials != None:
            self.reset()

        # Fetch the current ID
        timeline: dict = self.__get_timeline__()
        if timeline != None:
            self.id = timeline["ID"]
    
    def __get_timeline__ (self) -> dict:
        '''
        Attempts to fetch the current timeline information from the simulation, 
        including the initial epoch, ID and current time.
        '''
        response = get_request(self.__credentials, "timeline")
        if response == {}:
            return None
        return response

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
        log("Attempted to create %d component(s) with IDs: \n\t%s" % (len(response), response))

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

    def get_planet_message(self, planet: str) -> Message:
        """
        Get the spice state message for an input planet

        :param planet: the name of the planet whose state msg will be returned
        :type planet: str
        :return: return the Message object containing the spice planet state message
        :rtype: Message
        """
        # Create the data packet to be submitted to the api
        body = dict(planet=str(planet))
        body["data"] = {}
        request_data: str = jsonify(body)
        # Make the request to get the data
        response = post_request(self._credentials, f"query/planet", data=request_data)
        # Check for a valid response and update the data
        if response == None or response == {}:
            error(f"Failed to retrieve data from planet.")
            return
        # Transform the data into a Message object
        msg: Message = Message(credentials=self._credentials, id=response["guid"])
        # Return the message
        return msg

    def get_planet_message_id(self, planet: str) -> str:
        """
        Get the spice planet message id
        :param planet: the name of the planet whose state msg will be returned
        :return: the guid of the spice planet state message
        """
        return self.get_planet_message(planet=planet).id

    def tick (self, step: float = 1e-3, iterations: int = 1) -> None:
        '''
        Attempts to tick the simulation by a certain amount. This will
        tick the simulation with some step size, in the form of a time
        span, and the iterations. The iterations are ticked on the
        simulation side and will tick with the same step size.
        '''

        # Get the timespan and number of seconds and milliseconds to tick
        step = float(step)
        timespan: str = value.timespan(0, 0, 0, int(step), int(step * 1000) - int(step) * 1000)
        
        # Construct the JSON body
        request_data: str = jsonify(
            {
                "timestep": timespan,
                "iterations": iterations
            }
        )

        # Create the response from the POST request on the timeline
        post_request(self.__credentials, "timeline/tick", data=request_data)
        success('Ticked the simulation with a step of %.3fs %d time(s).' % (step, iterations))

        # Increase the time
        self.__time += step * float(iterations)

        # Update all objects so their data needs to be fetched
        for obj in self.__components:
            obj.__require_update__()
        
    def get_time (self) -> float:
        '''
        Returns the current simulation time based on the number of
        seconds that have been ticked.
        '''
        return self.__time

    def capture_image(self, file_name, spacecraft: Object, fov: float = 90.0, exposure: float = 0.0,
                      ray_tracing: bool = False,
                      size: tuple = (500, 500), camera_position: dict = None, camera_rotation: tuple = (0, 0, 0),
                      cesium: bool = False, timeout: float = 3.0) -> bool:
        '''
        Attempts to capture an image of the simulation using the visualisation
        tool. This will capture an image based on a component's position and
        attitude.
         - file_name:       [REQUIRED] The name of the file to save the image as when the data is received
         - spacecraft:      [REQUIRED] The simulation object for ths spacecraft in
         - fov:             The field of view of the camera in degrees
         - exposure:        The exposure level of the camera to take an image with
         - ray_tracing:     A flag whether to enable ray-tracing on the camera
         - size:            A tuple containing the X and Y pixel size of the image as (X, Y)
         - camera_position: The JSON formatted position of the camera relative to the base object as X, Y, Z
         - camera_rotation: A tuple containing pitch, roll and yaw angle values in degrees of the camera relative to the base object
         - cesium:          A flag whether Cesium is enabled. Cesium must have been configured before this can be enabled
         - timeout:         A timeout for pausing the thread waiting for an image. If the timeout is <= 0, it will run asynchronously.
        '''

        # Puts a default file extension
        if "." not in file_name:
            file_name += ".png"
        format: str = file_name.split(".")[-1]

        # Fetches the current epoch
        epoch: dict = self.get_system(UNIVERSE).get_value("Epoch")
        zero_base: str = self.get_system(UNIVERSE).get_value("ZeroBase")

        # Fetches the spacecraft information
        spacecraft_position: dict = spacecraft.get_value("Position")
        spacecraft_attitude: dict = spacecraft.get_value("Attitude")

        # Create the visualiser if it doesn't exist
        if self.__visualiser == None:
            self.__visualiser = Visualiser()

        # Fetch the cesium values
        cesium_data: dict = self.__cesium if cesium else None

        # Capture the image with the parameters
        self.__visualiser.capture(epoch=epoch, zero_base=zero_base, position=spacecraft_position,
                                  attitude=spacecraft_attitude,
                                  format=format, fov=fov, exposure=exposure, ray_tracing=ray_tracing, size=size,
                                  camera_position=camera_position,
                                  camera_rotation=camera_rotation, cesium=cesium_data, file_name=file_name)

        # If pausing thread
        if timeout > 0:
            end_time: float = time.time() + timeout
            completed: bool = False
            while time.time() < end_time:
                if self.__visualiser.file == file_name:
                    completed = True
                    break
                time.sleep(0.1)

            # Throw a warning if the timeout passes
            if not completed:
                warning(
                    "The capture image from the visualiser was not returned within a %ss timeout. The image may still be received asynchronously but requests may be lost." % timeout)

    def confiure_cesium(self, access_token: str, terrain_id: int = 1, imagery_id: int = 2) -> None:
        '''
        Configures Cesium within the imagery system to capture photos using
        a Cesium account. The access token must be valid or the imagery
        request will not work correctly.
        '''
        if access_token == "" or access_token == None:
            error("Invalid Cesium Ion Access Token.")
        if terrain_id == 0 or imagery_id == 0:
            error("Invalid Terrain or Imagery asset IDs entered.")

        # Configure the Cesium data
        self.__cesium = {
            "enabled": True,
            "access_token": access_token,
            "terrain_id": terrain_id,
            "imagery_id": imagery_id
        }

    def reset (self) -> None:
        '''
        Deletes and resets the simulation. All components, data
        and messages associated with the timeline on the simulation
        will be deleted.
        '''
        delete_request(self.__credentials, "timeline")
        self.__components = []
        self.__time = 0.0
        self.id = None