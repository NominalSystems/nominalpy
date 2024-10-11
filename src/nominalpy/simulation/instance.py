#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

from ..connection import Credentials, http_requests
from ..utils import NominalException, helper

class Instance:
    '''
    The instance class is a base class that is used to define any simulation object
    that exists within the simulation. It is able to fetch and set data on the API,
    invoke methods and can be tracked by the API. This class is used to define the
    base functionality for the other types, but should not be created by the user
    itself.
    '''

    __data: dict = None
    '''Defines the data dictionary that is fetched from the API.'''

    __type: str = None
    '''Defines the type of the object that is fetched from the API.'''

    _refresh_cache: bool = True
    '''Defines whether the cache needs to be refreshed or not.'''

    _credentials: Credentials = None
    '''Specifies the credentials for accessing the API correctly.'''

    id: str = None
    '''Defines the unique GUID identifier of the object. This needs to be in the correct GUID format.'''
    
    def __init__ (self, credentials: Credentials, id: str) -> None:
        '''
        Initialises the instance with the credentials and the ID of the object.

        :param credentials:     The credentials to access the API
        :type credentials:      Credentials
        :param id:              The GUID ID of the object
        :type id:               str
        '''

        # Check if the credentials and ID are valid
        if not credentials or not credentials.is_valid():
            raise NominalException("Invalid credentials provided on an Instance.")
        if not helper.is_valid_guid(id):
            raise NominalException(f"Invalid GUID ID '{id}' provided on an Instance.")

        # Set the values and default data
        self.id = id
        self._credentials = credentials
        self.__data = None
        self.__type = None
        self._refresh_cache = True

    def _get_data (self) -> None:
        '''
        This function is used to fetch the data from the API and store it in the
        object. This is used to ensure that the data is fetched correctly and is
        up to date.
        '''

        # Skip if the cache does not need to be refreshed
        if not self._refresh_cache:
            return
        
        # Fetch all data and then set the cache to false
        self.__data = http_requests.get(self._credentials, "object", {'guid': self.id})
        self._refresh_cache = False

    def _require_refresh (self) -> None:
        '''
        This function is used to set the flag for refreshing the cache to true.
        It can be overriden by a base class if additional functionality is required.
        '''

        self._refresh_cache = True
    
    def get_type (self) -> str:
        '''
        Returns the type of the object that is fetched from the API. This is the
        full type, including the namespace and the class name. If the type has not
        been fetched, it will fetch it from the API.

        :returns:   The type of the object
        :rtype:     str
        '''

        # If there is no type, find it
        if not self.__type:
            self.__type = http_requests.patch(self._credentials, "object", {"guid": self.id, "name": "GetType"})
        return self.__type

    def get (self, param: str) -> any:
        '''
        Fetches a parameter from the object that is stored in the API. This will
        return the parameter if it exists and will raise an exception if it does
        not exist. If the data has not been fetched, it will fetch the data from
        the API.

        :param param:   The parameter to fetch from the object
        :type param:    str

        :returns:       The parameter value from the object
        :rtype:         any
        '''

        # Ensures that the data is fetched correctly
        self._get_data()

        # Check if the param is in the data
        if param not in self.__data:
            raise NominalException(f"Parameter '{param}' not found in object '{self.id}' of type '{self.get_type()}'.")
        return helper.deserialize(self.__data[param])

    def get_all (self) -> dict:
        '''
        Returns all of the data that is stored in the object. This will return
        the full dictionary of the object and will fetch the data if it has not
        been fetched yet.

        :returns:   The full dictionary of the object
        :rtype:     dict
        '''
            
        # Ensures that the data is fetched correctly
        self._get_data()
        return self.__data
    
    def set (self, **kwargs) -> None:
        '''
        Sets the parameters of the object that is stored in the API. This will
        take in a dictionary of parameters and values and will update the object
        with the new values. This will raise an exception if the data is invalid.

        :param kwargs:  The parameters and values to set on the object
        :type kwargs:   dict
        '''

        # For each of the key values, serialize the data
        for key in kwargs:
            kwargs[key] = helper.serialize(kwargs[key])

        # Add the put request to update the data
        http_requests.put(self._credentials, "object", {'guid': self.id, 'data': kwargs })

        # Ensure that the cache is refreshed for the next get
        self._require_refresh()

    def invoke (self, function: str, *args) -> any:
        '''
        Invoke a function on the object that is stored in the API. This will take
        in the function name and the arguments to pass to the function. This will
        return the response from the function call, if there is a response.

        :param function:    The function name to invoke on the object
        :type function:     str
        :param args:        The arguments to pass to the function
        :type args:         any

        :returns:           The response from the function call
        :rtype:             any
        '''

        # For each of the arguments, serialize the data
        args = list(args)
        for i in range(len(args)):
            args[i] = helper.serialize(args[i])

        # Create the request data
        request = {
            'guid': self.id,
            'name': function,
        }

        # only add 'args' to the request if args is not empty
        if args:
            request['args'] = list(args)

        # Create the response from the PATCH request and get the IDs
        response = http_requests.patch(self._credentials, "object", request)
        
        # Update the flag for needing to get values
        self._require_refresh()
        return response
        
    def __str__ (self) -> str:
        '''
        The automated cast of this object to a string will only return the
        GUID identifier of the object.

        :returns:   The formatted ID from the object
        :rtype:     str
        '''

        return self.id