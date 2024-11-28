# ---------------------------------------------------------------------------------------------------------------------------- #
# Copyright 2024 (c) Nominal Systems, Pty Ltd. All Rights Reserved
# See the 'LICENSE' file at the root of this git repository
# ---------------------------------------------------------------------------------------------------------------------------- #
import re, json, time, datetime, aiohttp
# ---------------------------------------------------------------------------------------------------------------------------- #
class Session:
    '''
    This class represents a HTTP(s) connection that allows the user to make requests to the Nominal API.
    '''
    # ------------------------------------------------------------------------------------------------------------------------ #
    def __init__ (self, host: str, port: int = None, guid: str = None) -> None:
        '''
        Connects to a Nominal API session.
        '''

        # create global HTTP client
        global SESSION_HTTP
        if SESSION_HTTP is None: SESSION_HTTP = aiohttp.ClientSession()

        # set the default HTTP settings
        self.guid = guid
        self.headers = { "Content-Type": "application/json" }

        # create a new HTTP(s) connection
        try:
            if re.match(r"^http?:[\\\/]{2}[a-zA-Z0-9\\\.\/]*[^\\\/]$", host) is not None:
                self.port = 80 if port is None else port
                self.host = host
            elif re.match(r"^https?:[\\\/]{2}[a-zA-Z0-9\\\.\/]*[^\\\/]$", host) is not None:
                self.port = 443 if port is None else port
                self.host = host
            else:
                raise Exception(f"NominalSystems: Invalid parameter host '{host}'")
        except:
            raise Exception(f"NominalSystems: Failed to connect to '{host}:{port}'")
    # ------------------------------------------------------------------------------------------------------------------------ #
    async def get(self, endpoint: str, body: any = None) -> str:
        '''
        Sends a HTTP request to the session.
        '''

        return await self.request("GET", endpoint, body)
    # ------------------------------------------------------------------------------------------------------------------------ #
    async def put(self, endpoint: str, body: any = None) -> str:
        '''
        Sends a HTTP request to the session.
        '''
        return await self.request("PUT", endpoint, body)
    # ------------------------------------------------------------------------------------------------------------------------ #
    async def post(self, endpoint: str, body: any = None) -> str:
        '''
        Sends a HTTP request to the session.
        '''
        return await self.request("POST", endpoint, body)
    # ------------------------------------------------------------------------------------------------------------------------ #
    async def patch(self, endpoint: str, body: any = None) -> str:
        '''
        Sends a HTTP request to the session.
        '''
        return await self.request("PATCH", endpoint, body)
    # ------------------------------------------------------------------------------------------------------------------------ #
    async def delete(self, endpoint: str, body: any = None) -> str:
        '''
        Sends a HTTP request to the session.
        '''
        return await self.request("DELETE", endpoint, body)
    # ------------------------------------------------------------------------------------------------------------------------ #
    async def request(self, method: str, endpoint: str, body: any = None) -> any:
        '''
        Sends a HTTP request to the session.
        '''

        # check if session is running
        if not await self.is_running():
            raise Exception(f"NominalSystems: Already disconnected")

        # check for invalid request endpoint
        if re.match(r"^[a-zA-Z0-9-_]*$", endpoint) is None:
            raise Exception(f"NominalSystems: Invalid parameter endpoint '{endpoint}'")

        # generate URL from method and endpoint
        url = f"/{endpoint}"
        match method:
            case "GET":
                if "x-api-key" in self.headers:
                    url = f"/v1.0/{endpoint}?op=get"
                    method = "POST"
            case "PUT":
                if "x-api-key" in self.headers:
                    url = f"/v1.0/{endpoint}?op=set"
                    method = "POST"
            case "POST":
                if "x-api-key" in self.headers:
                    url = f"/v1.0/{endpoint}?op=new"
                    method = "POST"
            case "PATCH":
                if "x-api-key" in self.headers:
                    url = f"/v1.0/{endpoint}?op=ivk"
                    method = "POST"
            case "DELETE":
                if "x-api-key" in self.headers:
                    url = f"/v1.0/{endpoint}?op=del"
                    method = "POST"
            case _:
                raise Exception(f"NominalSystems: Invalid parameter method '{method}'")

        # add session guid to URL as a query parameter
        if self.guid is not None:
            url += f"&session={self.guid}"

        # send HTTP request to server and return response
        global SESSION_HTTP
        response = await SESSION_HTTP.request(method, f"{self.host}:{self.port}{url}",
            data    = json.dumps(body),
            headers = self.headers
        )
        response_body = (await response.content.read()).decode("utf-8")
        if response.status == 400:
            raise Exception(f"NominalSystems: {response_body}")
        if response.status == 402:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status == 403:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status != 200:
            raise Exception(f"NominalSystems: Unknown error")
        return json.loads(response_body) if len(response_body) > 0 else None
    # ------------------------------------------------------------------------------------------------------------------------ #
    async def is_running(session: "Session"):
        '''
        Is 'True' if the session is running.
        '''

        # check for invalid parameters
        if session is None:
            raise Exception("NominalSystems: Invalid parameter session 'None'")

        # check if session has already ended
        if session.host is None:
            return False

        # check if session is a local session
        if not "x-api-key" in session.headers:
            return True

        # query if cloud session is still running
        global SESSION_HTTP
        response = await SESSION_HTTP.post(f"{session.host}:{session.port}/v1.0/session?op=get",
            data    = json.dumps({ "guid": session.guid }),
            headers = session.headers
        )
        response_body = (await response.content.read()).decode("utf-8")
        if response.status == 400:
            raise Exception(f"NominalSystems: {response_body}")
        if response.status == 402:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status == 403:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status != 200:
            raise Exception(f"NominalSystems: Unknown error")
        return json.loads(response_body)["status"] == "RUNNING"
    # ------------------------------------------------------------------------------------------------------------------------ #
    @staticmethod
    async def list_sessions(key: str) -> list["Session"]:
        '''
        [STATIC] Returns all running cloud sessions.
        '''

        # create global HTTP client
        global SESSION_HTTP
        if SESSION_HTTP is None: SESSION_HTTP = aiohttp.ClientSession()

        # list all available cloud sessions
        headers = { "Content-Type": "application/json", "x-api-key": key }
        response = await SESSION_HTTP.post("https://api.nominalsys.com/v1.0/session?op=get", headers=headers)
        response_body = json.loads((await response.content.read()).decode("utf-8"))
        if response.status == 400:
            raise Exception(f"NominalSystems: {response_body}")
        if response.status == 402:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status == 403:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status != 200:
            raise Exception(f"NominalSystems: Unknown error")

        # return all currently running sessions
        results = []
        for item in response_body:
            if item["status"] == "RUNNING":
                result = Session("https://api.nominalsys.com", None, item["guid"])
                result.headers["x-api-key"] = key
                results.append(result)
        return results
    # ------------------------------------------------------------------------------------------------------------------------ #
    @staticmethod
    async def create_session(key: str, version: str = None, duration: int = None) -> "Session":
        '''
        [STATIC] Creates a new cloud session.
        '''

        # create global HTTP client
        global SESSION_HTTP
        if SESSION_HTTP is None: SESSION_HTTP = aiohttp.ClientSession()

        # create a new cloud session
        session = Session("https://api.nominalsys.com")
        session.headers["x-api-key"] = key
        session.guid = json.loads(await session.post("/v1.0/session", json.dumps({
            "version": "1.0" if version is None else version,
            "duration": 900 if duration is None else duration
        })))["guid"]

        # wait for session to start running
        start_time = datetime.datetime.now()
        while (datetime.datetime.now() - start_time).total_seconds() < 300:
            if (await session.is_running()):
                return session
            time.sleep(1)
        raise Exception("NominalSystems: Pending")
    # ------------------------------------------------------------------------------------------------------------------------ #
    @staticmethod
    async def destroy_session(session: "Session") -> None:
        '''
        [STATIC] Destroys a cloud session.
        '''

        # create global HTTP client
        global SESSION_HTTP
        if SESSION_HTTP is None: SESSION_HTTP = aiohttp.ClientSession()

        # check for invalid parameters
        if session is None:
            raise Exception("NominalSystems: Invalid parameter session 'None'")

        # check if session is still running
        if not await session.is_running():
            return

        # check if session is a local session
        if not "x-api-key" in session.headers:
            session.delete("")
            session.host = None
            session.port = None
            session.guid = None
            session.headers = {}
            return

        # destroy a cloud session with session guid
        response = await SESSION_HTTP.post(f"{session.host}:{session.port}/v1.0/session?op=del",
            data    = json.dumps({ "guid": session.guid }),
            headers = session.headers
        )
        response_body = json.loads((await response.content.read()).decode("utf-8"))
        if response.status == 400:
            raise Exception(f"NominalSystems: {response_body}")
        if response.status == 402:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status == 403:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status != 200:
            raise Exception(f"NominalSystems: Unknown error")
        session.host = None
        session.port = None
        session.guid = None
        session.headers = {}
    # ------------------------------------------------------------------------------------------------------------------------ #