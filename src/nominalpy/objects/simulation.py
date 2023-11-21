#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2023.

import time
from .component import Component
from .entity import Entity
from .message import Message
from .object import Object
from ..connection import Credentials, http, helper
from ..maths import value
from ..utils import NominalException, printer, types
from ..image import Visualiser


class Simulation(Entity):
    '''
    The Simulation class allows for a simulation to be constructed using
    the API and for objects to be added to the simulation. All objects
    need to be created via the simulation and the simulation can also
    tick all objects within the simulation.
    '''

    __components: list = []
    '''Defines a list of components added to the simulation. This will be populated by adding components to the simulation.'''

    __time: float = 0.0
    '''Defines the current simulation since starting the simulation. This is calculated based on the number of ticks that have occurred.'''

    __visualiser: Visualiser = None
    '''Defines the image visualiser if it has been created and initialised with MQTT'''

    __cesium: dict = {}
    '''Defines the Cesium configuration for the image request that can be sent through the system'''

    __messages: dict = {}
    '''Defines a list of messages associated with a particular property for easy fetching'''

    def __init__ (self, credentials: Credentials, reset: bool = True) -> None:
        '''
        Default constructor for the simulation handler which takes 
        in the credentials to access the API. The reset flag will attempt
        to reset the simulation when initialised by default.

        :param credentials: The Credentials object that is used for the API
        :type credentials:  Credentials
        :param reset:       A flag whether to reset the previous simulation loaded in the session if existed
        :type reset:        bool
        '''

        super().__init__(credentials=credentials, id=None)

        self.__credentials = credentials
        if self.__credentials == None:
            raise NominalException("Invalid Credentials: No credentials passed into the Simulation.")
        
        # Attempt a simple request
        if not self.__credentials.is_local:
            http.validate_credentials(self.__credentials)

        # Resets the simulation if valid credentials
        if reset and self.__credentials != None:
            self.reset()

        # Fetch the current ID
        timeline: dict = self.__get_timeline()
        if timeline != None:
            self.id = timeline["ID"]
    
    def __get_timeline (self) -> dict:
        '''
        Attempts to fetch the current timeline information from the simulation, 
        including the initial epoch, ID and current time.

        :returns:   The timeline information in the form of a JSON object
        :rtype:     dict
        '''
        
        response = http.get_request(self.__credentials, "timeline")
        if response == {}:
            return None
        return response

    def get_component_types (self) -> list:
        '''
        This will return a list of all component types available in the simulation
        that can be created. This includes components, component models and
        simulation subsystems. This will include the full name of every component
        inside a list.

        :returns:   A list of all component types available in the simulation
        :rtype:     list
        '''

        # Create the get request
        return http.get_request(self.__credentials, "object/types")

    def add_component (self, type: str, owner: Component = None, **kwargs) -> Component:
        '''
        Attempts to add a new component to the simulation. This component
        can be added to an owner, if the owning component is passed in,
        or it can be added to the simulation as the base type. Additionally,
        initialisation parameters can be passed in to set on create
        with the keyword arguments. If the component is invalid or the type
        is incorrect, a None component will be returned. Otherwise, a component
        will be initialised with the ID from the call.

        :param type:    The full simulation type that the object will be created of
        :type type:     str
        :param owner:   The component that will own the component and will be attached to, if it exists
        :type owner:    Component
        :param kwargs:  A set of keyword arguments and parameters to initialse the object's data to when created
        :type kwargs:   dict

        :returns:       A reference to the component added initialised with the correct ID
        :rtype:         Component
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
            body["data"] = helper.serialize(kwargs)

        # Create the data
        request_data: str = helper.jsonify(body, True)

        # Create the response from the PUT request and get the IDs
        response = http.put_request(self.__credentials, "objects", data=request_data)
        printer.log("Attempted to create %d component(s) with IDs: \n\t%s" % (len(response), response))

        # Skip on empty list
        if len(response) == 0: return None

        # Check the GUID and return a new component with that ID or a None component
        guid: str = response[0]
        if helper.is_valid_guid(guid):
            printer.success("Component of type '%s' created." % type)
            obj: Component = Component(self.__credentials, guid)
            self.__components.append(obj)
            return obj
        
        # Throw an error if no object or valid ID
        printer.error("Could not construct object of class '%s'" % type)
        return None
    
    def get_system (self, type: str, **kwargs) -> Object:
        '''
        Fetches a particular simulation system that is valid
        from the simulation and returns it as an object.

        :param type:    The full simulation type that the system will be searched for
        :type type:     str
        :param kwargs:  A set of keyword arguments and parameters to initialse the systems' data to when created
        :type kwargs:   dict

        :returns:       The object reference to the simulation system that is found
        :rtype:         Object
        '''

        return self.add_component(type, **kwargs)
    
    def get_message_types (self) -> list:
        '''
        This will return a list of all message types available in the simulation
        that can be created. This will include the full name of every message
        inside a list.

        :returns:   A list of all simulation message types that are valid within the simulation
        :rtype:     list
        '''

        # Create the get request
        return http.get_request(self.__credentials, "message/types")

    def get_planet_message (self, planet: str) -> Message:
        '''
        Returns the current planet state from the simulation by fetching
        the data from the SPICE kernels via the Universe system.

        :param planet:  The name of the planet whose state message will be returned
        :type planet:   str

        :returns:       The Message object containing the SPICE planet state message
        :rtype:         Message
        '''

        # Get the lower of the planet
        planet = planet.lower()

        # Check if the message exists
        if planet in self.__messages:
            return self.__messages[planet]

        # Create the data packet to be submitted to the api
        body = dict(planet=str(planet))
        body["data"] = {}
        request_data: str = helper.jsonify(body)

        # Make the request to get the data
        response = http.post_request(self._credentials, "query/planet", data=request_data)

        # Check for a valid response and update the data
        if response == None or response == {}:
            printer.error("Failed to retrieve data from planet '%s'." % planet)
            return
        
        # Transform the data into a Message object
        msg: Message = Message(credentials=self._credentials, id=response["guid"])
        self.__messages[planet] = msg
        return msg

    def tick (self, step: float = 1e-3, iterations: int = 1) -> None:
        '''
        Attempts to tick the simulation by a certain amount. This will
        tick the simulation with some step size, in the form of a time
        span, and the iterations. The iterations are ticked on the
        simulation side and will tick with the same step size.

        :param step:        The step-size to tick the simulation in seconds
        :type step:         float
        :param iterations:  The number of iterations to run the simulation at
        :type iterations:   int
        '''

        # Get the timespan and number of seconds and milliseconds to tick
        step = float(step)
        timespan: str = value.timespan(0, 0, 0, int(step), int(step * 1000) - int(step) * 1000)
        
        # Construct the JSON body
        request_data: str = helper.jsonify(
            {
                "timestep": timespan,
                "iterations": iterations
            }
        )

        # Create the response from the POST request on the timeline
        http.post_request(self.__credentials, "timeline/tick", data=request_data)
        printer.success('Ticked the simulation with a step of %.3fs %d time(s).' % (step, iterations))

        # Increase the time
        self.__time += step * float(iterations)

        # Update all objects so their data needs to be fetched
        for obj in self.__components:
            obj._require_update()
        for msg in self.__messages.values():
            msg._require_update()
        
    def get_time (self) -> float:
        '''
        Returns the current simulation time based on the number of
        seconds that have been ticked.

        :returns:   The current time of the simulation in seconds
        :rtype:     float
        '''

        return self.__time

    def capture_image (self, file_name: str, spacecraft: Object, fov: float = 90.0, exposure: float = 0.0,
        ray_tracing: bool = False, size: tuple = (500, 500), camera_position: dict = None, 
        camera_rotation: tuple = (0, 0, 0), cesium: bool = False, timeout: float = 3.0) -> bool:
        '''
        Attempts to capture an image of the simulation using the visualisation
        tool. This will capture an image based on a component's position and
        attitude. The visualiser will only capture the image if it has been
        initialised and enabled for the user account.

        :param file_name:       The name of the file to save the image as when the data is received
        :type file_name:        str
        :param spacecraft:      The spacecraft object to capture the image from with it's position
        :type spacecraft:       Object
        :param fov:             The field of view of the camera in degrees
        :type fov:              float
        :param exposure:        The camera exposure levels with a base level of 0
        :type exposure:         float
        :param ray_tracing:     A flag whether ray-tracing on the camera is enabled
        :type ray_tracing:      bool
        :param size:            A tuple containing the X and Y pixel size of the image as (X, Y)
        :type size:             tuple
        :param camera_position: The JSON formatted position of the camera relative to the base object as X, Y, Z
        :type camera_position:  dict
        :param camera_rotation: A tuple containing pitch, roll and yaw angle values in degrees of the camera relative to the base object
        :type camera_rotation:  dict
        :param cesium:          A flag whether Cesium is enabled. Cesium must have been configured before this can be enabled
        :type cesium:           bool
        :param timeout:         A timeout for pausing the thread waiting for an image. If the timeout is <= 0, it will run asynchronously
        :type timeout:          float

        :returns:               A successful capture flag if the request was sent correctly
        :rtype:                 bool     
        '''

        # Puts a default file extension
        if "." not in file_name:
            file_name += ".png"
        format: str = file_name.split(".")[-1]

        # Fetches the current epoch
        system: Object = self.get_system(types.UNIVERSE)
        epoch: dict = helper.serialize(system.get_value("Epoch"))
        zero_base: str = system.get_value("ZeroBase")

        # Fetches the spacecraft information
        spacecraft_position: dict = helper.serialize_object(spacecraft.get_value("Position"))
        spacecraft_attitude: dict = helper.serialize_object(spacecraft.get_value("Attitude"))

        # Serialize the camera information
        camera_position: dict = helper.serialize_object(camera_position)
        camera_rotation: dict = helper.serialize_object(camera_rotation)

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
                printer.warning(
                    "The capture image from the visualiser was not returned within a %ss timeout. The image may still be received asynchronously but requests may be lost." % timeout)

    def confiure_cesium (self, access_token: str, terrain_id: int = 1, imagery_id: int = 2) -> None:
        '''
        Configures Cesium within the imagery system to capture photos using
        a Cesium account. The access token must be valid or the imagery
        request will not work correctly.

        :param access_token:    The valid Cesium access token that exists within a user's account
        :type access_token:     str
        :param terrain_id:      The asset ID of the terrain map chosen for the Cesium object
        :type terrain_id:       int
        :param imagery_id:      The asset ID of the imagery asset chosen for the Ceisum object
        :type imagery_id:       int
        '''

        if access_token == "" or access_token == None:
            printer.error("Invalid Cesium Ion Access Token.")
        if terrain_id == 0 or imagery_id == 0:
            printer.error("Invalid Terrain or Imagery asset IDs entered.")

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
        
        http.delete_request(self.__credentials, "timeline")
        self.__components = []
        self.__messages = {}
        self.__time = 0.0
        self.id = None
