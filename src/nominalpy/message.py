'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

The Message class is able to store a series of parameters and data
associated with the particular message type. The message is also 
able to be subscribed to a database and data can be fetched from
the database system to pull back message data over the simulation
time.
'''

from .request_helper import *
from .object import Object
from .printer import *

class Message (Object):

    '''
    Defines whether the message has already been subscribed to
    the database system or not.
    '''
    __subscribed: bool = False

    def __init__(self, credentials: Credentials, id: str) -> None:
        '''
        Initialises the message with a set of credentials and a
        unique GUID identifier for the message.
        '''
        super().__init__(credentials, id, "message")

    def subscribe (self, interval: float = 10.0) -> bool:
        '''
        This method will subscribe the message to the database
        system and ensure that the data is stored over time. The
        interval specifies the time in seconds between recordings
        of the data in the database.
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
        This method fetches the data, in the form of a JSON array,
        from the database assuming that it has been subscribed to
        the database system. The returned data will include a time
        stamp and the JSON data of the message at that time. This
        method also takes in a filter of the minimum and maximum
        simulation time in seconds to search for.
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
        This method fetches the data, in the form of a JSON array,
        from the database assuming that it has been subscribed to
        the database system. The returned data will include a time
        stamp and the JSON data of the message at that time.
        '''
        return self.fetch_range(0.0, 0.0, *values)