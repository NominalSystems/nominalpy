'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

The Object class represents an object within the simulation. Objects
can have data that can be set and returned. This wrapper ensures that
all data is cached and updated when required. Cached data is fetched
on an API call and if no simulation events have occurred, the data is
not fetched again.
'''

from .. import request_helper as rh
from ..credentials import Credentials
from ..printer import *
from ..objects.entity import Entity


class Object(Entity):

    '''
    A flag that defines whether the caching needs updated on the parameter.
    This will be triggered when a simulation is ticked.
    '''
    __update_required: bool = True

    '''
    A dictionary that holds all of the JSON data for the object that is
    fetched when the get value functions are called.
    '''
    __data: dict = None

    '''
    Defines the full Nominal class name of the object that has been fetched.
    This is updated when values are fetched.
    '''
    __type: str = None

    '''
    The API type defines the root object type of the class. This is either
    'object' for components and simulation objects or 'message' for messages.
    '''
    _api_type = "object"

    def __init__(self, credentials: Credentials, id: str, api_type: str = "object") -> None:
        '''
        The initialisation of the object must take in some API credentials,
        which control the access to the API, a unique GUID identifier
        associated with the simulation object and the type of requests that
        must be made.
        '''
        super().__init__(credentials=credentials, id=id)
        self._api_type = api_type

    def __require_update__ (self) -> None:
        '''
        When this function is called, from the simulation when a new tick is
        executed, this will ensure that the cached data is needed to be
        updated again from the API.
        '''
        self.__update_required = True

    def __get_object__ (self) -> None:
        '''
        This is an internal method that fetches all of the current simulation
        JSON data from the API and stores it locally in the cache. If the
        data does not require an update, it will skip this process.
        '''

        # Check if the update has not occurred
        if not self.__update_required:
            return
        
        # Perform the request on the data
        request_data: str = rh.jsonify({
            "guid": self.id
        })
        response = rh.post_request(self._credentials, "query/" + self._api_type, data=request_data)
        
        # Check for a valid response and update the data
        if response == None or response == {}:
            error("Failed to retrieve data from %s '%s'." % (self._api_type, self.id))
        else:
            self.__update_required = False
            self.__type = response["type"]
            self.__data = response["data"]
    
    def get_type (self) -> str:
        '''
        This method returns the full simulation type class name, including the
        namespace of the object. This requires a call to fetch the object.
        '''
        self.__get_object__()
        return self.__type

    def get_values (self, *values) -> dict:
        '''
        This method returns a JSON dictionary of parameters passed within the
        function. The values can be a set of parameter names to fetch and the
        JSON data associated with the object's data will be returned at the
        current simulation time.
        '''

        # Attempt to get the current object data or throw an error.
        self.__get_object__()
        if self.__data == None:
            error("No data available on the component.")
            return {}
        
        # If no values, return all of the data
        if len(values) == 0:
            return self.__data
        
        # Parse the data to only fetch the data requested by the user
        data: dict = {}
        for param in values:
            if param in self.__data:
                data[param] = self.__data[param]
        return data

    def get_value (self, param: str) -> str:
        '''
        This method returns the JSON data associated with the parameter
        passed in at the current time in the simulation.
        '''

        # Fetch all values and parse only the one in the parameter
        data: dict = self.get_values(param)
        if data == {}:
            error("Failed to find parameter '%s' in class '%s'. Please check the documentation for valid variables." % (param, self.__type))
            return None
        return data[param]
    
    def set_values (self, **kwargs) -> bool:
        '''
        This method sets a series of parameters on the object based on a
        dictionary keyword argument set. Any number of parameters can be
        set. If the values are incorrect, then the parameter will not be
        set.
        '''

        # Construct the JSON body
        body: dict = {
            "guid": self.id
        }

        # Check if no values exists and set the data
        if len(kwargs) == 0:
            error("No values to set.")
            return False
        
        # Clean up if using the 'set_value' function
        if 'param_name' in kwargs:
            kwargs[kwargs['param_name']] = kwargs['param_value']
            del kwargs['param_name']
            del kwargs['param_value']
        
        # Update the data in the body
        body["data"] = kwargs

        # Create the data
        request_data: str = rh.jsonify(body)

        # Create the response from the PATCH request and get the IDs
        response = rh.patch_request(self._credentials, self._api_type, data=request_data)
        if response == False:
            error("Failed to set data on %s." % self._api_type)
            return False
        
        # Update the flag for needing to get values
        self.__require_update__()
        return True
    
    def set_value (self, param: str, value: str) -> bool:
        '''
        This method attempts to set a particular parameter to a particular
        value, provided that the value is in the correct JSON format. If
        the parameter name or the value is incorrect, the value will not be
        set and return a failure.
        '''
        return self.set_values(param_name=param, param_value=value)

    def delete (self) -> bool:
        '''
        This method will delete the current object from the simulation and
        remove access to all objects associated with this.
        '''
        # Construct the JSON body
        request_data: str = rh.jsonify(
            {
                "guid": self.id
            }
        )

        # Create the response
        response = rh.delete_request(self._credentials, self._api_type, data=request_data)
        if response == True:
            success("Successfully deleted object '%s' of type '%s'." % (self.id, self.__type))
            self.id = None
            self.__type = None
            self.__update_required = True
            self.__data = None
            return True
        
        # Failed to delete
        else:
            error("Failed to delete object '%s'." % self.id)
            return False
    
    def __str__ (self) -> str:
        '''
        The automated cast of this object to a string will only return the
        GUID identifier of the object.
        '''
        return self.id