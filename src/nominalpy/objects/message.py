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
import pandas as pd
from copy import deepcopy
from ..http.http_request import *
from ..http.credentials import Credentials
from ..objects.object import Object
from ..printer import *


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
        response = put_request(self._credentials, "database/message", data=request_data)
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
        response = post_request(self._credentials, "query/database/message", data=request_data)
        return response

    def fetch (self, *values) -> list:
        '''
        This method fetches the data, in the form of a JSON array,
        from the database assuming that it has been subscribed to
        the database system. The returned data will include a time
        stamp and the JSON data of the message at that time.
        '''
        return self.fetch_range(0.0, 0.0, *values)

    def fetch_df(self, *values) -> pd.DataFrame:
        """
        Fetch the data from the simulation and return the results as a pandas DataFrame for easy handling and analysis

        :param values: The message names desired to be returned from the simulation
        :return: A dataframe containing the values of the subscribed messages for the simulation
        """
        data = self.fetch(values)
        # Define a variable containing the name of the time data returned from the API
        time_col_name = "time"
        # Add the data from the simulation, handling multi-dimensional and single-dimension data variables
        data_new = []
        for x in data:
            packet = x["data"]
            # Create a copy of the packet that can be manipulated without losing the original data
            packet_new = deepcopy(packet)
            for key, value in packet.items():
                # If the data item is a dictionary, it indicates that the variable is multi-dimensional
                if isinstance(value, dict):
                    # Add each component of a multi-dimensional variable to their own column
                    for key2, value2 in value.items():
                        # Create a new key for the element of the multi-dimensional variable
                        key_new = f"{key}_{key2}"
                        # Add the element to the new packet
                        packet_new[key_new] = value2
                    # Remove the original data from the new data packet to avoid data duplication
                    packet_new.pop(key, None)
                # Else the data is a single-dimension, and so we leave the new packet as is for this value
            # Add the new packet to a container so that it can be added to a DataFrame
            data_new.append(packet_new)
        # Create the dataframe
        df = pd.DataFrame(data_new)
        # Add the time column
        df.loc[:, "time"] = [x[time_col_name] for x in data]
        # Reorder the time column to be the first column
        df = df[[time_col_name] + [col for col in df if col != time_col_name]]
        return df

    @classmethod
    def message_fetch_range (cls, credentials: Credentials, simulation: str, id: str, min_time: float, max_time: float, *values) -> list:
        '''
        This method fetches the data, in the form of a JSON array,
        from the database assuming that it has been subscribed to
        the database system. The returned data will include a time
        stamp and the JSON data of the message at that time. This
        method also takes in a filter of the minimum and maximum
        simulation time in seconds to search for. This is a class
        level method and takes in some credentials and an ID of the
        message, rather than being an object level method.
        '''

        # Construct the JSON body parameters
        body: dict = {
            "guid": id,
            "simulation": simulation,
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
        response = post_request(credentials, "query/database/message", data=request_data)
        return response
    
    @classmethod
    def message_fetch (cls, credentials: Credentials, simulation: str, id: str, *values) -> list:
        '''
        This method fetches the data, in the form of a JSON array,
        from the database assuming that it has been subscribed to
        the database system. The returned data will include a time
        stamp and the JSON data of the message at that time. This is 
        a class level method and takes in some credentials and an ID 
        of the message, rather than being an object level method.
        '''
        return Message.message_fetch_range(credentials, simulation, id, 0.0, 0.0, *values)

    def __bool__(self) -> bool:
        """
        Return the self testing of the validity of this object
        """
        return self.id is not None
