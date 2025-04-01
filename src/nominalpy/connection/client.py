"""
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2025.
"""

import aiohttp, asyncio, json
from typing import Optional, Dict, List
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
        url: str = "https://api.nominalsys.com/",
        token: str = None,
        port: int = 25565,
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
        if url.endswith("/"):
            url = url[:-1]

        # Set the token and port
        self.token = token
        self.port = port

        # Make the base url include the port
        if "https://" in url and port == 443:
            self.base_url = url + "/"
        elif "http://" in url and port == 80:
            self.base_url = url + "/"
        else:
            self.base_url = f"{url}:{port}/"

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
        self, method: str, endpoint: str, data: Optional[dict] = None
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

        # Add in the token as the 'x-api-key' header
        if self.token:
            if not data:
                data = {}
            data["x-api-key"] = self.token

        # Make the request
        async with self.semaphore:

            # Attempt to make the request
            try:
                # Log the request
                printer.log(
                    f"Attempting a {method} request to '{endpoint}' with data: {data}"
                )

                # Prepare the request data and result
                async with client.request(
                    method, f"{self.base_url}{endpoint}", json=data
                ) as response:

                    # Return the result, which is just the content from the response
                    content: str = await response.read()

                    # Get the status from the result
                    status: dict = {
                        "version": response.version,
                        "reason": response.reason,
                        "method": response.method,
                        "status": response.status,
                        "content": content,
                        "headers": dict(response.headers),
                    }

                    # Print the status
                    printer.log(f"Request response: {status}")

                    # Try to parse the content as JSON
                    try:
                        if content != None and content != "":
                            result = json.loads(content)
                    except:
                        result = content

            # Handle client errors
            except aiohttp.ClientError as e:
                raise NominalException(f"Request failed: {str(e)}")

            # Cleanup the clients and decrement the requests
            finally:
                self.client_requests[client] -= 1
                asyncio.create_task(self._cleanup_clients())

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

    @staticmethod
    def _sync_wrapper(f):
        """
        Create a decorator to make async functions callable synchronously.
        This is a static method and should not be called directly.
        """

        @wraps(f)
        def wrapper(*args, **kwargs):
            return asyncio.run(f(*args, **kwargs))

        return wrapper

    @_sync_wrapper
    async def get_sync(self, endpoint: str, data: Optional[dict] = None) -> dict:
        """
        Create a synchronous GET request to the specified endpoint. This will
        return the result of the request as a dictionary.

        :param endpoint: The endpoint to use for the request.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: Optional[dict]

        :return: The result of the request.
        :rtype: dict
        """
        return await self.get(endpoint, data)

    @_sync_wrapper
    async def post_sync(self, endpoint: str, data: Optional[dict] = None) -> dict:
        """
        Create a synchronous POST request to the specified endpoint. This will
        return the result of the request as a dictionary.

        :param endpoint: The endpoint to use for the request.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: Optional[dict]

        :return: The result of the request.
        :rtype: dict
        """
        return await self.post(endpoint, data)

    @_sync_wrapper
    async def delete_sync(self, endpoint: str, data: Optional[dict] = None) -> dict:
        """
        Create a synchronous DELETE request to the specified endpoint. This will
        return the result of the request as a dictionary.

        :param endpoint: The endpoint to use for the request.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: Optional[dict]

        :return: The result of the request.
        :rtype: dict
        """
        return await self.delete(endpoint, data)

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
            url="localhost/",
            port=port,
            max_requests_per_client=max_requests_per_client,
            max_total_concurrent_requests=max_total_concurrent_requests,
        )
