#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2023.

import pandas as pd
from copy import deepcopy
from ..connection import Credentials, http, helper
from .object import Object
from ..utils import printer


class Message (Object):
    '''
    The Message class is able to store a series of parameters and data
    associated with the particular message type. The message is also 
    able to be subscribed to a database and data can be fetched from
    the database system to pull back message data over the simulation
    time.
    '''

    __subscribed: bool = False
    '''Defines whether the message has already been subscribed to the database system or not.'''

    def __init__(self, credentials: Credentials, id: str) -> None:
        '''
        Initialises the message with a set of credentials and a
        unique GUID identifier for the message.

        :param credentials: The Credentials object that is used for the API
        :type credentials:  Credentials
        :param id:          The unique identifier for the Entity in a GUID format
        :type id:           str
        '''

        super().__init__(credentials, id, "message")

    def subscribe (self, interval: float = 10.0) -> bool:
        '''
        This method will subscribe the message to the database
        system and ensure that the data is stored over time. The
        interval specifies the time in seconds between recordings
        of the data in the database.

        :param interval:    The simulation second interval that the data should be stored in the database
        :type interval:     float

        :returns:           A successful subscription flag if the message is now logged to the database
        :rtype:             bool
        '''

        # Construct the JSON body
        body: dict = {
            "guid": self.id,
            "interval": interval
        }

        # Create the data
        request_data: str = helper.jsonify(body)

        # Create the response from the PATCH request and get the IDs
        response = http.put_request(self._credentials, "database/message", data=request_data)
        if response == False:
            printer.error("Failed to subscribe message to the database system.")
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

        :param min_time:    The minimum time in simulation seconds to pull the data from the database
        :type min_time:     float
        :param max_time:    The maximum time in simulation seconds to pull the data from the database
        :type max_time:     float
        :param values:      An optional set of parameters as a list that can filter the data
        :type values:       list

        :returns:           A list containing all data time-stamped within the range
        :rtype:             list
        '''

        # Throw an error if not subscribed
        if not self.__subscribed:
            printer.error("Unable to fetch data. Ensure that this message has been subscribed to the database system.")
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
        request_data: str = helper.jsonify(body)

        # Create the response from the POST request and get the data
        response = http.post_request(self._credentials, "query/database/message", data=request_data)

        # Parse the data into a new list
        data: list = []
        for r in response:
            entry: dict = {}
            entry["time"] = r["time"]
            entry_data = {}
            for d in r["data"].keys():
                entry_data[d] = helper.deserialize(r["data"][d])
            entry["data"] = entry_data
            data.append(entry)

        return data

    def fetch (self, *values) -> list:
        '''
        This method fetches the data, in the form of a JSON array,
        from the database assuming that it has been subscribed to
        the database system. The returned data will include a time
        stamp and the JSON data of the message at that time.

        :param values:      An optional set of parameters as a list that can filter the data
        :type values:       list

        :returns:           A list containing all data time-stamped from the database
        :rtype:             list
        '''

        return self.fetch_range(0.0, 0.0, *values)

    def fetch_df (self, *values) -> pd.DataFrame:
        '''
        Fetch the data from the simulation and return the results 
        as a pandas DataFrame for easy handling and analysis.

        :param values:  An optional set of parameters as a list that can filter the data
        :type values:   list

        :return:        A dataframe containing the values of the subscribed messages for the simulation
        :rtype:         pandas.DataFrame
        '''

        data = self.fetch(*values)
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

        :param credentials: The API credentials to correctly call the simulation
        :type credentials:  Credentials
        :param simulation:  The simulation unique ID in a GUID format
        :type simulation:   str
        :param id:          The unique ID of the message to fetch in a GUID format
        :type id:           str
        :param min_time:    The minimum time to fetch data from the database from in seconds
        :type min_time:     float
        :param max_time:    The maximum time to fetch data from the database from in seconds
        :type max_time:     float
        :param values:      An optional set of parameters as a list that can filter the data
        :type values:       list

        :returns:           A list containing all data time-stamped from the database
        :rtype:             list
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
        request_data: str = helper.jsonify(body)

        # Create the response from the POST request and get the data
        response = http.post_request(credentials, "query/database/message", data=request_data)

        # Parse the data into a new list
        data: list = []
        for r in response:
            entry: dict = {}
            entry["time"] = r["time"]
            entry_data = {}
            for d in r["data"].keys():
                entry_data[d] = helper.deserialize(r["data"][d])
            entry["data"] = entry_data
            data.append(entry)

        return data
    
    @classmethod
    def message_fetch (cls, credentials: Credentials, simulation: str, id: str, *values) -> list:
        '''
        This method fetches the data, in the form of a JSON array,
        from the database assuming that it has been subscribed to
        the database system. The returned data will include a time
        stamp and the JSON data of the message at that time. This is 
        a class level method and takes in some credentials and an ID 
        of the message, rather than being an object level method.

        :param credentials: The API credentials to correctly call the simulation
        :type credentials:  Credentials
        :param simulation:  The simulation unique ID in a GUID format
        :type simulation:   str
        :param id:          The unique ID of the message to fetch in a GUID format
        :type id:           str
        :param values:      An optional set of parameters as a list that can filter the data
        :type values:       list

        :returns:           A list containing all data time-stamped from the database
        :rtype:             list
        '''

        return Message.message_fetch_range(credentials, simulation, id, 0.0, 0.0, *values)

    def __bool__ (self) -> bool:
        '''
        Returns the self testing of the validity of this object
        and whether the object is valid.

        :returns:   A flag whether the ID exists
        :rtype:     bool
        '''

        return self.id is not None
