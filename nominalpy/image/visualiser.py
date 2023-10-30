from ..mqtt import MqttClient
import json
from ..printer import *

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

    def __init__(self) -> None:
        '''
        Initialises the class and sets up the Mqtt client with the
        appropriate callback functions for the response.
        '''

        self.client: MqttClient = MqttClient()
        self.client.connect(wait=True)
        self.client.add_callback(self.topic_response, self.on_callback)

    def capture (self, position: dict = None, attitude: dict = None, epoch: dict = None, file: str = "capture", format: str = "png") -> None:
        '''
        Attempts to capture the simulation at a particular point in time, with
        a position, attitude, epoch and other properties.
        '''

        # Provide some default data for the missing values
        if position == None:
            position = { "x": 0.0, "y": 0.0, "z": 0.0 }
        if attitude == None:
            attitude = { "x": 0.0, "y": 0.0, "z": 0.0 }
        if epoch == None:
            dt = datetime.datetime.now()
            epoch = { "year": dt.year, "month": dt.month, "day": dt.day, "hour": dt.hour, "minute": dt.minute, "second": dt.second }

        # Construc the JSON formatted data
        data = {
            "epoch": json.loads(json.dumps(epoch).lower()),
            "position": json.loads(json.dumps(position).lower()),
            "attitude": json.loads(json.dumps(attitude).lower()),
            "camera": {
                "format": format,
                "fov": 50.0
            },
            "mqtt": {
                "topic": self.topic_response
            },
            "file": file
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
        file: str = meta_data["file"]
        format: str = meta_data["camera"]["format"]
        if not file.endswith("." + format):
            file += "." + format

        # Overwrite the file
        with open(file, "wb") as f:
            # Write the raw data
            f.write(data)
            f.close

        # Print a success
        success("Successfully saved image from simulation to file '%s'." % file)