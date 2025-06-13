"""
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2025.
"""

from typing import Optional, Dict, Union
from nominalpy.utils import printer, NominalException
import asyncio, aiohttp, json, atexit
from typing import Optional, Union, Dict


class Client:
    """
    A simple client to handle HTTP requests to an API.
    Each simulation ID processes requests sequentially using its own session.
    """

    def __init__(self, url: str = "https://api.nominalsys.com", token: str = None):
        """
        Initialize the client with a base URL and optional token.

        :param url: The base URL for the API.
        :param token: Authentication token for requests.
        """
        self.base_url = url.rstrip("/") + "/"
        self.token = token
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
        self.queues: Dict[str, asyncio.Queue] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self._closed = False
        atexit.register(self._sync_cleanup)

    def _sync_cleanup(self):
        """
        Synchronous cleanup for program exit.
        """
        if self._closed:
            return
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(self._close())
            if not loop.is_closed():
                loop.close()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._close())
            loop.close()
        except Exception:
            pass

    def __del__(self):
        """
        Ensure cleanup when the object is garbage-collected.
        """
        if not self._closed:
            self._sync_cleanup()

    async def _close(self):
        """
        Close all sessions and cancel tasks.
        """
        if self._closed:
            return
        self._closed = True
        for id, task in self.tasks.items():
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        for id, session in self.sessions.items():
            if not session.closed:
                await session.close()
        self.sessions.clear()
        self.queues.clear()
        self.tasks.clear()

    async def _process_requests(self, id: str):
        """
        Process requests for a simulation ID sequentially.

        :param id: The simulation ID.
        """
        queue = self.queues.get(id)
        if not queue:
            return
        if id not in self.sessions:
            self.sessions[id] = aiohttp.ClientSession()
        session = self.sessions[id]

        while not self._closed:
            try:
                async with asyncio.timeout(60.0):
                    method, endpoint, data, future = await queue.get()

                if session.closed:
                    if not future.done():
                        future.set_exception(NominalException("Session closed"))
                    queue.task_done()
                    continue

                headers = {"Accept": "application/json"}
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                timeout = aiohttp.ClientTimeout(total=30.0)

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
                    if not future.done():
                        future.set_exception(
                            ValueError("Data must be a string, list, dict, or None")
                        )
                    queue.task_done()
                    continue

                url = f"{self.base_url}{endpoint.lstrip('/')}"

                # Print the request details for debugging
                printer.log(f"Requesting {method} {url} with data: {body}")

                for attempt in range(3):
                    try:
                        async with session.request(
                            method,
                            url,
                            json=body if isinstance(body, (list, dict)) else None,
                            data=body if not isinstance(body, (list, dict)) else None,
                            headers=headers,
                            timeout=timeout,
                        ) as response:
                            content = await response.read()
                            if response.status != 200:
                                raise NominalException(
                                    f"Request failed: {response.status} {response.reason}"
                                )
                            result = None
                            if content:
                                try:
                                    result = json.loads(content)
                                except json.JSONDecodeError:
                                    result = content.decode("utf-8")

                            # Print the response details for debugging
                            printer.log(f"Response from {method} {url}: {result}.")

                            if not future.done():
                                future.set_result(result)
                            break
                    except (aiohttp.ClientError, NominalException) as e:
                        if attempt < 2:
                            await asyncio.sleep(1)
                            continue
                        if not future.done():
                            future.set_exception(
                                NominalException(f"Request failed: {e}")
                            )
                queue.task_done()
            except asyncio.TimeoutError:
                if queue.empty() and self._closed:
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                if "future" in locals() and not future.done():
                    future.set_exception(e)
                try:
                    if "queue" in locals():
                        queue.task_done()
                except:
                    pass

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[str, list, dict]] = None,
        id: str = "default",
    ) -> dict:
        """
        Make an HTTP request for a given simulation ID.

        :param method: HTTP method (GET, POST, etc.).
        :param endpoint: API endpoint.
        :param data: Data to send with the request.
        :param id: Simulation ID for sequential processing.
        :return: Response data as a dictionary or string.
        """
        if self._closed:
            raise RuntimeError("Client is closed")
        if id not in self.queues:
            self.queues[id] = asyncio.Queue()
            self.tasks[id] = asyncio.create_task(self._process_requests(id))

        future = asyncio.Future()
        await self.queues[id].put((method, endpoint, data, future))
        try:
            async with asyncio.timeout(200.0):
                return await future
        except asyncio.TimeoutError:
            if not future.done():
                future.set_exception(NominalException("Request timed out"))
            raise

    async def get(
        self, endpoint: str, data: Optional[dict] = None, id: str = "default"
    ) -> dict:
        """
        Perform an async GET request to the specified endpoint. This will
        return the result of the request as a dictionary.

        :param endpoint: The endpoint to use for the request.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: Optional[dict]
        :param id: The ID of the context for the client, if applicable.
        :type id: str

        :return: The result of the request.
        :rtype: dict
        """
        return await self._request("GET", endpoint, data, id=id)

    async def post(
        self, endpoint: str, data: Optional[dict] = None, id: str = "default"
    ) -> dict:
        """
        Perform an async POST request to the specified endpoint. This will
        return the result of the request as a dictionary.

        :param endpoint: The endpoint to use for the request.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: Optional[dict]
        :param id: The ID of the context for the client, if applicable.
        :type id: str

        :return: The result of the request.
        :rtype: dict
        """
        return await self._request("POST", endpoint, data, id=id)

    async def delete(
        self, endpoint: str, data: Optional[dict] = None, id: str = "default"
    ) -> dict:
        """
        Perform an async DELETE request to the specified endpoint. This will
        return the result of the request as a dictionary.

        :param endpoint: The endpoint to use for the request.
        :type endpoint: str
        :param data: The data to send with the request.
        :type data: Optional[dict]
        :param id: The ID of the context for the client, if applicable.
        :type id: str

        :return: The result of the request.
        :rtype: dict
        """
        return await self._request("DELETE", endpoint, data, id=id)

    @classmethod
    def create_local(cls, port: int = 25565) -> "Client":
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
        return Client(url=f"http://localhost:{port}")
