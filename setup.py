from setuptools import setup, find_packages

# Setup the project
setup(
    name='nominalpy',
    version='0.7.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=["requests", "urllib3", "paho-mqtt", "numpy", "pandas"],
    author='Nominal Systems',
    author_email='support@nominalsys.com',
    description='Python Interface to the Nominal API for simulations',
    long_description="Python Interface to the Nominal API for simulations",
    url='https://api.nominalsys.com',
)