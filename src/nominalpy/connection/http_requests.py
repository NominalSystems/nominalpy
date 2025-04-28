#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication
# to the public API. All code is under the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

"""
This module assists with helper functions for requesting data from the API,
ensuring the data is in the correct form, and handling errors.
"""

import requests
import json
import urllib3
from urllib3.util.retry import Retry
from ..utils import printer, NominalException
from .credentials import Credentials
import time

# Disable the insecure request warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _create_session() -> requests.Session:
    """
    Creates a new requests Session with retry logic and timeout configuration.
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # Max retry attempts
        backoff_factor=1,  # Wait 1s, 2s, 4s between retries
        status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP errors
        allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],  # Retry all methods
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.timeout = 60  # Set a reasonable timeout (in seconds)
    return session


def __http_request(
    credentials: Credentials, method: str, path: str, data: dict = {}
) -> dict:
    """
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

    :returns:               The JSON data from the API response, or None if no valid JSON
    :rtype:                 dict
    """
    # Define the URL and headers
    if "http" not in credentials.url:
        url = f"http://{credentials.url}{path}"
    else:
        url = f"{credentials.url}{path}"
    headers = {"Content-Type": "application/json", "x-api-key": credentials.access_key}
    params = {"session": credentials.get_session_id()}

    # Log the request
    printer.log("Attempting a %s request to '%s' with data: %s" % (method, url, data))

    # Prepare the request data
    json_data = json.dumps(data)

    # Create a new session for this request
    with _create_session() as session:
        try:
            # Use the session for the request
            if credentials.is_local:
                if method == "GET":
                    response = session.get(
                        url,
                        headers=headers,
                        data=json_data,
                        params=params,
                        timeout=session.timeout,
                    )
                elif method == "POST":
                    response = session.post(
                        url,
                        headers=headers,
                        data=json_data,
                        params=params,
                        timeout=session.timeout,
                    )
                elif method == "PUT":
                    response = session.put(
                        url,
                        headers=headers,
                        data=json_data,
                        params=params,
                        timeout=session.timeout,
                    )
                elif method == "PATCH":
                    response = session.patch(
                        url,
                        headers=headers,
                        data=json_data,
                        params=params,
                        timeout=session.timeout,
                    )
                elif method == "DELETE":
                    response = session.delete(
                        url,
                        headers=headers,
                        data=json_data,
                        params=params,
                        timeout=session.timeout,
                    )
            else:
                if method == "GET":
                    action = "get"
                elif method == "POST":
                    action = "new"
                elif method == "PUT":
                    action = "set"
                elif method == "PATCH":
                    action = "ivk"
                elif method == "DELETE":
                    action = "del"
                params["op"] = action
                response = session.post(
                    url,
                    headers=headers,
                    data=json_data,
                    params=params,
                    verify=False,
                    timeout=session.timeout,
                )

            # Check if the response is valid
            if response.status_code != 200:
                printer.error(response.text)
                if response.status_code == 403:
                    raise NominalException(
                        "Invalid Credentials: Access key is unauthorised to connect to the API."
                    )
                elif response.status_code == 404:
                    raise NominalException(
                        "Invalid Connection: The URL specified does not exist."
                    )
                elif response.status_code == 500:
                    raise NominalException(
                        "Invalid Connection: An internal server exception was thrown. Please try again later."
                    )
                elif response.status_code == 402:
                    raise NominalException(
                        "Invalid Connection: Your API key is not associated with a valid account. Please create an account and try again."
                    )
                else:
                    raise NominalException(
                        f"Error [{response.status_code}]: {response.text}"
                    )

            # Handle the response content
            if (
                response.text and response.text.strip()
            ):  # Check if there's non-empty content
                # Return the JSON data (or None)
                try:
                    if response.text != None and response.text != "":
                        return json.loads(response.text)
                except:
                    return response.text
                return None

        except requests.exceptions.ConnectionError as e:
            printer.error(f"Connection error: {str(e)}")
            time.sleep(2)  # Wait before retrying outside the retry mechanism
            raise
        except requests.exceptions.RequestException as e:
            printer.error(f"Request failed: {str(e)}")
            raise


def get(credentials: Credentials, path: str, data: dict = {}) -> dict:
    """
    Performs a GET request to the API with the specified path and data. This
    will return the JSON data from the response if the request was successful.
    """
    return __http_request(credentials, "GET", path, data)


def post(credentials: Credentials, path: str, data: dict = {}) -> dict:
    """
    Performs a POST request to the API with the specified path and data. This
    will return the JSON data from the response if the request was successful.
    """
    return __http_request(credentials, "POST", path, data)


def put(credentials: Credentials, path: str, data: dict = {}) -> dict:
    """
    Performs a PUT request to the API with the specified path and data. This
    will return the JSON data from the response if the request was successful.
    """
    return __http_request(credentials, "PUT", path, data)


def patch(credentials: Credentials, path: str, data: dict = {}) -> dict:
    """
    Performs a PATCH request to the API with the specified path and data. This
    will return the JSON data from the response if the request was successful.
    """
    return __http_request(credentials, "PATCH", path, data)


def delete(credentials: Credentials, path: str, data: dict = {}) -> dict:
    """
    Performs a DELETE request to the API with the specified path and data. This
    will return the JSON data from the response if the request was successful.
    """
    return __http_request(credentials, "DELETE", path, data)
