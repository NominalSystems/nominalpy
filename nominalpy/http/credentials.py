'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

The Credentials class stores the credential access to the Nominal API 
for making API calls to the server. This can allow for both a remote 
or a local server call.
'''

import requests, time
from ..printer import *

class Credentials:

    '''
    Defines the base URL for the API. If empty, it assumes
    that the URL is localhost.
    '''
    url: str = ""

    '''
    Defines the port for the API. If left as None, no port
    will be used.
    '''
    port: int = None

    '''
    Defines the access key if it exists for the API. This is
    required for cloud based API calls.
    '''
    access_key: str = ""

    '''
    Defines whether the URL is a localhost one or not, which
    can be used to ensure that a connection is valid.
    '''
    is_local: bool = False

    '''
    This defines the session ID for the current working session.
    This will need to be stored for public API keys.
    '''
    session_id: str = None


    def __init__ (self, url: str = "https://api.nominalsys.com", port: int = None, access: str = "") -> None:
        '''
        Initialises some credentials to access the API and will be called
        by the simulation when making requests.     
        '''
        self.url = url
        if url == "" or url == None:
            self.url = "https://localhost"
        
        self.port = port
        if port != 0 and port != None:
            self.url += ":%d" % port

        if not self.url.endswith("/"):
            self.url += "/"

        self.access_key = access

        if "localhost" in self.url:
            self.is_local = True

        # Attempt to authenticate with the session
        if "nominalsys" in self.url:
            self.connect()
    

    def connect (self) -> None:
        '''
        Connects to a session or retrieves the current session and updates the
        session ID to the new IP address of the session if it exists. This
        will also check to see if the health is valid
        '''

        # If this is a local-host, skip
        if self.is_local:
            return
        
        # A flag for whether this is the first attempt
        first_attempt: bool = True
        SESSION_TIMEOUT: float = 30
        counter: float = SESSION_TIMEOUT
        
        # Loop until the health is valid
        while True:

            # If the time is greater than the wait, create a session
            if counter >= SESSION_TIMEOUT:
                self.__create_session()
                counter = 0.0

            # Fetch the health
            if self.__is_healthy():
                return
            
            # Print some information
            if first_attempt:
                warning("New sessions may take up to 3 minutes to start up. Please wait while your session is being configured.")
                first_attempt = False
            else:
                log("Unable to find session. Attempting again in 10 seconds.")
            
            # Wait some time
            delta: float = 10.0
            time.sleep(delta)
            counter += delta


    def __create_session (self) -> None:
        '''
        Attempts to create or fetch a new session from the AWS batch system. This
        will call the API for a new session or load one that already exists.
        '''

        # Fetch the data
        log("Attempting to find or create a new user session. This may take a few seconds.")
        response = requests.get(
            self.url + "session", 
            verify=False, 
            params={}, 
            headers = {'x-api-key': self.access_key, 'Content-Type': 'application/json'}
        )

        # Update the data and get the data
        if response.status_code == 200:
            self.session_id = response.text
            log("A session has been created successfully.")
        else:
            error("Failed to create an API user session or retrieve previous session.")


    def __is_healthy (self) -> bool:
        '''
        Returns whether the current session with the instance that is available
        is healthy as of right now. This will return a true or false flag.
        '''

        try:
            response = requests.get(
                self.url + "session/health", 
                verify=False, 
                params={'session_id': self.session_id}, 
                headers = {'x-api-key': self.access_key, 'Content-Type': 'application/json'},
                timeout=3
            )

            # If the session is valid, continue
            if response and response.status_code == 200 and response.text == "true":
                return True
            return False

        # Catch any exception
        except:
            return False