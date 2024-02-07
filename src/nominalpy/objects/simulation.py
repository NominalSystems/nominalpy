#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

import time, os, json
from datetime import datetime
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

    __systems: dict = {}
    '''Defines a dictionary of systems that have been added to the simulation, based on the type and the object.'''

    __time: float = 0.0
    '''Defines the current simulation since starting the simulation. This is calculated based on the number of ticks that have occurred.'''

    __visualiser: Visualiser = None
    '''Defines the image visualiser if it has been created and initialised with MQTT'''

    __cesium: dict = {}
    '''Defines the Cesium configuration for the image request that can be sent through the system'''

    __messages: dict = {}
    '''Defines a list of messages associated with a particular property for easy fetching'''

    def __init__ (self, credentials: Credentials, reset: bool = True, delete_database: bool = True) -> None:
        '''
        Default constructor for the simulation handler which takes 
        in the credentials to access the API. The reset flag will attempt
        to reset the simulation when initialised by default.

        :param credentials:     The Credentials object that is used for the API
        :type credentials:      Credentials
        :param reset:           A flag whether to reset the previous simulation loaded in the session if existed
        :type reset:            bool
        :param delete_database: A flag whether to delete the database that exists too
        :type delete_database:  bool
        '''

        super().__init__(credentials=credentials, id=None)

        self._credentials = credentials
        if self._credentials == None:
            raise NominalException("Invalid Credentials: No credentials passed into the Simulation.")
        if not self._credentials.is_valid():
            raise NominalException("Invalid Credentials: The credentials are missing information.")
        
        # Attempt a simple request
        if not self._credentials.is_local:
            http.validate_credentials(self._credentials)

        # Resets the simulation if valid credentials
        if reset and self._credentials != None:
            self.reset(delete_database)

        # Fetch the current ID
        simulation: dict = self.__get_simulation()
        if simulation != None:
            self.id = simulation["ID"]
    
    def __get_simulation (self) -> dict:
        '''
        Attempts to fetch the current timeline information from the simulation, 
        including the initial epoch, ID and current time.

        :returns:   The simulation timeline information in the form of a JSON object
        :rtype:     dict
        '''
        
        response = http.get_request(self._credentials, "simulation")
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
        return http.get_request(self._credentials, "object/types")

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
            "Type": type
        }
        
        # Add in owner to the body
        if owner != None and isinstance(owner, Component):
            body["Owner"] = owner.id

        # If there are keyword arguments
        if len(kwargs) > 0:
            body["Data"] = helper.serialize(kwargs)

        # Create the data
        request_data: str = helper.jsonify(body, True)

        # Create the response from the PUT request and get the IDs
        response = http.put_request(self._credentials, "objects", data=request_data)
        printer.log("Attempted to create %d component(s) with IDs: \n\t%s" % (len(response), response))

        # Skip on empty list
        if len(response) == 0:
            return None

        # Check the GUID and return a new component with that ID or a None component
        guid: str = response[0]
        if helper.is_valid_guid(guid):
            printer.success("Component of type '%s' created." % type)
            obj: Component = Component(self._credentials, guid)
            self.__components.append(obj)

            # Add the child to the owner
            if owner != None:
                owner._Component__children.append(obj)

            return obj

        # Throw an error if no object or valid ID
        raise NominalException(f"Could not construct object of class {type}. Object name may be invalid.")
    
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

        # Checks if the type exists, update the values and return
        if type in self.__systems:
            system: Component = self.__systems[type]
            if len(kwargs) > 0:
                system.set_values(**kwargs)
            return system
        
        # Otherwise, add a new component and return
        system: Component = self.add_component(type, **kwargs)
        self.__systems[type] = system
        return system
    
    def get_components_added (self) -> list:
        '''
        Returns the list of components that have been added to this
        simulation.

        :returns:   A list of component objects as a copied list
        :rtype:     list
        '''
        return self.__components
    
    def find_component (self, id: str) -> Component:
        '''
        Attempts to find a component with a particular ID in the
        simulation and is able to create it as a python object if
        it does not yet exist. This searches the simulation API
        for an ID and if it doesn't exist in the Python simulation
        object, then it will be created and added. Otherwise, if
        it does exist, the reference to the object will be returned.

        :param id:  The GUID of the object being searched for
        :type id:   str

        :returns:   A reference to the component that was found
        :rtype:     Component
        '''

        # If empty ID, throw exception
        if not helper.is_valid_guid(id):
            raise NominalException(f"Invalid ID '{id}' passed.")

        # Check if the ID matches within the list and return the object
        obj: Component = next((obj for obj in self.__components if obj.id == id), None)
        if obj != None:
            return obj

        # Fetch the components from the API of the type
        request_data = helper.jsonify({
            "ID": id,
            "Params": ["Owner"]
        })

        # Fetch the object if it exists
        response: list = http.post_request(self._credentials, "query/object", data=request_data)
        
        # If no response, throw an exception
        if response == None:
            raise NominalException(f"Failed to find component with ID '{id}'.")
        
        # Create the new object
        printer.success("Component of type '%s' found and added to the simulation." % response["Type"])
        id = response["ID"]
        obj: Component = Component(self._credentials, id)
        self.__components.append(obj)

        # Return the new object
        return obj
    
    def find_components_of_type (self, type: str) -> list:
        '''
        Attempts to find components of a particular type and
        returns a list of components of a particular type that
        exist within the simulation. This will also check off
        any components that may already exist in this simulation
        object.

        :param type:    The full Nominal type of the object to filter by
        :type type:     str

        :returns:       A list of components that match the type
        :rtype:         list
        '''

        # Sanitise the type
        if "NominalSystems" not in type:
            if "." not in type:
                type = "NominalSystems.Classes." + type
            else:
                type = "NominalSystems." + type

        # Fetch the components from the API of the type
        request_data = helper.jsonify({
            "Type": type,
            "Params": ["Owner"] # This is to force no other data to come through
        })

        # Make the request to get the data
        response: list = http.post_request(self._credentials, "query/objects", data=request_data)

        # Create the components list
        components: list = []

        # Loop through each component
        for component in response:
            id: str = component["ID"]

            # Fetch the component and add it
            components.append(self.find_component(id))

        # Return the list
        return components
    
    def get_systems_added (self) -> list:
        '''
        Returns the list of all systems that have been added to the simulation.
        This will return the system as a list as a cache.

        :returns:   A list of system objects as a copied list
        :rtype:     list
        '''
        return self.__systems.values()
    
    def get_message_types (self) -> list:
        '''
        This will return a list of all message types available in the simulation
        that can be created. This will include the full name of every message
        inside a list.

        :returns:   A list of all simulation message types that are valid within the simulation
        :rtype:     list
        '''

        # Create the get request
        return http.get_request(self._credentials, "message/types")

    def get_planet_message (self, planet: str) -> Message:
        '''
        Returns the current planet state from the simulation by fetching
        the data from the SPICE kernels via the Universe system.

        :param planet:  The name of the planet whose state message will be returned
        :type planet:   str

        :returns:       The Message object containing the SPICE planet state message
        :rtype:         Message
        '''

        # Skip if missing planet
        if planet == None or planet == "":
            raise NominalException("Invalid planet name passed into 'get_planet_message' function.")

        # Get the lower of the planet
        planet = planet.lower()

        # Check if the message exists
        if planet in self.__messages.keys():
            return self.__messages[planet]

        # Create the data packet to be submitted to the api
        body = dict(Planet=str(planet))
        body["Params"] = {}
        request_data: str = helper.jsonify(body)

        # Make the request to get the data
        response = http.post_request(self._credentials, "query/planet", data=request_data)

        # Check for a valid response and update the data
        if response is None or response == {}:
            raise NominalException(f"Failed to retrieve data from planet {planet}.")
        
        # Transform the data into a Message object
        msg: Message = Message(credentials=self._credentials, id=response["ID"])
        self.__messages[planet] = msg
        return msg

    def create_message (self, type: str, **kwargs) -> Message:
        '''
        Attempts to create a new empty message that does not belong to a
        component but is owned by the simulation. This can also create
        some parameters within the message and will return the message
        object if created correctly.

        :param type:    The namespace and type of the message to be created
        :type type:     str
        :param kwargs:  Additional parameters to initialise the message with
        :type kwargs:   dict

        :returns:       The message wrapper object if was created correctly
        :rtype:         Message
        '''

        # Sanitise the type
        if "NominalSystems.Messages" not in type:
            type = "NominalSystems.Messages." + type

        # Construct the JSON body
        body: dict = {
            "Type": type
        }

        # If there are keyword arguments
        if len(kwargs) > 0:
            body["Data"] = helper.serialize(kwargs)

        # Create the data
        request_data: str = helper.jsonify(body, True)

        # Create the response from the PUT request and get the IDs
        response = http.put_request(self._credentials, "messages", data=request_data)
        printer.log("Attempted to create a new message of type '%s'." % type)

        # Skip on empty list
        if len(response) == 0: return None

        # Check the GUID and return a new message with that ID or a None message
        guid: str = response[0]
        if helper.is_valid_guid(guid):
            printer.success("Message of type '%s' created." % type)
            msg: Message = Message(self._credentials, guid)
            return msg
        
        # Throw an error if no message or valid ID
        raise NominalException(f"Could not construct message of class {type}. Message name may be invalid.")

    def tick (self, step: float = 1e-3, iterations: int = 1, batch: bool = True, callback = None) -> None:
        '''
        Attempts to tick the simulation by a certain amount. This will
        tick the simulation with some step size, in the form of a time
        span, and the iterations. The iterations are ticked on the
        simulation side and will tick with the same step size. By calling
        the 'batch' as True, then the simulation will run the iterations
        on the simulation side. However, for running one API request per
        iteration, set the 'batch' parameter to False.

        :param step:        The step-size to tick the simulation in seconds
        :type step:         float
        :param iterations:  The number of iterations to run the simulation at
        :type iterations:   int
        :param batch:       This defines whether the simulation should run the simulation at batch
        :type batch:        bool
        :param callaback:   An optional function callback that is executed after each tick. This must have a time parameter.
        :type callback:     function
        '''

        # Sanitise the inputs
        step = float(step)
        if step <= 1e-9:
            raise NominalException("Invalid step. Unable to tick a simulation with a timestep under 1e-9 seconds.")
        if iterations < 1:
            raise NominalException("Invalid iterations. Unable to tick a simulation with iterations < 1.")

        # Get the timespan and number of seconds and milliseconds to tick
        timespan: str = value.timespan(0, 0, 0, int(step), int(step * 1000) - int(step) * 1000)

        # Create the generic body for the request data
        request_data: str = helper.jsonify(
            {
                "Timestep": timespan,
                "Iterations": iterations if batch else 1
            }
        )

        # If running the batch command, create the body and the response
        if batch:
            http.post_request(self._credentials, "simulation/tick", data=request_data)
            if callback is not None: 
                callback(self.__time + step * float(iterations))
        
        # If running one at a time, perform the loop and print the update
        else:
            for i in range (int(iterations)):
                http.post_request(self._credentials, "simulation/tick", data=request_data)
                printer.log('Ticked the simulation with a step of %.3fs. \t[%d / %d].' % (step, i + 1, int(iterations) + 1))
                if callback is not None: 
                    callback(self.__time + step * float(i))

        # Output the success message
        printer.success('Ticked the simulation with a step of %.3fs %d time(s).' % (step, iterations))

        # Increase the time
        self.__time += step * float(iterations)

        # Update all objects so their data needs to be fetched
        for obj in self.__components:
            obj._require_update()
        for msg in self.__messages.values():
            msg._require_update()

    def tick_duration (self, duration: float, step: float = 1e-3, batch: bool = True, callback = None) -> None:
        '''
        Attempts to tick the simulation by a certain amount. This will
        tick the simulation with some step size, in the form of a time
        span, and the iterations. The iterations are ticked on the
        simulation side and will tick with the same step size.

        :param duration:    The number of seconds forward in time to tick the simulation
        :type duration:     float
        :param step:        The size of the step to tick the simulation in seconds
        :type step:         float
        :param batch:       This defines whether the simulation should run the simulation at batch
        :type batch:        bool
        :param callaback:   An optional function callback that is executed after each tick. This must have a time parameter.
        :type callback:     function
        '''

        # Sanitise the inputs
        if step <= 1e-9:
            raise NominalException("Invalid step. Unable to tick a simulation with a timestep under 1e-9 seconds.")
        if duration <= 0.0:
            raise NominalException("Invalid duration. Unable to tick a simulation for a duration that is less than or equal to 0 seconds.")

        # Call the tick with some time
        return self.tick(step=step, iterations=int(duration / step), batch=batch, callback=callback)

    def get_time (self) -> float:
        '''
        Returns the current simulation time based on the number of
        seconds that have been ticked.

        :returns:   The current time of the simulation in seconds
        :rtype:     float
        '''

        return self.__time
    
    def get_datetime (self) -> datetime:
        '''
        Returns the current datetime of the simulation at the current
        point in the simulation. This will be returned from the simulation
        and is the sum of the initial Epoch and the time elapsed.

        :returns:   The current datetime of the simulation
        :rtype:     datetime
        '''

        # Fetches the datetime data and returns the structure
        dt: dict = self.__get_simulation()["SimulationDate"]
        return datetime(dt["Year"], dt["Month"], dt["Day"], dt["Hour"], dt["Minute"], dt["Second"], dt["Millisecond"] * 1000)

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
        if self.__visualiser is None:
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
            raise NominalException("Invalid Cesium Ion Access Token.")
        if terrain_id == 0 or imagery_id == 0:
            raise NominalException("Invalid Terrain or Imagery asset IDs entered.")

        # Configure the Cesium data
        self.__cesium = {
            "enabled": True,
            "access_token": access_token,
            "terrain_id": terrain_id,
            "imagery_id": imagery_id
        }
    
    def get_state (self) -> dict:
        '''
        Attempts to fetch the current simulation state in the form of a
        JSON object and returns the state of the simulation as a dictionary.
        If there is an error in the simulation, this will be caught and
        displayed as an error thrown. The simulation state includes all
        component, message and system parameters.

        :returns:   A dictionary with the simulation state stored
        :rtype:     dict
        '''

        # Fetch the data
        response = http.post_request(self._credentials, "simulation")

        # Return the response as a dictionary
        return response
    
    def save_state (self, path: str = None) -> None:
        '''
        Saves the state of the simulation to a file relative to
        the current working directory. This will save the entire
        simulation as JSON into a text file.

        :param path:    The relative (or full) path to the file to save to
        :type path:     str
        '''

        # Fetch the current state
        state: dict = self.get_state()

        # Fetch the path
        path = self.__get_state_file_name(path)
        
        # Check if the directory needs to be created
        directory: str = "".join(path.replace("\\", "/").split("/")[:-1])
        os.makedirs(directory, exist_ok=True)

        # Save the file in the directory
        with open(path, "+w") as file:
            json.dump(state, file, indent=4)
    
    def load_state (self, path: str = None, data: dict = None) -> None:
        '''
        Attempts to load the state of the simulation to a valid JSON
        object. This data can be found in either a file, with a valid
        path, or from a JSON data object. Once the simulation is reloaded,
        all components are deleted and the objects are recreated based
        on the simulation state that was saved.

        :param path:    The full or relative path to the file with the json data
        :type path:     str
        :param data:    Alternatively, the json data can be passed through here
        :type data:     dict
        '''

        # If there is a path, load it as the json
        if path != None:
            path = self.__get_state_file_name(path)

            # Check if the file exists
            if not os.path.exists(path):
                raise NominalException(f"Unable to find file with path: '{path}'.")

            # Open the file and load it as a JSON into the json data
            with open(path, "r") as file:
                data = json.load(file)
        
        # If there is no data, then throw an error
        if data is None:
            raise NominalException("Invalid or missing data passed into the load state for the simulation.")

        # Attempt to load the simulation with the data
        id: str = http.put_request(self._credentials, "simulation", data=helper.jsonify(data))

        # Reset the simulation and update the id
        self.__reset()
        self.id = id

    def __get_state_file_name (self, path: str) -> str:
        '''
        Cleans up the simulation file name and makes sure
        it is of the correct format. It must end with a
        .json and must be a file.
        '''

        # Check if the path is empty
        if path == None:
            path = ""

        # Clean the path name
        path = path.rstrip().lstrip()

        # Check if there is no ending to the path
        if path == "" or path.endswith("/"):
            path += "simulation"
        
        # Check if the path does not have the correct ending
        if not path.endswith(".json"):
            path += ".json"

        # Return the path
        return path

    def reset (self, delete_database: bool = True) -> None:
        '''
        Deletes and resets the simulation. All components, data
        and messages associated with the timeline on the simulation
        will be deleted.

        :param delete_database: A flag whether to delete the database that exists too
        :type delete_database:  bool
        '''

        # Create the generic body for the request data
        request_data: str = helper.jsonify(
            {
                "Database": delete_database
            }
        )
        
        # Delete the simulation and the database if required
        http.delete_request(self._credentials, "simulation", data=request_data)
        self.__reset()
    
    def __reset (self) -> None:
        '''
        Performs a soft reset, only adjusting the data within the
        simulation on the python end without making a HTTP REST
        endpoint call.
        '''

        # Reset any data
        self.__components = []
        self.__systems = {}
        self.__messages = {}
        self.__time = 0.0
        self.id = None