from .request_helper import *
from .credentials import Credentials
from .printer import *
import json, re

class Object:

    id: str = None

    # Stores the crendetials for the message
    __credentials: Credentials = None

    __update_required: bool = True

    __data: dict = None

    def __init__(self, credentials: Credentials, id: str) -> None:
        self.id = id
        self.__credentials = credentials

    def __get_object__ (self) -> None:
        if not self.__update_required:
            return
        data = {
            "guid": self.id
        }
        log("Attempting to retrieve new object data from the simulation for object '%s'." % self.id)
        request_data: str = jsonify(data, False)
        response = post_request(self.__credentials, "object", data=request_data)
        if response != None and len(response) > 0:
            log("Successfully retrieved new object data for object '%s'." % self.id)
            self.__update_required = False
            data_with_quotes = re.sub(r'(\w+)', r'"\1"', response)
            print(response)
            print("")
            print(data_with_quotes)
            self.__data = json.loads(data_with_quotes)

    def get_values (self, *values) -> dict:
        self.__get_object__()
        if self.__data != None:
            if len(values) == 0:
                return self.__data["values"]
            data: dict = {}
            for param in values:
                if param in self.__data["values"]:
                    data[param] = self.__data["values"][param]   
            return data
        return {}