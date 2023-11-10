'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

This code assists with having some helper functions for requesting
data from the API and ensuring the data is in the correct form.
'''

import requests, json
import urllib3
from .printer import *
from .credentials import Credentials
from .exception import NominalException

# Disable the insecure request warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def validate_credentials (credentials: Credentials) -> None:
    '''
    Creates a GET request to test if the credentials are valid by
    calling the root directory of the URL passed through the credentials.
    This can be used to validate whether the API is live.
    '''

    # Skip if missing credentials
    if credentials == None:
        return False

    # Create the GET request
    try:
        response = requests.get(
            credentials.url, 
            verify=False,
            headers = {'x-api-key': credentials.access_key, 'Content-Type': 'application/json'}
        )
    
    # In the case of an invalid request
    except:
        raise NominalException("Invalid Credentials: The URL specified does not exist.")
    
    # Check the response codes
    if response.status_code != 200:
        raise create_web_exception(response.status_code)


def handle_request_data (response: requests.Response) -> dict:
    '''
    Handles the standard request data created from a HTTP
    web request. This will attempt to return a JSON or throw
    a web 
    '''

    # Skip if no response
    if response == None:
        raise Exception("Invalid response passed into 'handle_request_data'.")
    
    # Check if the request was valid and return the json data
    if response.status_code == 200:
        if response.text == "":
            return {}
        data = json.loads(response.text)
        return data
    
    # Throw an error if not
    error("Invalid request with status code %d." % response.status_code)
    raise create_web_exception(response.status_code)


def get_request (credentials: Credentials, url: str, params: dict = {}) -> dict:
    '''
    Creates a GET request with some suffix URL data and returns
    the result of the request in a JSON form. If there was an
    error, then a None will be returned. This requires valid
    credentials to be passed through.
    '''

    # Skip if missing credentials
    if credentials == None:
        raise Exception("Invalid Credentials: No valid credentials were passed into the GET requets.")
    
    # Add the session ID parameter
    if credentials.session_id != None:
        params["session_id"] = credentials.session_id

    # Create the GET request
    log("Attempting a GET request '/%s' with parameters: %s" % (url, params))
    response = requests.get(
        credentials.url + url, 
        verify=False, 
        params=params, 
        headers = {'x-api-key': credentials.access_key, 'Content-Type': 'application/json'}
    )

    # Handle the response
    return handle_request_data(response)


def post_request (credentials: Credentials, url: str, data: str = None, params: dict = {}) -> dict:
    '''
    Creates a POST request with some suffix URL data and returns
    the result of the request in a JSON form. If there was an
    error, then a None will be returned. This requires valid
    credentials to be passed through.
    '''

    # Skip if missing credentials
    if credentials == None:
        raise Exception("Invalid Credentials: No valid credentials were passed into the POST requets.")
    
    # Add the session ID parameter
    if credentials.session_id != None:
        params["session_id"] = credentials.session_id

    # Create the POST request
    log("Attempting a POST request '/%s' with data: %s" % (url, data))
    response = requests.post(
        credentials.url + url, 
        verify=False, 
        params=params,
        data=data,
        headers = {'x-api-key': credentials.access_key, 'Content-Type': 'application/json'}
    )

    # Handle the response
    return handle_request_data(response)


def put_request (credentials: Credentials, url: str, data: str = None, params: dict = {}) -> dict:
    '''
    Creates a PUT request with some suffix URL data and returns
    the result of the request in a JSON form. If there was an
    error, then a None will be returned. This requires valid
    credentials to be passed through.
    '''

    # Skip if missing credentials
    if credentials == None:
        raise Exception("Invalid Credentials: No valid credentials were passed into the POST requets.")
    
    # Add the session ID parameter
    if credentials.session_id != None:
        params["session_id"] = credentials.session_id

    # Create the PUT request
    log("Attempting a PUT request '/%s' with data: %s" % (url, data))
    response = requests.put(
        credentials.url + url, 
        verify=False, 
        params=params,
        data=data,
        headers = {'x-api-key': credentials.access_key, 'Content-Type': 'application/json'}
    )

    # Handle the response
    return handle_request_data(response)

def patch_request (credentials: Credentials, url: str, data: str = None, params: dict = {}) -> dict:
    '''
    Creates a PATCH request with some suffix URL data and returns
    the result of the request in a JSON form. If there was an
    error, then a None will be returned. This requires valid
    credentials to be passed through.
    '''

    # Skip if missing credentials
    if credentials == None:
        raise Exception("Invalid Credentials: No valid credentials were passed into the POST requets.")
    
    # Add the session ID parameter
    if credentials.session_id != None:
        params["session_id"] = credentials.session_id

    # Create the PATCH request
    log("Attempting a PATCH request '/%s' with data: %s" % (url, data))
    response = requests.patch(
        credentials.url + url, 
        verify=False, 
        params=params,
        data=data,
        headers = {'x-api-key': credentials.access_key, 'Content-Type': 'application/json'}
    )

    # Handle the response
    return handle_request_data(response)

def delete_request (credentials: Credentials, url: str, data: str = None, params: dict = {}) -> dict:
    '''
    Creates a DELETE request with some suffix URL data and returns
    the result of the request in a JSON form. If there was an
    error, then a None will be returned. This requires valid
    credentials to be passed through.
    '''

    # Skip if missing credentials
    if credentials == None:
        raise Exception("Invalid Credentials: No valid credentials were passed into the POST requets.")
    
    # Add the session ID parameter
    if credentials.session_id != None:
        params["session_id"] = credentials.session_id

    # Create the DELETE request
    log("Attempting a DELETE request '/%s' with data: %s" % (url, data))
    response = requests.delete(
        credentials.url + url, 
        verify=False, 
        params=params,
        data=data,
        headers = {'x-api-key': credentials.access_key, 'Content-Type': 'application/json'}
    )

    # Handle the response
    return handle_request_data(response)

def jsonify (data: dict, array: bool = False) -> str:
    '''
    Converts a particular data as a dictionary to string
    using the JSON payload and has an optional parameter
    to wrap the data inside of an array.
    '''
    if array:
        return "[%s]" %  json.dumps(data)
    return json.dumps(data)

def is_valid_guid (guid: str) -> bool:
    '''
    Determines if a parsed GUID, as a string,
    is valid. This will ensure that it is of
    the correct format.
    '''
    empty: str = "00000000-0000-0000-0000-000000000000"
    if guid == empty: return False
    if len(guid) != len(empty): return False
    if guid[8] != empty[8]: return False
    if guid[13] != empty[13]: return False
    if guid[18] != empty[18]: return False
    if guid[23] != empty[23]: return False
    return True

def create_web_exception (code: int) -> NominalException:
    '''
    This method creates an exception based on the status code
    that exists. This is useful for any status code that is not
    200, which is an OK status.
    '''
    if code == 200:
        return None
    elif code == 403:
        raise NominalException("Invalid Credentials: Access key is unauthorised to connect to the API.")
    elif code == 404:
        raise NominalException("Invalid Connection: The URL specified does not exist.")
    else:
        raise NominalException("Unknown Error: A communication link with the API is broken. Status Code: %d" % code)