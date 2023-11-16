'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.
'''

import json, os, datetime
from uuid import uuid4
from ..mqtt import MqttClient
from ..utils import printer

TOPIC_REQUEST: str = "NominalSystems/APIVisualiser/Request"


'''
TODO: Write this description
'''
class Visualiser:

    '''
    The name of the file to be saved into the configuration. This will
    be recorded on the capture.
    '''
    file: str = ""

    '''
    The response topic to publish the image data back from the byte
    array over.
    '''
    topic_response: str = "NominalSystems/APIVisualiser/Response"

    '''
    This records a list of metadata stored in the capture which will be
    used for updating the images when they are received by the Mqtt
    system.
    '''
    capture_data: list = []

    '''
    This defines the unique request ID that is generated when a new
    request is made.
    '''
    request_id: str = ""

    def __init__(self) -> None:
        '''
        Initialises the class and sets up the Mqtt client with the
        appropriate callback functions for the response.
        '''
        
        # Generate the request ID
        self.request_id = str(uuid4())
        self.topic_response = "NominalSystems/APIVisualiser/Response/%s" % self.request_id

        self.client: MqttClient = MqttClient()
        self.client.connect(wait=True)
        self.client.add_callback(self.topic_response, self.on_callback)

    def capture (self, epoch: dict = None, zero_base: str = "earth", position: dict = None, attitude: dict = None, 
        format: str = "png", fov: float = 90.0, exposure: float = 0.0, ray_tracing: bool = False, size: tuple = (500, 500),
        camera_position: dict = None, camera_rotation: tuple = (0, 0, 0), cesium: dict = None, file_name: str = "capture") -> None:
        '''
        Attempts to capture the simulation at a particular point in time, with a particular set
        of parameters for both the position of the object as well as the position of the camera
        relative to the object.
         - epoch:           The JSON formatted epoch for the datetime of the simulation
         - zero_base:       The central body name of the origin of the simulation coordinates
         - position:        The JSON formatted position as X, Y, Z of the target object
         - attitude:        The JSON formatted MRP attitude as X, Y, Z of the target object
         - format:          The type of the image, including JPEG, PNG or EXR
         - fov:             The field of view of the camera in degrees
         - exposure:        The exposure level of the camera to take an image with
         - ray_tracing:     A flag whether to enable ray-tracing on the camera
         - size:            A tuple containing the X and Y pixel size of the image as (X, Y)
         - camera_position: The JSON formatted position of the camera relative to the base object as X, Y, Z
         - camera_rotation: A tuple containing pitch, roll and yaw angle values in degrees of the camera relative to the base object
         - cesium:          A dictionary containing information if Cesium is required for the imnage
         - file_name:       The name of the file to save the image as when the data is received
        '''

        # Provide some default data for the missing values
        if epoch == None:
            dt = datetime.datetime.now()
            epoch = { "year": dt.year, "month": dt.month, "day": dt.day, "hour": dt.hour, "minute": dt.minute, "second": dt.second }
        if position == None:
            position = { "x": 0.0, "y": 0.0, "z": 0.0 }
        if attitude == None:
            attitude = { "x": 0.0, "y": 0.0, "z": 0.0 }
        if camera_position == None:
            camera_position = { "x": 0.0, "y": 0.0, "z": 0.15 }
        if cesium == None:
            cesium = {
                "enabled": False
            }

        # Construct the JSON formatted data
        data = {
            "request_id": self.request_id,
            "epoch": json.loads(json.dumps(epoch).lower()),
            "zero_base": zero_base,
            "spacecraft": {
                "position": json.loads(json.dumps(position).lower()),
                "attitude": json.loads(json.dumps(attitude).lower())
            },
            "camera": {
                "format": format,
                "fov": fov,
                "exposure": exposure,
                "ray_tracing": ray_tracing,
                "size": {
                    "x": size[0],
                    "y": size[1]
                },
                "position": json.loads(json.dumps(camera_position).lower()),
                "rotation": {
                    "pitch": camera_rotation[0],
                    "roll": camera_rotation[1],
                    "yaw": camera_rotation[2]
                }
            },
            "mqtt": {
                "topic": self.topic_response
            },
            "cesium": cesium,
            "file": file_name
        }

        # Store the data in the capture data
        self.capture_data.append(data)

        # Publish the request
        self.client.publish_json(TOPIC_REQUEST, data)

    def on_callback (self, data: list) -> None:
        '''
        This method is called when the raw binary data from the image
        is called back by the topic. This will attempt to save the photo
        and write it into a file.
        '''
        
        # Get the metdata and make sure the file is valid
        meta_data: dict = self.capture_data.pop(0)
        self.file = meta_data["file"]
        format: str = meta_data["camera"]["format"]
        if not self.file.endswith("." + format):
            self.file += "." + format
        
        # Make sure the path exists
        if "/" in self.file:
            dir: str = "/".join(self.file.split("/")[:-1])
            if not os.path.exists(dir):
                os.makedirs(dir)

        # Overwrite the file
        with open(self.file, "wb") as f:
            # Write the raw data
            f.write(data)
            f.close

        # Print a success
        printer.success("Successfully saved image from simulation to file '%s'." % self.file)
        printer.success(self.topic_response)