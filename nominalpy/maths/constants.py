'''
                    [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems to aid with communication 
to the public API. All code is under the the license provided along
with the 'nominalpy' module. Copyright Nominal Systems, 2023.

This file contains public constants related to general mathematics,
as well as astrophysical constants. These include planetary data
and useful values that can be used for conversions.
'''

# [-] The value of PI
M_PI: float = 3.141592653589793

# [-] The value of PI/2
M_PI_2: float = 1.5707963267948966

# [-] The value of the exponential constant E
M_E: float = 2.718281828459045

# [-] Degrees to Radians constant
D2R: float = M_PI / 180.0

# [-] Radians to Degrees constant
R2D: float = 180.0 / M_PI

# [-] Conversion from rad/s to revolutions per minute
RPM: float = 0.10471975511965977

# [d] The number of days in a second
SEC2DAY: float = 1.0 / (60.0 * 60.0 * 24.0)



# [m^3/s^2/kg] Universial Gravitational Constant
G: float = 6.67259e-11

# [m] Astronomical unit
AU: float = 149597870693.0

# [m/s] The absolute speed of light in a vacuum in meters per second
LIGHT_SPEED: float = 299792458

# [K] The value of temperature in Kelvin at 0 degrees Celcius
CELCIUS_TO_KELVIN: float = 273.15



# [m] The equatorial radius of the Sun
SUN_REQ: float = 695000000

# [m] Polar radius of the Sun
SUN_RP: float = 6.95508e8

# [kg] The total mass of the Sun
SUN_MASS: float = 1.989E+30

# [-] The Sun J2 value (implicitely zero)
SUN_J2: float = 0.0

# [m^3/s^2] The Sun Gravitational constant
SUN_MU: float = 132712440023.310 * 1e9

# [kg/m^3] The density of Sun
SUN_DENSITY: float = 1410

# [-] A reflection albedo constant from the Sun's surface
SUN_ALBEDO_AVG: float = 0.0



# [m] Equatorial radius of Mercury
MERCURY_REQ: float = 2439700

# [m] Polar radius of Mercury
MERCURY_RP: float = 2.4397e6

# [kg] The total mass of Mercury
MERCURY_MASS: float = 0.330E+24

# [-] Mercury J2 value
MERCURY_J2: float = 60.0e-6

# [m] Mercury Semi-Major Axis of it's orbit
MERCURY_ORBIT_SMA: float = 0.38709893 * AU

# [rad] The axis inclination of Mercury's orbit
MERCURY_ORBIT_INC: float = 7.00487 * D2R

# [-] The eccentricity for Mercury's orbit
MERCURY_ORBIT_E: float = 0.20563069

# [r/s] Rotation rate of the planet
MERCURY_OMEGA: float = 2 * M_PI / 1407.6 / 3600.0

# [m^3/s^2] The gravitational constant for Mercury
MERCURY_MU: float = 22032.080 * 1e9

# [kg/m^3] The density of Mercury
MERCURY_DENSITY: float = 5427

# [-] A reflection albedo constant from Mercury's surface
MERCURY_ALBEDO_AVG: float = 0.119



# [m] Equatorial radius of Venus
VENUS_REQ: float = 6051800

# [m] Polar radius of Venus
VENUS_RP: float = 6.0518e6

# [kg] The total mass of Venus
VENUS_MASS: float = 4.87E+24

# [-] Venus J2 value
VENUS_J2: float = 4.458e-6

# [m] Venus Semi-Major Axis of its orbit
VENUS_ORBIT_SMA: float = 0.72333199 * AU

# [rad] The axis inclination of Venus's orbit
VENUS_ORBIT_INC: float = 3.39471 * D2R

# [-] The eccentricity for Venus's orbit
VENUS_ORBIT_E: float = 0.00677323

# [r/s] Rotation rate of the planet
VENUS_OMEGA: float = 2 * M_PI / -5832.6 / 3600.0

# [k=m^3/s^2] The gravitational constant for Venus
VENUS_MU: float = 324858.599 * 1e9

# [kg/m^3] The density of Venus
VENUS_DENSITY: float = 5243

# [-] A reflection albedo constant from Venus's surface
VENUS_ALBEDO_AVG: float = 0.75



# [m] Equatorial radius of Earth
EARTH_REQ: float = 6378136.6

# [m] Polar radius of Earth
EARTH_RP: float = 6356751.9

# [kg] The total mass of Earth
EARTH_MASS: float = 5.97E+24

# [-] Earth J2 value
EARTH_J2: float = 1082.616e-6

# [-] Earth J3 value
EARTH_J3: float = -2.53881e-6

