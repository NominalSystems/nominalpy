#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

import requests, time, json
from ..utils import printer, NominalException
import pkg_resources


class Credentials:
    '''
    The Credentials class stores the credential access to the Nominal API 
    for making API calls to the server. This can allow for both a remote 
    or a local server call.
    '''

    url: str = ""
    '''Defines the base URL for the API. If empty, it assumes that the URL is localhost.'''

    port: int = None
    '''Defines the port for the API. If left as None, no port will be used.'''

    access_key: str = ""
    '''Defines the access key if it exists for the API. This is required for cloud based API calls.'''

    is_local: bool = False
    '''Defines whether the URL is a localhost one or not; used to ensure that a connection is valid.'''

    session_id: str = None
    '''This defines the session ID for the current working session, stored for public API keys.'''

    def __init__ (self, url: str = "https://api.nominalsys.com", port: int = None, access: str = "") -> None:
        '''
        Initialises some credentials to access the API and will be called
        by the simulation when making requests. If using a public API
        connection, this will create a new session or attempt to find if a
        session already exists. For new sessions, this may take a couple of
        minutes to initialise.

        :param url:     The URL or HTTP link to the API endpoint
        :type url:      str
        :param port:    The port number of the API endpoint
        :type port:     int
        :param access:  The access key or token for a public API request
        :type access:   str
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
            self.__connect()
    
    def __connect (self) -> None:
        '''
        Connects to a session or retrieves the current session and updates the
        session ID to the new IP address of the session if it exists. This will 
        also check to see if the health is valid
        '''

        # If this is a local-host, skip
        if self.is_local:
            return
        
        # A flag for whether this is the first attempt
        first_attempt: bool = True
        
        # Attempt to create the session
        # If there is no valid session, it will throw an execption at this point.
        self.__create_session()
        
        # Loop until the health is valid
        while True:

            # Fetch the health
            if self.__is_healthy():
                return
            
            # Print some information
            if first_attempt:
                printer.warning("New sessions may take up to 3 minutes to start up. Each session will last 2 hours once created. Please wait while your session is being configured...")
                first_attempt = False
            
            # Wait some time before attempting again
            time.sleep(3.0)

    def __create_session (self) -> None:
        '''
        Attempts to create or fetch a new session from the AWS batch system. This
        will call the API for a new session or load one that already exists.
        '''

        # Fetch the data
        printer.log("Attempting to find or create a new user session. This may take a few seconds.")
        response = requests.get(
            self.url + "session", 
            verify=False, 
            params={},
            headers = {'x-api-key': self.access_key, 'Content-Type': 'application/json'}
        )

        # Update the data and get the data
        if response.status_code == 200:
            data: dict = json.loads(response.text)
            self.session_id = data['id']
            printer.log("A session has been found. Continuing session...")

            # Fetch the version
            api_version: str = data['version']
            pkg_version: str = pkg_resources.get_distribution('nominalpy').version

            # If the versions do not match, print a warning
            if api_version != pkg_version:
                printer.warning("API Version Mismatch. You are on an older version of the API. " +
                    f"\nPlease upgrade to version {api_version} via 'pip install nominalpy --upgrade'. Some features may not work as intended.")
        
        # If there is a code, check the status
        else:

            # In the case of 402, then the account needs to purchase more credits
            # In this case, stop the loop.
            if response.status_code == 402:
                data: dict = json.loads(response.text)
                raise NominalException(data["error"])
            
            # Otherwise, check if there is an error message
            else:

                # Attempt to raise an exception with the custom error
                try:
                    data: dict = json.loads(response.text)
                    error: str = data["error"]

                # Otherwise, just raise the error manually
                except:
                    raise NominalException(f"ERROR {response.status_code}: {response.text}")
                
                # Raise the error with the data
                raise NominalException(error)
                
    def __is_healthy (self) -> bool:
        '''
        Returns whether the current session with the instance that is available
        is healthy as of right now. This will return a true or false flag.

        :returns:   A healthy success flag
        :rtype:     bool
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
    
    def is_valid (self) -> bool:
        '''
        Returns whether the credentials are valid. This does not check if the
        credentials are valid to a connection, more that the information has
        been added correctly.

        :returns:   A valid credential flag
        :rtype:     bool
        '''

        if self.url == None: return False
        if self.url == "": return False
        if len(self.url) < 8: return False
        if "http" not in self.url: return False
        return True