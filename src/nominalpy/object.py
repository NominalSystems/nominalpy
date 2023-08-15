from .request_helper import *
from .credentials import Credentials
from .printer import *

class Object:

    id: str = None

    # Stores the crendetials for the message
    __credentials: Credentials = None

    __update_required: bool = True

    __data: dict = None

    __type: str = None

    __api_type = "object"

    def __init__(self, credentials: Credentials, id: str, api_type: str = "object") -> None:
        '''
        TODO
        '''
        self.id = id
        self.__credentials = credentials
        self.__api_type = api_type

    def __require_update__ (self) -> None:
        '''
        TODO
        '''
        self.__update_required = True

    def __get_object__ (self) -> None:
        '''
        TODO
        '''
        if not self.__update_required:
            return
        data = {
            "guid": self.id
        }
        request_data: str = jsonify(data)
        response = post_request(self.__credentials, "query/" + self.__api_type, data=request_data)
        if response == None or response == {}:
            error("Failed to retrieve data from %s '%s'." % (self.__api_type, self.id))
        else:
            self.__update_required = False
            self.__type = response["type"]
            self.__data = response["data"]

    def get_values (self, *values) -> dict:
        '''
        TODO
        '''
        self.__get_object__()
        if self.__data == None:
            error("No data available on the component.")
            return {}
        if len(values) == 0:
            return self.__data
        data: dict = {}
        for param in values:
            if param in self.__data:
                data[param] = self.__data[param]
        return data

    def get_value (self, param: str) -> str:
        '''
        TODO
        '''
        data: dict = self.get_values(param)
        if data == {}:
            error("Failed to find parameter '%s' in class '%s'." % (param, self.__type))
            return None
        return data[param]
    
    def set_values (self, **kwargs) -> bool:
        '''
        TODO
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
        request_data: str = jsonify(body)

        # Create the response from the PATCH request and get the IDs
        response = patch_request(self.__credentials, self.__api_type, data=request_data)
        if response == False:
            error("Failed to set data on %s." % self.__api_type)
            return False
        
        # Update the flag for needing to get values
        self.__require_update__()
        return True
    
    def set_value (self, param: str, value: str) -> bool:
        '''
        TODO
        '''
        return self.set_values(param_name=param, param_value=value)

    def delete (self) -> bool:
        '''
        TODO
        '''
        # Construct the JSON body
        request_data: str = jsonify(
            {
                "guid": self.id
            }
        )

        # Create the response
        response = delete_request(self.__credentials, self.__api_type, data=request_data)
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