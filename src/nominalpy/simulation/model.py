#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

from ..utils import printer, NominalException, helper
from .instance import Instance
from .message import Message
from .context import Context


class Model(Instance):
    """
    The model class cannot exist in the simulation by itself, but can be used to
    attach to a simulation object. Each object can have up to 1 model of a specific
    type attach and allows for extended functionality to be added to the object.
    """

    __target: Instance = None
    """Defines the target object that the model is attached to."""

    __messages: dict[str:Message] = {}
    """Defines all messages that are attached to the object, by name."""

    def __init__(
        self, context: Context, id: str, type: str = None, target: Instance = None
    ) -> None:
        """
        Initialises the model with the context and the ID of the model.

        :param context:         The context of the simulation
        :type context:          Context
        :param id:              The GUID ID of the model
        :type id:               str
        :param type:            The type of the model to create, if applicable
        :type type:             str
        :param target:          The target object that the model is attached to
        :type target:           Instance
        """

        super().__init__(context, id, type)

        # If there is no target, raise an exception
        if not target:
            raise NominalException(
                "Failed to create model with a missing target object."
            )

        # Clear and reset the data
        self.__target = target
        self.__messages = {}

    def get_target(self) -> Instance:
        """
        Returns the target object that the model is attached to.

        :returns:   The target object that the model is attached to
        :rtype:     Object
        """

        return self.__target

    def _require_refresh(self) -> None:
        """
        Overrides the base class method to set the flag for refreshing the cache to true.
        This will ensure that all messages will also require a refresh.
        """

        # Ensure all messages require a refresh too
        for message in self.__messages.values():
            message._require_refresh()
        super()._require_refresh()

    def find_instance_with_id(self, id: str, recurse: bool = False) -> "Instance":
        """
        Returns the instance that is attached to this behaviour with the specified ID. If the
        instance does not exist, None will be returned. This may be a message or a child instance
        of some kind.

        :param id:  The ID of the instance to fetch
        :type id:   str
        :param recurse:  Whether to look down the chain of children to find the instance
        :type recurse:   bool

        :returns:   The instance that is attached to the object with the specified ID
        :rtype:     Instance
        """

        # Start by looking at the instances for the ID
        for msg in self.__messages.values():
            if msg.id == id:
                return msg

        # Return none otherwise
        return None

    async def get_message(self, name: str) -> Message:
        """
        Attempts to get the message with the specified name that is attached to the model. If the
        message does not exist, it will be created and attached to the model. If the message cannot
        be created, an exception will be raised.

        :param name:    The name of the message to fetch
        :type name:     str

        :returns:       The message with the specified name that is attached to the model
        :rtype:         Message
        """

        # Check if the name is within the message structure and return that
        if name in self.__messages.keys():
            return self.__messages[name]

        # Fetch the data
        message_id: str = await self.get(name)
        if not helper.is_valid_guid(message_id):
            raise NominalException(f"Failed to find message with name '{name}'.")

        # Create the message object with the ID
        message = Message(self._context, message_id)
        self.__messages[name] = message

        # Return the message of that name
        printer.success(f"Successfully created message with name '{name}'.")
        return message

    def get_messages(self) -> list[Message]:
        """
        Returns all of the messages that are attached to the model. This will only include the
        messages that have currently been fetched.

        :returns:   All of the messages that are attached to the model
        :rtype:     list[Message]
        """

        return list(self.__messages.values())
