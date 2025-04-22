#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

from ..connection import Client
from .instance import Instance


class Message(Instance):
    """
    The Message class is able to store a series of parameters and data
    associated with the particular message type. This class is a pure
    data class and is not able to invoke any methods.
    """

    def __init__(self, client: Client, id: str, type: str = None) -> None:
        """
        Initialises the message with a client and a
        unique GUID identifier for the message.

        :param client:      The client object that is used for the API
        :type client:       Client
        :param id:          The unique identifier for the Entity in a GUID format
        :type id:           str
        :param type:        The type of the system, if applicable
        :type type:         str
        """

        super().__init__(client, id, type)
