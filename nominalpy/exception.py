'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

The Exception class defines a custom exception that is able to track 
errors with the Nominal API. Any connection errors or issues with the 
objects will throw an Nominal API if there are configuration issues.
'''

class NominalException (Exception):

    def __init__(self, message: str):
        '''
        Defines the constructor for the exception and is able
        to pass in some parameters in regards to the exception.
        '''
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        '''
        This is the automated cast to a string from the message,
        which is able to return the exception information.
        '''
        return "[NOMINAL ERROR] %s" % self.message
