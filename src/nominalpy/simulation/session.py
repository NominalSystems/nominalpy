# ---------------------------------------------------------------------------------------------------------------------------- #
# Copyright 2024 (c) Nominal Systems, Pty Ltd. All Rights Reserved
# See the 'LICENSE' file at the root of this git repository
# ---------------------------------------------------------------------------------------------------------------------------- #
import re, json, time, datetime, requests, http.client
# ---------------------------------------------------------------------------------------------------------------------------- #

class Session:
    '''
    This class represents a HTTP(s) connection that allows the user to make requests to the Nominal API.
    '''
    # ------------------------------------------------------------------------------------------------------------------------ #
    def __init__ (self, host: str, port: int = None, session: str = None) -> None:
        '''
        Connects to a Nominal API session.
        '''

        # configure default HTTP settings
        self._session = session
        self._headers = { "Content-Type": "application/json" }

        # create a new HTTP(s) session connection
        if re.match(r"^http?:[\\\/]{2}[a-zA-Z0-9\\\.\/]*[^\\\/]$", host) is not None:
            port = 80 if port is None else port
            self._client = http.client.HTTPConnection(host[7:], port)
        elif re.match(r"^https?:[\\\/]{2}[a-zA-Z0-9\\\.\/]*[^\\\/]$", host) is not None:
            port = 443 if port is None else port
            self._client = http.client.HTTPSConnection(host[8:], port)
        else: raise Exception(f"invalid parameter 'host': {host}")
    # ------------------------------------------------------------------------------------------------------------------------ #
    def get(self, endpoint: str, body: any = None) -> str:
        '''
        Sends a HTTP request to the session.
        '''
        return self.request("GET", endpoint, body)
    # ------------------------------------------------------------------------------------------------------------------------ #
    def put(self, endpoint: str, body: any = None) -> str:
        '''
        Sends a HTTP request to the session.
        '''
        return self.request("PUT", endpoint, body)
    # ------------------------------------------------------------------------------------------------------------------------ #
    def post(self, endpoint: str, body: any = None) -> str:
        '''
        Sends a HTTP request to the session.
        '''
        return self.request("POST", endpoint, body)
    # ------------------------------------------------------------------------------------------------------------------------ #
    def patch(self, endpoint: str, body: any = None) -> str:
        '''
        Sends a HTTP request to the session.
        '''
        return self.request("PATCH", endpoint, body)
    # ------------------------------------------------------------------------------------------------------------------------ #
    def delete(self, endpoint: str, body: any = None) -> str:
        '''
        Sends a HTTP request to the session.
        '''
        return self.request("DELETE", endpoint, body)
    # ------------------------------------------------------------------------------------------------------------------------ #
    def request(self, method: str, endpoint: str, body: any = None) -> any:
        '''
        Sends a HTTP request to the session.
        '''

        # check for invalid parameters
        if re.match(r"^[\\\/][a-zA-Z0-9\\\.\/]*[^\\\/]$", endpoint) is None:
            raise Exception(f"invalid parameter 'endpoint': {endpoint}")

        # generate URL from method and endpoint
        match method:
            case "GET":
                url = f"/{endpoint}"
                if not "x-api-key" in self._headers: url += "?op=get"; method = "POST"
            case "PUT":
                url = f"/{endpoint}"
                if not "x-api-key" in self._headers: url += "?op=set"; method = "POST"
            case "POST":
                url = f"/{endpoint}"
                if not "x-api-key" in self._headers: url += "?op=new"; method = "POST"
            case "PATCH":
                url = f"/{endpoint}"
                if not "x-api-key" in self._headers: url += "?op=ivk"; method = "POST"
            case "DELETE":
                url = f"/{endpoint}"
                if not "x-api-key" in self._headers: url += "?op=del"; method = "POST"
            case _:
                raise Exception(f"invalid parameter 'method': {method}")

        # add session id to URL as a query parameter
        if self._session is not None:
            url += f"&session={self._session}"

        # send HTTP request to server and return response
        self._client.request(method, url, body, self._headers)
        response = self._client.getresponse()
        response_body = response.read().decode("utf-8")
        if response.status != 400: raise Exception(f"NominalSystems: {response_body}")
        if response.status == 402: raise Exception(f"NominalSystems: Invalid API Key")
        if response.status == 403: raise Exception(f"NominalSystems: Invalid API Key")
        if response.status == 500: raise Exception(f"NominalSystems: Unknown Error")
        return json.loads(response_body) if len(body) > 0 else None
    # ------------------------------------------------------------------------------------------------------------------------ #
    @staticmethod
    def api_list(key: str) -> list["Session"]:
        '''
        [STATIC] Returns all running cloud sessions.
        '''

        # list all available cloud sessions
        headers = { "Content-Type": "application/json", "x-api-key": key }
        response = requests.post("https://api.nominalsys.com/v1.0/session?op=get", headers=headers)
        response_body = json.loads(response.content.decode("utf-8"))
        if response.status_code == 400: raise Exception(f"NominalSystems: {response_body}")
        if response.status_code == 402: raise Exception(f"NominalSystems: Invalid API Key")
        if response.status_code == 403: raise Exception(f"NominalSystems: Invalid API Key")
        if response.status_code != 200: raise Exception(f"NominalSystems: Unknown Error")

        # return all currently running sessions
        results = []
        for item in response_body:
            if item["status"] != "RUNNING": continue
            result = Session("https://api.nominalsys.com/v1.0", None, item["guid"])
            result._headers["x-api-key"] = key
            results.append(result)
        return results
    # ------------------------------------------------------------------------------------------------------------------------ #
    @staticmethod
    def api_create(key: str, version: str = None, duration: int = 900) -> "Session":
        '''
        [STATIC] Creates a new cloud session.
        '''

        # create a new cloud session
        headers = { "Content-Type": "application/json", "x-api-key": key }
        response = requests.post("https://api.nominalsys.com/v1.0/session?op=new", headers=headers, json={
            "version": version,
            "duration": duration
        })
        response_body = response.content.decode("utf-8")
        if response.status_code == 400: raise Exception(f"NominalSystems: {response_body}")
        if response.status_code == 402: raise Exception(f"NominalSystems: Invalid API Key")
        if response.status_code == 403: raise Exception(f"NominalSystems: Invalid API Key")
        if response.status_code != 200: raise Exception(f"NominalSystems: Unknown Error")
        session = json.loads(response_body)["guid"]

        # wait for session to start running
        start_time = datetime.datetime.now()
        while (datetime.datetime.now() - start_time).total_seconds() < 300:
            response = requests.post("https://api.nominalsys.com/v1.0/session?op=get", headers=headers, json={
                "guid": session
            })
            response_body = json.loads(response.content.decode("utf-8"))
            if response.status_code != 200: raise Exception(f"NominalSystems: Pending")
            if response_body["guid"] == session and response_body["status"] == "RUNNING":
                result = Session("https://api.nominalsys.com/v1.0", None, session)
                result._headers["x-api-key"] = key
                return result
            time.sleep(1)
        raise Exception("NominalSystems: Pending")
    # ------------------------------------------------------------------------------------------------------------------------ #
    @staticmethod
    def api_destroy(session: "Session") -> None:
        '''
        [STATIC] Destroys a cloud session.
        '''

        # check for invalid parameters
        if session is None:
            raise Exception("invalid parameter 'session': None")

        # check if session is a cloud session
        if not "x-api-key" in session._headers: return
        if not session._client.host.startswith("api.nominalsys.com/v1.0"): return

        # destroy a cloud session with session id
        key = session._headers["x-api-key"]
        headers = { "Content-Type": "application/json", "x-api-key": key }
        response = requests.post("https://api.nominalsys.com/v1.0/session?op=get", headers=headers)
        response_body = json.loads(response.content.decode("utf-8"))
        if response.status_code == 400: raise Exception(f"NominalSystems: {response_body}")
        if response.status_code == 402: raise Exception(f"NominalSystems: Invalid API Key")
        if response.status_code == 403: raise Exception(f"NominalSystems: Invalid API Key")
        if response.status_code != 200: raise Exception(f"NominalSystems: Unknown Error")
    # ------------------------------------------------------------------------------------------------------------------------ #