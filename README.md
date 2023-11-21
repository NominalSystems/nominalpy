# nominalpy

[![PyPI Version](https://img.shields.io/pypi/v/your-package-name.svg)](https://pypi.org/project/nominalpy/)

NominalPy is a Python library that enables easy access to the Nominal API. The API is a REST interface to the Nominal simulation library, enabling simulations of spacecraft, ground stations, maritime objects and more. The API requires an access key that can be purchased by contacting Nominal Systems at `support@nominalsys.com`.

Example simulation scripts and usage of the NominalPy library can be found in the public repository [NominalPy Examples](https://github.com/NominalSystems/nominalpy_examples). This contains some sample scripts showcasing how to use the library and how to run spacecraft simulations with flight software and requesting data from the simulation API. This requires an API key to execute but can be used as a basis for development.

Additional tutorials and functionality for the library can be found on the public documentation at [docs.nominalsys.com](https://docs.nominalsys.com) under the Tutorials page.

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

<br>

---

### Updating `nominalpy`

To upgrade a version of NominalPy, make sure to upgrade the python package. This can be done by the following command.

`
pip install nominalpy --user --upgrade
`

---