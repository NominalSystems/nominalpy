'''
        [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems
to aid with communication to the public API.
'''

import requests
import urllib3
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


def get_request (credentials: Credentials, url: str, params: dict = {}) -> str:
    '''
    Creates a GET request with some suffix URL data and returns
    the result of the request in a text form. If there was an
    error, then a None will be returned. This requires valid
    credentials to be passed through.
    '''

    # Skip if missing credentials
    if credentials == None:
        raise Exception("Invalid Credentials: No valid credentials were passed into the GET requets.")

    # Create the GET request
    response = requests.get(
        credentials.url + url, 
        verify=False, 
        params=params, 
        headers = {'x-api-key': credentials.access_key, 'Content-Type': 'application/json'}
    )

    # Check if the request went through
    if response.status_code == 200:
        data = response.text
        return data
    
    # Throw an error
    raise create_web_exception(response.status_code)


def post_request (credentials: Credentials, url: str, params: dict = {}) -> str:
    '''
    Creates a POST request with some suffix URL data and returns
    the result of the request in a text form. If there was an
    error, then a None will be returned. This requires valid
    credentials to be passed through.
    '''

    # Skip if missing credentials
    if credentials == None:
        raise Exception("Invalid Credentials: No valid credentials were passed into the POST requets.")

    # Create the POST request
    response = requests.post(
        credentials.url + url, 
        verify=False, 
        params=params, 
        headers = {'x-api-key': credentials.access_key, 'Content-Type': 'application/json'}
    )

    # Check if the request went through
    if response.status_code == 200:
        data = response.text.replace('\"', "")
        return data

    # Throw an error
    raise create_web_exception(response.status_code)


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
        raise NominalException("Unknown Error: A communication link with the API is broken.")