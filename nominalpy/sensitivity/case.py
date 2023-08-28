'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

The Sensitivity Case class enables the user to define a particular
case with a series of parameters that will be adjusted in this
ID. These will be the parameters compared to the initial case in
the simulation configuration.
'''

class SensitivityCase:

    def __init__ (self) -> None:
        '''
        Initialises a new case with an empty set of data. No parameters
        are required to be initialised. This defines the use case data in 
        the correct format as per the expected case study.
        '''
        self.data: list = []

    def add (self, object: str, param: str, value: str):
        '''
        Adds a new entry into the data, including the object to modify,
        the parameter to change and the new value in a valid JSOn format.
        '''

        # Define a new row and add to the list
        row: dict = {
            "object": object,
            "param": param,
            "value": value
        }
        self.data.append(row)

        # Return the object
        return self