# [-] Earth J4 value
EARTH_J4: float = -1.65597e-6

# [-] Earth J5 value
EARTH_J5: float = -0.15e-6

# [-] Earth J6 value
EARTH_J6: float = 0.57e-6

# [m] Earth Semi-Major Axis of its orbit
EARTH_ORBIT_SMA: float = 1.00000011 * AU

# [rad] The axis inclination of Earth's orbit
EARTH_ORBIT_INC: float = 0.00005 * D2R

# [-] The eccentricity for Earth's orbit
EARTH_ORBIT_E: float = 0.01671022

# [rad/s] Rotation rate of the planet
EARTH_OMEGA: float = 2 * M_PI / 23.9345 / 3600.0

# [m^3/s^2] The gravitational constant for Earth
EARTH_MU: float = 3.986004414e14

# [kg/m^3] The density of Earth
EARTH_DENSITY: float = 5514

# [-] A reflection albedo constant from Earth's surface
EARTH_ALBEDO_AVG: float = 0.29

# [W/m^2] Median solar flux at Earth
EARTH_SOLAR_FLUX: float = 1372.5398

# [m/s] The gravitational acceleration at the surface of the Earth
EARTH_GRAV: float = 9.80665


# [m] Equatorial radius of the Moon
MOON_REQ: float = 1737400

# [m] Polar radius of the Moon
MOON_RP: float = 1.7374e6

# [kg] The total mass of the Moon
MOON_MASS: float = 0.073E+24

# [-] J2 constant for the Moon
MOON_J2: float = 202.7e-6

# [m] Semi-Major Axis of the Moon's orbit
MOON_ORBIT_SMA: float = 0.3844e9

# [-] Eccentricity of the Moon's orbit
MOON_ORBIT_E: float = 0.0549

# [rad/s] The Moon's rotation rate
MOON_OMEGA: float = 2 * M_PI / 655.728 / 3600.0

# [m^3/s^2] The gravitational constant for the Moon
MOON_MU: float = 4.9048695e12

# [kg/m^3] The density of the Moon
MOON_DENSITY: float = 3340

# [-] A reflection albedo constant from the Moon's surface
MOON_ALBEDO_AVG: float = 0.123



# [m] Equatorial radius of Mars
MARS_REQ: float = 3396190

# [m] Polar radius of Mars
MARS_RP: float = 3376200

# [kg] The total mass of Mars
MARS_MASS: float = 0.642E+24

# [-] Mars J2 value
MARS_J2: float = 1960.45e-6

# [m] Mars Semi-Major Axis of its orbit
MARS_ORBIT_SMA: float = 1.52366231 * AU

# [rad] The axis inclination of Mars's orbit
MARS_ORBIT_INC: float = 1.85061 * D2R

# [-] The eccentricity for Mars's orbit
MARS_ORBIT_E: float = 0.09341233

# [r/s] Rotation rate of the planet
MARS_OMEGA: float = 2 * M_PI / 24.6229 / 3600.0

# [m^3/s^2] The gravitational constant for Mars
MARS_MU: float = 42828.314 * 1e9

# [kg/m^3] The density of Mars
MARS_DENSITY: float = 3933

# [-] A reflection albedo constant from Mars's surface
MARS_ALBEDO_AVG: float = 0.16


# [m] The radius of Phobos
PHOBOS_REQ: float = 11200


# [m] The radius of Deimos
DEIMOS_REQ: float = 6100



# [m] Equatorial radius of Jupiter
JUPITER_REQ: float = 71492000

# [m] Polar radius of Jupiter
JUPITER_RP: float = 7.1492e7

# [kg] The total mass of Jupiter
JUPITER_MASS: float = 1898E+24

# [-] Jupiter J2 value
JUPITER_J2: float = 14736.0e-6

# [m] Jupiter Semi-Major Axis of its orbit
JUPITER_ORBIT_SMA: float = 5.20336301 * AU

# [rad] The axis inclination of Jupiter's orbit
JUPITER_ORBIT_INC: float = 1.30530 * D2R

# [-] The eccentricity for Jupiter's orbit
JUPITER_ORBIT_E: float = 0.04839266

# [r/s] Rotation rate of the planet
JUPITER_OMEGA: float = 2 * M_PI / 9.9250 / 3600.0

# [m^3/s^2] The gravitational constant for Jupiter
JUPITER_MU: float = 126712767.881 * 1e9

# [kg/m^3] The density of Jupiter
JUPITER_DENSITY: float = 1326

# [-] A reflection albedo constant from Jupiter's surface
JUPITER_ALBEDO_AVG: float = 0.34



