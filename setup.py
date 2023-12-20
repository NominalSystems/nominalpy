#                     [ NOMINAL SYSTEMS ]
# This code is developed by Nominal Systems to aid with communication 
# to the public API. All code is under the the license provided along
# with the 'nominalpy' module. Copyright Nominal Systems, 2023.

from setuptools import setup, find_packages

# Setup the project
setup(
    name='nominalpy',
    version='0.7.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=["requests", "urllib3", "paho-mqtt", "numpy", "pandas"],
    author='Nominal Systems',
    author_email='support@nominalsys.com',
    description='Python Interface to the Nominal API for simulations',
    long_description="This is the Python interface library for the Nominal API. \
        It enables accessing the REST API simulation functions in an easy format.\
        Examples of how to construct Nominal simulations are provided on the\
        Nominal Systems documentation found at https://www.docs.nominalsys.com.",
    url='https://api.nominalsys.com',
)