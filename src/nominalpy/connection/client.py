"""
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2025.
"""

import aiohttp, asyncio, json
from typing import Optional, Dict, List, Union
from functools import wraps
from collections import defaultdict
from nominalpy.utils import printer, NominalException

"""
Defines the wait time for the client to wait before making another request.
"""
CLIENT_WAIT_TIME: float = 0.1


class Client:

    def __init__(
        self,
        url: str = "https://api.nominalsys.com",
        token: str = None,
        max_requests_per_client: int = 50,
        max_total_concurrent_requests: int = 100,
    ) -> None:
        """
        Initialize the client with the base URL and optional token and port.
        These will attempt to be used in requests if provided.

        :param url: The base URL for the API.
        :type url: str
        :param token: The token to use for requests, when a public API is available.
        :type token: str
        :param port: The port to use for requests, when a public API is available.
        :type port: int
        :param max_requests_per_client: The maximum number of requests per client.
        :type max_requests_per_client: int
        :param max_total_concurrent_requests: The maximum number of total concurrent requests.
        :type max_total_concurrent_requests: int
        """

        # Remove the trailing slash from the URL if it exists
        if not url.endswith("/"):
            url += "/"
        self.base_url: str = url

        # Set the token and port
        self.token = token

        # Set the maximum requests per client and total concurrent requests
        if max_requests_per_client < 1:
            max_requests_per_client = 1
        self.max_requests_per_client = max_requests_per_client
        if max_total_concurrent_requests < 1:
            max_total_concurrent_requests = 1
        self.max_total_concurrent_requests = max_total_concurrent_requests

        # Create the semaphore and client pool
        self.client_pool: List[aiohttp.ClientSession] = []
        self.client_requests: Dict[aiohttp.ClientSession, int] = defaultdict(int)
        self.semaphore = asyncio.Semaphore(self.max_total_concurrent_requests)

    async def _get_client(self) -> aiohttp.ClientSession:
        """
        Attempt to get an available client or create a new one if needed.
        This is an internal function and should not be called directly.

        :return: An available client or a new client.
        :rtype: aiohttp.ClientSession
        """

        # Check for an available client
        for client in self.client_pool:
            if (
                not client.closed
                and self.client_requests[client] < self.max_requests_per_client
            ):
                return client

        # Check if a new client can be created
        if sum(self.client_requests.values()) < self.max_total_concurrent_requests:
            new_client = aiohttp.ClientSession()
            self.client_pool.append(new_client)
            printer.log(f"Created a new client for the pool ({len(self.client_pool)})")
            return new_client

        # Wait for an available client otherwise
        while True:
            for client in self.client_pool:
                if (
                    not client.closed
                    and self.client_requests[client] < self.max_requests_per_client
                ):
                    return client
            await asyncio.sleep(CLIENT_WAIT_TIME)

    async def _cleanup_clients(self) -> None:
        """
        Close clients with no active requests.
        This is an internal function and should not be called directly.
        """
        for client in self.client_pool[:]:
            if self.client_requests[client] == 0 and not client.closed:
                await client.close()
                self.client_pool.remove(client)
                del self.client_requests[client]

    async def _request(
        self, method: str, endpoint: str, data: Optional[Union[str, list, dict]] = None
    ) -> dict:
        """
        Perform the core async request function with multi-client support. This can
        take a method, endpoint, and optional data to send with the request. This
        is an async function and should not be called directly.

        :param method: The method to use for the request.
        :type method: str
        :param endpoint: The endpoint to use for the request.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: Optional[dict]

        :return: The result of the request.
        :rtype: dict
        """

        # Get the client and increment the requests
        client = await self._get_client()
        self.client_requests[client] += 1

        # Create the header
        headers = {"Accept": "application/json"}
        timeout = aiohttp.ClientTimeout(total=10)

        # Convert data based on type
        body = None
        if isinstance(data, str):
            headers["Content-Type"] = "text/plain"
            body = data.encode("utf-8") if data else None
        elif isinstance(data, (list, dict)):
            headers["Content-Type"] = "application/json"
            body = data
        elif data is None:
            headers["Content-Type"] = "application/json"
            body = None
        else:
            raise ValueError("Data must be a string, list, dictionary, or None")

        # Ensure the body is sent as a single packet by encoding it explicitly if needed
        if isinstance(body, (list, dict)):
            headers["Content-Type"] = "application/json"
            headers["Content-Length"] = str(
                len(json.dumps(body))
            )  # Set Content-Length header

        # Create the URL
        url: str = f"{self.base_url}{endpoint}"

        # Make the request
        async with self.semaphore:

            # Attempt to make the request
            try:
                # Log the request
                printer.log(
                    f"Attempting a {method} request to '{url}' with data: '{body if body else "None"}'."
                )

                # Prepare the request data and result
                async with client.request(
                    method,
                    url,
                    json=(
                        body if isinstance(body, (list, dict)) else None
                    ),  # Use json parameter for serializable data
                    data=(
                        body if not isinstance(body, (list, dict)) else None
                    ),  # Use data for non-serializable data
                    headers=headers,
                    timeout=timeout,
                ) as response:

                    # Return the result, which is just the content from the response
                    content: str = await response.read()

                    # Get the status from the result
                    status: dict = {
                        "version": response.version,
                        "reason": response.reason,
                        "method": response.method,
                        "status": response.status,
                        "content": len(content) > 0,
                        "headers": dict(response.headers),
                    }

                    # Print the status
                    printer.log(f"Request response: {status}")

                    # If the status is not 200, raise an exception
                    if response.status != 200:
                        raise NominalException(
                            f"Request failed with status {response.status}: {response.reason}"
                        )

                    # Try to parse the content as JSON
                    try:
                        if content != None and content != "":
                            result = json.loads(content)
                    except:
                        result = content.decode("utf-8")

                    # If the result is empty, return 'None'
                    if result == "":
                        result = None

            # Handle client errors
            except aiohttp.ClientError as e:
                raise NominalException(f"Request failed: {str(e)}")

            # Handle Nominal Exceptions
            except NominalException as e:
                raise e

            # Cleanup the clients and decrement the requests
            finally:
                self.client_requests[client] -= 1
                asyncio.create_task(self._cleanup_clients())

            # Return the result at the end of the function
            return result

    async def get(self, endpoint: str, data: Optional[dict] = None) -> dict:
        """
        Perform an async GET request to the specified endpoint. This will
        return the result of the request as a dictionary.

        :param endpoint: The endpoint to use for the request.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: Optional[dict]

        :return: The result of the request.
        :rtype: dict
        """
        return await self._request("GET", endpoint, data)

    async def post(self, endpoint: str, data: Optional[dict] = None) -> dict:
        """
        Perform an async POST request to the specified endpoint. This will
        return the result of the request as a dictionary.

        :param endpoint: The endpoint to use for the request.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: Optional[dict]

        :return: The result of the request.
        :rtype: dict
        """
        return await self._request("POST", endpoint, data)

    async def delete(self, endpoint: str, data: Optional[dict] = None) -> dict:
        """
        Perform an async DELETE request to the specified endpoint. This will
        return the result of the request as a dictionary.

        :param endpoint: The endpoint to use for the request.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: Optional[dict]

        :return: The result of the request.
        :rtype: dict
        """
        return await self._request("DELETE", endpoint, data)

    @classmethod
    def create_local(
        cls,
        port: int = 25565,
        max_requests_per_client: int = 50,
        max_total_concurrent_requests: int = 100,
    ) -> "Client":
        """
        Create a local client with the specified port and request limits.

        :param port: The port to use for the local client.
        :type port: int
        :param max_requests_per_client: The maximum number of requests per client.
        :type max_requests_per_client: int
        :param max_total_concurrent_requests: The maximum number of total concurrent requests.
        :type max_total_concurrent_requests: int

        :return: A new local client.
        :rtype: Client
        """
        return Client(
            url=f"http://localhost:{port}",
            max_requests_per_client=max_requests_per_client,
            max_total_concurrent_requests=max_total_concurrent_requests,
        )
