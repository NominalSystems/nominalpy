#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

"""
This module assists with helper functions for requesting
data from the API, ensuring the data is in the correct form,
and handling any errors.

Updated to be asynchronous using aiohttp for compatibility
with the async Simulation class.
"""

import json
import urllib3
import aiohttp
from ..utils import printer, NominalException
from .credentials import Credentials

# Disable the insecure request warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def __http_request_async(credentials: Credentials, method: str, path: str, data: dict = {}) -> dict:
    """
    Creates an asynchronous HTTP request to the API with the specified method, path,
    and data in the form of a JSON dictionary. Returns the JSON value from the response
    if the request was successful. Raises an exception if the request was not successful.

    :param credentials:     The credentials to access the API
    :type credentials:      Credentials
    :param method:          The HTTP method to use for the request
    :type method:           str
    :param path:            The path to the API endpoint
    :type path:             str
    :param data:            The data to send to the API
    :type data:             dict

    :returns:               The JSON data from the API response
    :rtype:                 dict
    """

    # Define the URL and headers
    if "http" not in credentials.url:
        url = f"http://{credentials.url}{path}"
    else:
        url = f"{credentials.url}{path}"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': credentials.access_key
    }
    params = {'session': "" if credentials.get_session_id() is None else credentials.get_session_id()}

    # Log the request
    printer.log(f"Attempting a {method} request to '{url}' with data: {data}")

    # Initialise the response to ensure it exists outside of conditional statements
    response = None
    resp_text = None

    session = aiohttp.ClientSession()

    # Create an aiohttp ClientSession
    try:
        # Build the request arguments
        # Use the json parameter to send JSON data
        # For local deployment
        if credentials.is_local:
            if method == 'GET':
                response = await session.get(url, headers=headers, params=params, json=data)
                try:
                    resp_text = await response.text()
                    # check if the response is valid inside the "async with" block
                    if response.status != 200:
                        __handle_http_error(response.status, resp_text)
                finally:
                    # Ensure the response is released
                    response.release()
            elif method == 'POST':
                response = await session.post(url, headers=headers, params=params, json=data)
                try:
                    resp_text = await response.text()
                    # check if the response is valid inside the "async with" block
                    if response.status != 200:
                        __handle_http_error(response.status, resp_text)
                finally:
                    # Ensure the response is released
                    response.release()
            elif method == 'PUT':
                response = await session.put(url, headers=headers, params=params, json=data)
                try:
                    resp_text = await response.text()
                    # check if the response is valid inside the "async with" block
                    if response.status != 200:
                        __handle_http_error(response.status, resp_text)
                finally:
                    # Ensure the response is released
                    response.release()
            elif method == 'PATCH':
                response = await session.patch(url, headers=headers, params=params, json=data)
                try:
                    resp_text = await response.text()
                    # check if the response is valid inside the "async with" block
                    if response.status != 200:
                        __handle_http_error(response.status, resp_text)
                finally:
                    # Ensure the response is released
                    response.release()
            elif method == 'DELETE':
                response = await session.delete(url, headers=headers, params=params, json=data)
                try:
                    resp_text = await response.text()
                    # check if the response is valid inside the "async with" block
                    if response.status != 200:
                        __handle_http_error(response.status, resp_text)
                finally:
                    # Ensure the response is released
                    response.release()
            else:
                raise NominalException(f"Unsupported HTTP method: {method}")

        # For cloud deployment
        else:
            if method == 'GET':
                action = "get"
            elif method == 'POST':
                action = "new"
            elif method == 'PUT':
                action = "set"
            elif method == 'PATCH':
                action = "ivk"
            elif method == 'DELETE':
                action = "del"
            else:
                raise NominalException(f"Unsupported HTTP method: {method}")
            params['op'] = action
            # Send the request with SSL verification disabled
            response = await session.post(url, headers=headers, params=params, json=data, ssl=False)
            try:
                resp_text = await response.text()
                # check if the response is valid inside the "async with" block
                if response.status != 200:
                    __handle_http_error(response.status, resp_text)
            finally:
                # Ensure the response is released
                response.release()

        # Return the JSON data (or None)
        try:
            if resp_text:
                return json.loads(resp_text)
        except json.JSONDecodeError:
            return resp_text  # Return raw text if JSON decoding fails
        return None
    finally:
        # Ensure the session is closed
        session.close()


