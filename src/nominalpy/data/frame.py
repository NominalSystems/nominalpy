#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

from __future__ import annotations
import json, os
from .. import NominalException
from matplotlib import pyplot as plt


class DataFrame:
    '''
    The DataFrame class is able to store a series of parameters and data associated
    with a particular simulation instance. This class is a pure data class and is
    not able to invoke any methods. It is able to store the data in a structured
    format and is able to be exported to a JSON format.
    '''

    __raw: dict = {}
    '''Defines the raw data that is fetched from the API.'''

    type: str = ""
    '''Defines the object type that was used for this DataFrame.'''

    id: str = ""
    '''Defines the unique GUID identifier of the object. This needs to be in the correct GUID format.'''

    fields: list = []
    '''Defines the fields that are associated with the DataFrame.'''

    data: list = []
    '''Defines the data that is associated with the DataFrame.'''

    def __init__ (self, data: dict) -> None:
        '''
        Initialises the DataFrame with the data that is fetched from the API. This must be
        created using the JSON data that is fetched from the API and is able to be exported
        back to the API in the same format.

        :param data:    The data that is fetched from the API
        :type data:     dict
        '''

        # Reset the data
        self.id = ""
        self.type = ""
        self.fields = []
        self.data = []
        self.__raw = data

        # Fetch the header values
        if "ID" in data:
           self.id = data["ID"]
        if "Type" in data:
            self.type = data["Type"]
        self.type = data["Type"]
        if "Data" not in data:
            raise NominalException("DataFrame Data not found in data.")
        
        # Data should be an array of arrays
        data = list(data["Data"])
        if len(data) == 0:
            raise NominalException("DataFrame Data is empty.")
        self.fields = data[0]

        # Loop through the data
        for i in range(1, len(data)):
            self.data.append(data[i])
    
    @classmethod
    def load (cls, path: str) -> DataFrame:
        '''
        Loads a DataFrame from a file path and returns the DataFrame object. This is a
        class method and does not require an instance to be created.

        :param path:    The path to the file that contains the DataFrame
        :type path:     str

        :returns:       The DataFrame object that is loaded from the file
        :rtype:         DataFrame
        '''

        # Check if the path is not valid and throw exception
        if not path or not os.path.exists(path):
            raise NominalException("Invalid path provided to load DataFrame.")
        return DataFrame(json.loads(path))

    def get_times (self) -> list:
        '''
        Returns the time values that are associated with the DataFrame. This is a helper
        function that is able to fetch the time values from the DataFrame, where each
        value is in seconds.

        :returns:   The time values that are associated with the DataFrame in seconds
        :rtype:     list
        '''

        # Ensure that the time is casted as a float
        return [float(x) for x in self.get_values("Time")]
    
    def get_values (self, parameter: str) -> list:
        '''
        Returns the values that are associated with a particular parameter in the DataFrame.
        This is a helper function that is able to fetch the values associated with a particular
        parameter in the DataFrame.

        :param parameter:   The parameter to fetch the values for
        :type parameter:    str

        :returns:           The values that are associated with the parameter
        :rtype:             list
        '''

        # Check if the parameter does not exist
        if parameter not in self.fields:
            raise NominalException(f"Parameter '{parameter}' not found in DataFrame.")
        
        # Fetch the index and data associated with it
        index = self.fields.index(parameter)
        return [row[index] for row in self.data]

    def plot (self, title="Simulation Data", params=None) -> None:
        '''
        Creates a quick plot of the DataFrame data. This will plot the data in a simple
        line plot format and will display the data in a single plot or multiple plots
        depending on the parameters provided. The following formats for the parameters 
        will work:

        params = "MyParam"                    -> will plot 'MyParam' against Time in a single plot
        params = ["MyParam1", "MyParam2"]     -> will plot 'MyParam1' and 'MyParam2' against Time in a single plot
        params = [["MyParam1"], ["MyParam2"]] -> will plot 'MyParam1' and 'MyParam2' against Time in separate plots

        :param title:   The title of the plot
        :type title:    str
        :param params:  The parameters to plot
        :type params:   str or list
        '''

        # Ensure params is initialized to an empty list if not provided
        if params is None:
            params = []

        # Check if params is a single string (single parameter case)
        if isinstance(params, str):
            params = [params]  # Convert to a list to handle uniformly

        # Check if params is a list of lists (multiple plots case)
        if all(isinstance(item, list) for item in params):
            _, axs = plt.subplots(len(params), 1, figsize=(8, len(params) * 4))
            # Ensure axs is always a list (even if there's only one subplot)
            if len(params) == 1:
                axs = [axs]
            
            for ax, param_list in zip(axs, params):
                for parameter in param_list:
                    ax.plot(self.get_times(), self.get_values(parameter), label=parameter)
                ax.set(xlabel="Time [s]", ylabel="Value", title=title)
                ax.grid()
                ax.legend()
        else:
            # Handle the case where params is a flat list
            _, ax = plt.subplots()
            for parameter in params:
                ax.plot(self.get_times(), self.get_values(parameter), label=parameter)
            ax.set(xlabel="Time [s]", ylabel="Value", title=title)
            ax.grid()
            ax.legend()
        
        # Display the plots on the screen
        plt.tight_layout()
        plt.show()

    def export (self) -> dict:
        '''
        Exports the DataFrame to a dictionary format that is able to be exported to the API.
        This will return the DataFrame in the same format that is fetched from the API.

        :returns:   The DataFrame in a dictionary format
        :rtype:     dict
        '''
        return self.__raw
    
    def save (self, path: str) -> None:
        '''
        Saves the DataFrame to a file path in a JSON format. This will save the DataFrame
        in a JSON format that is able to be loaded back into the DataFrame class.

        :param path:    The path to save the DataFrame to
        :type path:     str
        '''
        with open(path, "w") as f:
            f.write(self.__str__())
    
    def __str__ (self) -> str:
        '''
        Converts the DataFrame to a string format that is able to be exported to a JSON format.

        :returns:   The DataFrame in a string format
        :rtype:     str
        '''
        return json.dumps(self.export(), indent=4)