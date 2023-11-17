#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2023.

'''
This module includes some common class types that are used throughout
the simulation, making it easier to instantiate these objects.
'''


UNIVERSE        = "NominalSystems.Universe.UniverseSystem"
'''This defines the Universe System that is used to initialise all Universe conditions.'''

GROUND_STATION  = "NominalSystems.Universe.GroundStation"
'''This is a ground station that can be placed on a location on the planet.'''

SPACECRAFT      = "NominalSystems.Universe.Spacecraft"
'''This is a spacecraft class that can be initialised at some location in space.'''