def __handle_http_error(response_status: int, response_text: str):
    """
    Helper function to handle HTTP errors.

    :param response_status: The status of the aiohttp response object.
    :param response_text: The response text.
    """
    printer.error(response_text)
    if response_status == 403:
        raise NominalException("Invalid Credentials: Access key is unauthorized to connect to the API.")
    elif response_status == 404:
        raise NominalException("Invalid Connection: The URL specified does not exist.")
    elif response_status == 500:
        raise NominalException("Invalid Connection: An internal server error occurred. Please try again later.")
    elif response_status == 402:
        raise NominalException("Invalid Connection: Your API key is not associated with a valid account. Please create an account and try again.")
    else:
        raise NominalException(f'Error [{response_status}]: {response_text}')


async def get_async(credentials: Credentials, path: str, data: dict = {}) -> dict:
    """
    Performs an asynchronous GET request to the API with the specified path and data.
    Returns the JSON data from the response if the request was successful.

    :param credentials:     The credentials to access the API
    :type credentials:      Credentials
    :param path:            The path to the API endpoint
    :type path:             str
    :param data:            The data to send to the API (sent as JSON in the body)
    :type data:             dict

    :returns:               The JSON data from the API response
    :rtype:                 dict
    """
    return await __http_request_async(credentials, 'GET', path, data)


async def post_async(credentials: Credentials, path: str, data: dict = {}) -> dict:
    """
    Performs an asynchronous POST request to the API with the specified path and data.
    Returns the JSON data from the response if the request was successful.

    :param credentials:     The credentials to access the API
    :type credentials:      Credentials
    :param path:            The path to the API endpoint
    :type path:             str
    :param data:            The data to send to the API (sent as JSON in the body)
    :type data:             dict

    :returns:               The JSON data from the API response
    :rtype:                 dict
    """
    return await __http_request_async(credentials, 'POST', path, data)


async def put_async(credentials: Credentials, path: str, data: dict = {}) -> dict:
    """
    Performs an asynchronous PUT request to the API with the specified path and data.
    Returns the JSON data from the response if the request was successful.

    :param credentials:     The credentials to access the API
    :type credentials:      Credentials
    :param path:            The path to the API endpoint
    :type path:             str
    :param data:            The data to send to the API (sent as JSON in the body)
    :type data:             dict

    :returns:               The JSON data from the API response
    :rtype:                 dict
    """
    return await __http_request_async(credentials, 'PUT', path, data)


async def patch_async(credentials: Credentials, path: str, data: dict = {}) -> dict:
    """
    Performs an asynchronous PATCH request to the API with the specified path and data.
    Returns the JSON data from the response if the request was successful.

    :param credentials:     The credentials to access the API
    :type credentials:      Credentials
    :param path:            The path to the API endpoint
    :type path:             str
    :param data:            The data to send to the API (sent as JSON in the body)
    :type data:             dict

    :returns:               The JSON data from the API response
    :rtype:                 dict
    """
    return await __http_request_async(credentials, 'PATCH', path, data)


async def delete_async(credentials: Credentials, path: str, data: dict = {}) -> dict:
    """
    Performs an asynchronous DELETE request to the API with the specified path and data.
    Returns the JSON data from the response if the request was successful.

    :param credentials:     The credentials to access the API
    :type credentials:      Credentials
    :param path:            The path to the API endpoint
    :type path:             str
    :param data:            The data to send to the API (sent as JSON in the body)
    :type data:             dict

    :returns:               The JSON data from the API response
    :rtype:                 dict
    """
    return await __http_request_async(credentials, 'DELETE', path, data)
