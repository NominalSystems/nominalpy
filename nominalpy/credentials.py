'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

The Credentials class stores the credential access to the Nominal API 
for making API calls to the server. This can allow for both a remote 
or a local server call.
'''
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