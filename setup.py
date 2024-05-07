#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2024.

from setuptools import setup, find_packages

# Setup the project
setup(
    name='nominalpy',
    version='0.8.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=["requests", "urllib3", "paho-mqtt", "numpy", "pandas", "matplotlib"],
    author='Nominal Systems',
    author_email='support@nominalsys.com',
    description='Python Interface to the Nominal API for simulations',
    long_description="This is the Python interface library for the Nominal API. \
        The Nominal API allows access to spacecraft and space-domain simulation functions \
        and the framework for simulating high-fidelity satellites. \
        It enables accessing the REST API simulation functions in an easy format.\
        Examples of how to construct Nominal simulations are provided on the\
        Nominal Systems documentation found at https://docs.nominalsys.com.",
    url='https://github.com/NominalSystems/nominalpy',
)