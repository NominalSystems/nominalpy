'''
        [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems
to aid with communication to the public API.
'''

from .request_helper import *
from .value_old import Value
from .object import Object
from .printer import *

'''
The message class is used for storing data about a particular
set of parameters using the inbuilt Messaging system.
'''
class Message (Object):

    __subscribed: bool = False

    def __init__(self, credentials: Credentials, id: str) -> None:
        '''
        TODO
        '''
        super().__init__(credentials, id, "message")

    def subscribe (self, interval: float = 10.0) -> bool:
        '''
        TODO
        '''
        # Construct the JSON body
        body: dict = {
            "guid": self.id,
            "interval": interval
        }

        # Create the data
        request_data: str = jsonify(body)

        # Create the response from the PATCH request and get the IDs
        response = put_request(self._Object__credentials, "database/message", data=request_data)
        if response == False:
            error("Failed to subscribe message to the database system.")
            return False
        self.__subscribed = True
        return True

    def fetch_range (self, min_time: float, max_time: float, *values) -> list:
        '''
        TODO
        '''

        # Throw an error if not subscribed
        if not self.__subscribed:
            error("Unable to fetch data. Ensure that this message has been subscribed to the database system.")
            return []

        # Construct the JSON body parameters
        body: dict = {
            "guid": self.id,
            "min_time": min_time,
            "max_time": max_time
        }
        if len(values) > 0:
            body["data"] = []
            for param in values:
                body["data"].append(param)

        # Create the data
        request_data: str = jsonify(body)

        # Create the response from the POST request and get the data
        response = post_request(self._Object__credentials, "query/database/message", data=request_data)
        return response

    def fetch (self, *values) -> list:
        '''
        TODO
        '''
        return self.fetch_range(0.0, 0.0, *values)