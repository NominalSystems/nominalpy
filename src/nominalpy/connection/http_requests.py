#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

'''
This modules assists with having some helper functions for requesting
data from the API and ensuring the data is in the correct form, and
handling any errors.
'''

import requests, json
import urllib3
from ..utils import printer, NominalException
from .credentials import Credentials


# Disable the insecure request warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def __http_request(credentials: Credentials, method: str, path: str, data: dict = {}) -> dict:
    '''
    Creates a generic HTTP request to the API with the specified type, path
    and some data in the form of a JSON dictionary. This will return the JSON
    value from the response if the request was successful. It will throw an
    exception if the request was not successful.

    :param credentials:     The credentials to access the API
    :type credentials:      Credentials
    :param method:          The type of request to make to the API
    :type method:           str
    :param path:            The path to the API endpoint
    :type path:             str
    :param data:            The data to send to the API
    :type data:             dict

    :returns:               The JSON data from the API response
    :rtype:                 dict
    '''

    # Define the URL and headers
    if "http" not in credentials.url:
        url = f"http://{credentials.url}{path}"
    else:
        url = f"{credentials.url}{path}"
    headers = {'Content-Type': 'application/json', 'x-api-key': credentials.access_key}
    params = {'session': credentials.get_session_id() }

    # Log the request
    printer.log("Attempting a %s request to '%s' with data: %s" % (method, url, data))

    # If a local deployment
    if credentials.is_local:
        if method == 'GET':
            response = requests.get(url, headers=headers, data=json.dumps(data), params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=json.dumps(data), params=params)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, data=json.dumps(data), params=params)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, data=json.dumps(data), params=params)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, data=json.dumps(data), params=params)

    # If a cloud deployment
    else:
        if method == 'GET':
            action: str = "get"
        elif method == 'POST':
            action: str = "new"
        elif method == 'PUT':
            action: str = "set"
        elif method == 'PATCH':
            action: str = "ivk"
        elif method == 'DELETE':
            action: str = "del"
        params['op'] = action
        response = requests.post(url, headers=headers, data=json.dumps(data), params=params, verify=False)
    
    # Check if the response is valid
    if response.status_code != 200:
        printer.error(response.text)
        if response.status_code == 403:
            raise NominalException("Invalid Credentials: Access key is unauthorised to connect to the API.")
        elif response.status_code == 404:
            raise NominalException("Invalid Connection: The URL specified does not exist.")
        elif response.status_code == 500:
            raise NominalException("Invalid Connection: An internal server exception was thrown. Please try again later.")
        elif response.status_code == 402:
            raise NominalException("Invalid Connection: Your API key is not associated with a valid account. Please create an account and try again.")
        else:
            raise NominalException('Error [%d]: %s' % (response.status_code, response.text))
    
    # Return the JSON data (or None)
    try:
        if response.text != None and response.text != "": 
            return json.loads(response.text)
    except:
        return response.text
    return None


def get(credentials: Credentials, path: str, data: dict = {}) -> dict:
    '''
    Performs a GET request to the API with the specified path and data. This
    will return the JSON data from the response if the request was successful.

    :param credentials:     The credentials to access the API
    :type credentials:      Credentials
    :param path:            The path to the API endpoint
    :type path:             str
    :param data:            The data to send to the API
    :type data:             dict

    :returns:               The JSON data from the API response
    :rtype:                 dict
    '''

    return __http_request(credentials, 'GET', path, data)


def post(credentials: Credentials, path: str, data: dict = {}) -> dict:
    '''
    Performs a POST request to the API with the specified path and data. This
    will return the JSON data from the response if the request was successful.

    :param credentials:     The credentials to access the API
    :type credentials:      Credentials
    :param path:            The path to the API endpoint
    :type path:             str
    :param data:            The data to send to the API
    :type data:             dict

    :returns:               The JSON data from the API response
    :rtype:                 dict
    '''

    return __http_request(credentials, 'POST', path, data)


def put(credentials: Credentials, path: str, data: dict = {}) -> dict:
    '''
    Performs a PUT request to the API with the specified path and data. This
    will return the JSON data from the response if the request was successful.

    :param credentials:     The credentials to access the API
    :type credentials:      Credentials
    :param path:            The path to the API endpoint
    :type path:             str
    :param data:            The data to send to the API
    :type data:             dict

    :returns:               The JSON data from the API response
    :rtype:                 dict
    '''

    return __http_request(credentials, 'PUT', path, data)


def patch(credentials: Credentials, path: str, data: dict = {}) -> dict:
    '''
    Performs a PATCH request to the API with the specified path and data. This
    will return the JSON data from the response if the request was successful.

    :param credentials:     The credentials to access the API
    :type credentials:      Credentials
    :param path:            The path to the API endpoint
    :type path:             str
    :param data:            The data to send to the API
    :type data:             dict

    :returns:               The JSON data from the API response
    :rtype:                 dict
    '''

    return __http_request(credentials, 'PATCH', path, data)


def delete(credentials: Credentials, path: str, data: dict = {}) -> dict:
    '''
    Performs a DELETE request to the API with the specified path and data. This
    will return the JSON data from the response if the request was successful.

    :param credentials:     The credentials to access the API
    :type credentials:      Credentials
    :param path:            The path to the API endpoint
    :type path:             str
    :param data:            The data to send to the API
    :type data:             dict

    :returns:               The JSON data from the API response
    :rtype:                 dict
    '''

    return __http_request(credentials, 'DELETE', path, data)
