'''
        [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems
to aid with communication to the public API.
'''

import datetime

'''
Defines a value that can be casted to a particular data type based on
the data that is stored. This is a helper function that can be useful
for converting raw data between Vector3 and Matrix3x3 data types.
'''
class Value:

    @classmethod
    def vector3 (self, x: float, y: float, z: float) -> dict:
        '''
        Defines a way for specifying a particular value based
        on a Vector3 structure.
        '''
        value: dict = {'X': x, 'Y': y, 'Z': z}
        return value
    
    @classmethod
    def matrix33 (self, m1: tuple, m2: tuple, m3: tuple) -> list:
        '''
        Defines a way for specifying a particular value based
        on a Matrix3x3 structure.
        '''
        value: list = [[m1[0], m1[1], m1[2]], [m2[0], m2[1], m2[2]], [m3[0], m3[1], m3[2]]]
        return value
    
    @classmethod
    def datetime (self, year: int, month: int, day: int, hour: int = 0, min: int = 0, sec: int = 0) -> dict:
        '''
        Defines a way of specifying a particular value based on
        a DateTime structure.
        '''
        dt: datetime.datetime = datetime.datetime(year, month, day, hour, min, sec)
        value: dict = {'Year': dt.year, 'Month': dt.month, 'Day': dt.day, 'Hour': dt.hour, 'Minute': dt.minute, 'Second': dt.second}
        return value
    
    @classmethod
    def timespan (self, days: int = 0, hours: int = 0, mins: int = 0, secs: int = 0, milliseconds: int = 0) -> dict:
        '''
        Defines a way of specifying a particular value based on
        a TimeSpan structure
        '''
        value: dict = {'Days': days, 'Hours': hours, 'Minutes': mins, 'Seconds': secs, 'Milliseconds': milliseconds}
        return value