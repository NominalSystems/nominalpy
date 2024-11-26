#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

'''
This module includes some common class types that are used throughout
the simulation, making it easier to instantiate these objects.
'''


SOLAR_SYSTEM        = "NominalSystems.Universe.SolarSystem"
'''This defines the Universe System that is used to initialise all Universe conditions.'''

GROUND_STATION      = "NominalSystems.Universe.GroundStation"
'''This is a ground station that can be placed on a location on the planet.'''

PHYSICAL_OBJECT     = "NominalSystems.Universe.PhysicalObject"
'''This is a physical component that can be attached to other objects in a spacecraft or entity.'''

SPACECRAFT          = "NominalSystems.Universe.Spacecraft"
'''This is a spacecraft class that can be initialised at some location in space.'''

TELEMETRY_SYSTEM    = "NominalSystems.Classes.TelemetrySystem"
'''This is the telemetry system that tracks the links between antennae.'''