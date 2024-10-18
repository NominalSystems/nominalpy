# ---------------------------------------------------------------------------------------------------------------------------- #
# Copyright 2024 (c) Nominal Systems, Pty Ltd. All Rights Reserved
# See the 'LICENSE' file at the root of this git repository
# ---------------------------------------------------------------------------------------------------------------------------- #
import re, json, time, datetime, requests
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

        # check if session is running
        if not self.is_running:
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
        response = requests.request(method, f"{self.host}:{self.port}{url}",
            data    = json.dumps(body),
            headers = self.headers
        )
        response_body = response.content.decode("utf-8")
        if response.status_code == 400:
            raise Exception(f"NominalSystems: {response_body}")
        if response.status_code == 402:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status_code == 403:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status_code == 500:
            raise Exception(f"NominalSystems: Unknown error")
        return json.loads(response_body) if len(response_body) > 0 else None
    # ------------------------------------------------------------------------------------------------------------------------ #
    @property
    def is_running(self):
        '''
        Is 'True' if the session is running.
        '''

        # check if session has ended
        if self.host is None:
            return False

        # check if session is a local session
        if not "x-api-key" in self.headers:
            return True

        # query if cloud session is still running
        response = requests.post(f"{self.host}:{self.port}/v1.0/session?op=get",
            data    = json.dumps({ "guid": self.guid }),
            headers = self.headers
        )
        response_body = response.content.decode("utf-8")
        if response.status_code == 400:
            raise Exception(f"NominalSystems: {response_body}")
        if response.status_code == 402:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status_code == 403:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status_code == 500:
            raise Exception(f"NominalSystems: Unknown error")
        return json.loads(response_body)["status"] == "RUNNING"
    # ------------------------------------------------------------------------------------------------------------------------ #
    @staticmethod
    def list_sessions(key: str) -> list["Session"]:
        '''
        [STATIC] Returns all running cloud sessions.
        '''

        # list all available cloud sessions
        headers = { "Content-Type": "application/json", "x-api-key": key }
        response = requests.post("https://api.nominalsys.com/v1.0/session?op=get", headers=headers)
        response_body = json.loads(response.content.decode("utf-8"))
        if response.status_code == 400:
            raise Exception(f"NominalSystems: {response_body}")
        if response.status_code == 402:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status_code == 403:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status_code == 500:
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
    def create_session(key: str, version: str = None, duration: int = None) -> "Session":
        '''
        [STATIC] Creates a new cloud session.
        '''

        # create a new cloud session
        session = Session("https://api.nominalsys.com")
        session.headers["x-api-key"] = key
        session.guid = json.loads(session.post("/v1.0/session", json.dumps({
            "version": "1.0" if version is None else version,
            "duration": 900 if duration is None else duration
        })))["guid"]

        # wait for session to start running
        start_time = datetime.datetime.now()
        while (datetime.datetime.now() - start_time).total_seconds() < 300:
            if (session.is_running):
                return session
            time.sleep(1)
        raise Exception("NominalSystems: Pending")
    # ------------------------------------------------------------------------------------------------------------------------ #
    @staticmethod
    def destroy_session(session: "Session") -> None:
        '''
        [STATIC] Destroys a cloud session.
        '''

        # check for invalid parameters
        if session is None:
            raise Exception("NominalSystems: Invalid parameter session 'None'")

        # check if session is still running
        if not session.is_running:
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
        response = requests.post(f"{session.host}:{session.port}/v1.0/session?op=del",
            data    = json.dumps({ "guid": session.guid }),
            headers = session.headers
        )
        response_body = json.loads(response.content.decode("utf-8"))
        if response.status_code == 400:
            raise Exception(f"NominalSystems: {response_body}")
        if response.status_code == 402:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status_code == 403:
            raise Exception(f"NominalSystems: Invalid api key")
        if response.status_code == 500:
            raise Exception(f"NominalSystems: Unknown error")
        session.host = None
        session.port = None
        session.guid = None
        session.headers = {}
    # ------------------------------------------------------------------------------------------------------------------------ #