# [m] Equatorial radius of Saturn
SATURN_REQ: float = 60268000

# [m] Polar radius of Saturn
SATURN_RP: float = 6.0268e7

# [kg] The total mass of Saturn
SATURN_MASS: float = 568E+24

# [-] Saturn J2 value
SATURN_J2: float = 16298.0e-6

# [m] Saturn Semi-Major Axis of its orbit
SATURN_ORBIT_SMA: float = 9.53707032 * AU

# [rad] The axis inclination of Saturn's orbit
SATURN_ORBIT_INC: float = 2.48446 * D2R

# [-] The eccentricity for Saturn's orbit
SATURN_ORBIT_E: float = 0.05415060

# [r/s] Rotation rate of the planet
SATURN_OMEGA: float = 2 * M_PI / 10.656 / 3600.0

# [m^3/s^2] The gravitational constant for Saturn
SATURN_MU: float = 37940626.068 * 1e9

# [kg/m^3] The density of Saturn
SATURN_DENSITY: float = 687

# [-] A reflection albedo constant from Saturn's surface
SATURN_ALBEDO_AVG: float = 0.34



# [m] Equatorial radius of Uranus
URANUS_REQ: float = 25559000

# [m] Polar radius of Uranus
URANUS_RP: float = 2.5559e7

# [kg] The total mass of Uranus
URANUS_MASS: float = 86.8E+24

# [-] Uranus J2 value
URANUS_J2: float = 3343.43e-6

# [m] Uranus Semi-Major Axis of its orbit
URANUS_ORBIT_SMA: float = 19.19126393 * AU

# [rad] The axis inclination of Uranus's orbit
URANUS_ORBIT_INC: float = 0.76986 * D2R

# [-] The eccentricity for Uranus's orbit
URANUS_ORBIT_E: float = 0.04716771

# [r/s] Rotation rate of the planet
URANUS_OMEGA: float = 2 * M_PI / -17.24 / 3600.0

# [m^3/s^2] The gravitational constant for Uranus
URANUS_MU: float = 5794559.128 * 1e9

# [kg/m^3] The density of Uranus
URANUS_DENSITY: float = 1271

# [-] A reflection albedo constant from Uranus's surface
URANUS_ALBEDO_AVG: float = 0.29



# [m] Equatorial radius of Neptune
NEPTUNE_REQ: float = 24746000

# [m] Polar radius of Neptune
NEPTUNE_RP: float = 2.4746e7

# [kg] The total mass of Neptune
NEPTUNE_MASS: float = 102E+24

# [-] Neptune J2 value
NEPTUNE_J2: float = 3411.0e-6

# [m] Neptune Semi-Major Axis of its orbit
NEPTUNE_ORBIT_SMA: float = 30.06896348 * AU

# [rad] The axis inclination of Neptune's orbit
NEPTUNE_ORBIT_INC: float = 1.76917 * D2R

# [-] The eccentricity for Neptune's orbit
NEPTUNE_ORBIT_E: float = 0.00858587

# [r/s] Rotation rate of the planet
NEPTUNE_OMEGA: float = 2 * M_PI / 16.11 / 3600.0

# [m^3/s^2] The gravitational constant for Neptune
NEPTUNE_MU: float = 6836534.065 * 1e9

# [kg/m^3] The density of Neptune
NEPTUNE_DENSITY: float = 1638

# [-] A reflection albedo constant from Neptune's surface
NEPTUNE_ALBEDO_AVG: float = 0.31



# [m] Equatorial radius of Pluto
PLUTO_REQ: float = 1137000

# [m] Polar radius of Pluto
PLUTO_RP: float = 1.37e6

# [kg] The total mass of Pluto
PLUTO_MASS: float = 0.0146E+24

# [-] Pluto J2 value
PLUTO_J2: float = 0.0

# [m] Pluto Semi-Major Axis of its orbit
PLUTO_ORBIT_SMA: float = 39.48168677 * AU

# [rad] The axis inclination of Pluto's orbit
PLUTO_ORBIT_INC: float = 17.14175 * D2R

# [-] The eccentricity for Pluto's orbit
PLUTO_ORBIT_ECC: float = 0.24880766

# [r/s] Rotation rate of the planet
PLUTO_OMEGA: float = 2 * M_PI / -153.2928 / 3600.0

# [m^3/s^2] The gravitational constant for Pluto
PLUTO_MU: float = 983.055 * 1e9

# [kg/m^3] The density of Pluto
PLUTO_DENSITY: float = 2095

# [-] A reflection albedo constant from Pluto's surface
PLUTO_ALBEDO_AVG: float = 0.0