#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

from importlib.metadata import version

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

    version: str = ""
    '''Defines the version of the API that is being used.'''

    __raw_url: str = ""
    '''This defines the raw URL that is used for the API connection.'''

    __session_id: str = None
    '''This defines the session ID for the current working session, stored for public API keys.'''

    def __init__ (self, url: str = "https://api.nominalsys.com", port: int = 443, access: str = "") -> None:
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

        # Fetch the version from the package information and only select the first two digits
        package_version: str = version('nominalpy')
        package_version = package_version[:package_version.rfind(".")]
        self.version = "v" + package_version

        # Configure the URL
        self.url = url
        self.__raw_url = url
        if url == "" or url == None:
            self.url = "https://localhost"
        if "localhost" in self.url:
            self.is_local = True
        
        # Check if missing https
        if not self.is_local:
            if "http" not in self.url:
                self.url = f"https://{self.url}"
        
        # Configure the port
        self.port = port
        if port == 0 or port is None:
            port = 8080 if self.is_local else 443
        if self.is_local:
            self.url += ":%d" % port
        
        # Check if missing a slash at the end
        if not self.url.endswith("/"):
            self.url += "/"
        
        # Add in the version end-point
        if not self.is_local:
            self.url += f"{self.version}/"

        # Set the access key
        self.access_key = access

    def set_session_id (self, session_id: str) -> None:
        '''
        Sets the session ID for the current session. This is used to track the
        current session and to ensure that the session is valid.

        :param session_id:  The session ID for the current session
        :type session_id:   str
        '''
        self.__session_id = session_id
    
    def get_session_id (self) -> str:
        '''
        Returns the session ID for the current session. This is used to track
        
        :returns:   The session ID for the current session
        :rtype:     str
        '''
        return self.__session_id
        
    def is_valid (self) -> bool:
        '''
        Checks if the credentials are valid by checking if the URL is valid
        and the access key is valid.

        :returns:   Whether the credentials are valid
        :rtype:     bool
        '''
        return self.url != "" and (self.access_key != "" or self.is_local)
    
    def copy (self) -> "Credentials":
        '''
        Copies the current credentials to a new instance of the credentials.

        :returns:   A new instance of the credentials
        :rtype:     Credentials
        '''
        return Credentials(self.__raw_url, self.port, self.access_key)