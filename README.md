# nominalpy

[![PyPI Version](https://img.shields.io/pypi/v/nominalpy.svg)](https://pypi.org/project/nominalpy/)

NominalPy is a Python library that enables easy access to the Nominal API. The API is a REST interface to the Nominal simulation library, enabling simulations of spacecraft, ground stations, maritime objects and more. The API requires an [access key](#accessing-your-api-token) that is available with a free account from the Nominal website.

Example simulation scripts and usage of the NominalPy library can be found in the public repository [NominalPy Examples](https://github.com/NominalSystems/nominalpy_examples). This contains some sample scripts showcasing how to use the library and how to run spacecraft simulations with flight software and requesting data from the simulation API. This requires an API key to execute but can be used as a basis for development.

Additional tutorials and functionality for the library can be found on the public documentation at [docs.nominalsys.com](https://docs.nominalsys.com) under the Guides page.

![Sun Pointing Simulation](https://docs.nominalsys.com/v0.8/articles/NominalSystems/guides/images/Untitled%203.png)

<br>

---

### Installing `nominalpy`

NominalPy includes the interface for the Nominal API architecture, allowing for custom simulations to be constructed using API endpoints. For a non-local simulation, this requires correct authentication. To install `nominalpy`, install the project from the PyPi repository:

`
pip install nominalpy -user
`

Alternatively, this package can be downloaded, unzipped and installed via the following command instead.

`
pip install . --user
`

NominalPy requires the following Third-Party Python libraries to be installed alongside the installation of this package: 
- numpy
- pandas
- requests
- urllib3
- paho-mqtt
- matplotlib
- setuptools

<br>

---

### Updating `nominalpy`

To upgrade a version of NominalPy, make sure to upgrade the python package. This can be done by the following command.

`
pip install nominalpy --user --upgrade
`

---

### Accessing your API Token

API Tokens are accessible via the [Nominal Website](https://www.nominalsys.com/account/sign-in). Create a free account and start a 14-day free trial of the software. This will give you access to unlimited sessions and requests during the trial period. The access token is available from the dashboard once the account is created and logged in.

To enable your token, create a Credential object and pass into the Simulation class when constructing simulations. Alternatively, if using the example library, update the token in the `credential_helper.py` class for easier access to the token over multiple files. More information can be found in the [Public Documentation](https://docs.nominalsys.com/).

---

### API Sessions

Each token enables a single API session to be made. Multiple sessions cannot be created at once using the free-tier of the API. Each session is associated with a single cloud instance running the simulation that you have access to. This instance will run for 2 hours once connected. When first connected to the session, it may take between 30 seconds and 2 minutes for the instance to start when you run a simulation for the first time. After that, the instance will be available without any load times for 2 hours. Upon the completion of the session, a new session can be started immediately after with a similar load-up time as before. There is no limit for the number of sessions available during a period of time, with the exception of having one session running concurrently.

---

</br>

![Atmospheric Drag Analysis](https://docs.nominalsys.com/v0.8/articles/NominalSystems/guides/Python/GettingStarted/images/Untitled.png)