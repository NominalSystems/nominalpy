from setuptools import setup, find_packages

# Setup the project
setup(
    name='nominalpy',
    version='0.2.0',
    packages=find_packages(),
    install_requires=["requests", "urllib3"],
    author='Nominal Systems',
    author_email='support@nominalsys.com',
    description='Python Interface to the Nominal API for simulations',
    url='https://api.nominalsys.com',
)