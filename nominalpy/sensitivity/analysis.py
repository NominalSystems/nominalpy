'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

The Sensitivity Analysis class is able to create multiple simulations
with varying parameters and allow the data to be extracted from at the
end of the simulation. Each simulation will be identical with the
exception of some user defined parameters within the configuration.
'''

from .. import Component, Credentials, Message, NominalException, printer
from .case import SensitivityCase
from .configuration import SensitivityConfiguration

class SensitivityAnalysis:

    '''
    Specifies the credentials for accessing the API correctly.
    '''
    __credentials: Credentials = None

    '''
    This defines the simulation configuration that is being used for the
    sensitivity analysis.
    '''
    config: SensitivityConfiguration = None

    '''
    A list of JSON simulation cases that defines all the case studies that
    will be executed on the run.
    '''
    cases: list = []

    '''
    A list of all messages to register and keep track of in the database
    system based on the object they exist on.
    '''
    subscriptions: list = []

    '''
    A list of all message IDs that have been subscribed to correctly.
    '''
    message_ids: list = []

    '''
    A self-populating list of simulation IDs based on the simulations that
    are run in the analysis.
    '''
    ids: list = []

    def __init__(self, credentials: Credentials, config: SensitivityConfiguration) -> None:
        '''
        Initialises the sensitivity analysis with a particular simulation
        configuration. This must be passed in as a parameter.
        '''

        # Throw error if no config and update
        if config == None:
            raise Exception("No config passed into Sensitivity Analysis object.")
        self.config = config
        self.__credentials = credentials

    def add_case (self, case: SensitivityCase) -> None:
        '''
        Attempts to add a new sensitivity case to the sensitivity analysis
        system.
        '''
        if case == None:
            raise Exception("Invalid sensitivity case added.")
        self.cases.append(case)
    
    def new_case (self) -> SensitivityCase:
        '''
        Creates a new sensitivity case and added into the sensitivity analysis
        list to be edited. 
        '''
        self.cases.append(SensitivityCase())
        return self.cases[-1]
    
    def subscribe (self, object: str, message: str, interval: float = 10.0):
        '''
        Registers a new message to be subscribed to in the database system based
        on the object name and the message name, if it exists.
        '''

        # Add a subscription to the configuration
        self.subscriptions.append({
            "object": object,
            "message": message,
            "interval": interval
        })
    
    def run (self, time: float, step: float = 0.1) -> None:
        '''
        This will run the simulation based on the configuration and the 
        parameters. This will have a fixed step size and will run each
        simulation for the desired time in seconds.
        '''

        # Determine the iterations
        iterations: int = int(float(time) / float(step))

        # If no cases, add a single empty case
        if len(self.cases) == 0:
            printer.warning("No sensitivity cases were added to the analysis. Creating a default case now.")
            self.new_case()
        
        # Loop through each of the cases
        for idx, case in enumerate(self.cases):
            
            # Reset the simulation
            self.config.reset()
            
            # Configure the simulation and get the ID
            self.config.add_credentials(self.__credentials)
            self.config.configure()
            self.ids.append(self.config.get_id())

            # Loop through all of the case parameters
            for change in case.data:
                self.config.set_value(change["object"], change["param"], change["value"])
            
            # Subscribe to messages and add to the IDs
            self.message_ids.append([])
            for msg in self.subscriptions:
                id: str = self.config.subscribe(msg["object"], msg["message"], msg["interval"])
                self.message_ids[idx].append(id)
            
            # Run the simulation for the desired time
            self.config.tick(step, iterations)
        
        # Print a success
        printer.success("Successfully completed %d sensitivity cases." % len(self.cases))
    
    def get_values (self, object: str, message: str, parameter: str, min_time: float = 0.0, max_time: float = 0.0) -> list:
        '''
        Returns all of the values from particular messages stored in
        the database based on the name of the message. If the message
        does not exist, then this will return an empty list. This also
        fetches data within the minimum and maximum time (if applicable).
        This requires a valid parameter name to search for.
        '''

        # Find the index of the message name
        index: int = -1
        for idx, msg in enumerate(self.subscriptions):
            if msg["object"] == object and msg["message"] == message:
                index = idx
                break
        
        # Fail if no correct message
        if index < 0:
            printer.error("No message of name '%s' on object '%s' was subscribed." % (message, object))
            return []
        
        # Create the data list
        values: list = []
        
        # Loop through all simulations
        for i in range(len(self.ids)):

            # Get the IDs
            sim_id: str = self.ids[i]
            msg_id: str = self.message_ids[i][index]

            # Get the data
            data: list = Message.message_fetch_range(self.__credentials, sim_id, msg_id, min_time, max_time, parameter)
            if data == {}:
                printer.warning("No data found when fetching data for message '%s' on object '%s'." % (message, object))
            values.append(data)
        
        # Return the final list of values
        return values