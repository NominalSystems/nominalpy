# Define the version
__version__ = "1.2.0"

# Import the standard utilities
from .utils import NominalException, printer, helper

# Import the standard classes that are commonly used
from .connection import Credentials, Client
from .simulation import *
