from ..credentials import Credentials


class Entity:

    '''
    Defines the unique GUID identifier of the object. This needs to be
    in the corred GUID format and is used to call simulation requests.
    '''
    id: str = None

    '''
    Specifies the credentials for accessing the API correctly.
    '''
    _credentials: Credentials = None

    def __init__(self, credentials: Credentials, id: str):
        self.id = id
        self._credentials = credentials
