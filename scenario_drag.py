#!/usr/bin/env python3

'''
==================================================
                Nominal API
                
    This script acts to replicate the integrated
    test for a drag demo, having two spacecraft on
    an orbit and being able to show how they differ
    if one has drag.
==================================================
'''

# Import the relevant helper scripts
from nominalpy import Simulation
from nominalpy import Object
from nominalpy import Component
from nominalpy import Message
from nominalpy import Value
from nominalpy import printer
import os
from matplotlib import pyplot as plt
import numpy as np
from credential_helper import *

# Clear the terminal
os.system('cls' if os.name == 'nt' else 'clear')

# Construct the credentials
credentials = fetch_credentials()

# Set the verbosity
printer.set_verbosity(printer.LOG_VERBOSITY)

# Create a simulation handle
simulation: Simulation = Simulation(credentials)

# Configure the Universe with an epoch
universe: Object = simulation.get_system("NominalSystems.Universe.UniverseSystem")
universe.set_value("Epoch", Value.datetime(2022, 1, 1))

# Adds the spacecraft
sc_a: Component = simulation.add_component("Universe.Spacecraft")
sc_a.set_value("TotalMass", 10.0)
sc_a.set_value("Position", Value.vector3(0.0000, -6578140.0000, 0.0000))
sc_a.set_value("Velocity", Value.vector3(7784.2605, 0.0000, 0.0000))
sc_b: Component = simulation.add_component("Universe.Spacecraft")
sc_b.set_value("TotalMass", 10.0)
sc_b.set_value("Position", Value.vector3(0.0000, -6578140.0000, 0.0000))
sc_b.set_value("Velocity", Value.vector3(7784.2605, 0.0000, 0.0000))

# Give a drag to the second craft
drag: Component = simulation.add_component("DragEffector", owner=sc_b, ProjectedArea=500, DragCoefficient=2.2)

# Get the state messages for each craft
state_a: Message = sc_a.get_message("Out_BodyStatesMsg")
state_a.subscribe()
state_b: Message = sc_b.get_message("Out_BodyStatesMsg")
state_b.subscribe()

# Execute the simulation to be ticked
simulation.tick(5.0, 200)

# Get the data for the plot [SIGMA_BR]
sc_a_pos = state_a.fetch("R_BN_N")
sc_b_pos = state_b.fetch("R_BN_N")
time = Value.fetch_array(sc_a_pos, "time")
a_x = Value.fetch_array(sc_a_pos, "R_BN_N", "X")
a_y = Value.fetch_array(sc_a_pos, "R_BN_N", "Y")
b_x = Value.fetch_array(sc_b_pos, "R_BN_N", "X")
b_y = Value.fetch_array(sc_b_pos, "R_BN_N", "Y")

# Plot the data
figure, axes = plt.subplots()
earth = plt.Circle(( 0.0 , 0.0 ), 6371000.0, color = 'cyan', label = 'Earth')
axes.set_aspect(1.0)
axes.set_xlim(0, 7000000)
axes.set_ylim(-7000000, 0)
axes.add_artist( earth )
axes.scatter(a_x, a_y, 2.0, marker = 'o', label = "Small Craft Position [m]", color = 'red')
axes.scatter(b_x, b_y, 2.0, marker = 'x', label = "Dragged Craft Position [m]", color = 'green')
plt.legend()
plt.title("Position [m]")
plt.show()