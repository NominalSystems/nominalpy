'''
        [ NOMINAL SYSTEMS ]
This code is developed by Nominal Systems
to aid with communication to the public API.
'''

from datetime import datetime

'''
Defines a value that can be casted to a particular data type based on
the data that is stored. This is a helper function that can be useful
for converting raw data between Vector3 and Matrix3x3 data types.
'''
class Value:

    '''
    The raw data passed in from the constructor. This will be in
    a JSON format.
    '''
    data: str = ""


    def __init__(self, data: str) -> None:
        '''
        Defines the default constructor for the data type that 
        exists within the value.
        '''
        self.data = data
        if self.data == "":
            self.data = None

    @classmethod
    def from_vec3 (self, x: float, y: float, z: float):
        '''
        Defines a way for specifying a particular value based
        on a Vector3 structure.
        '''
        value: str = "{X: %f, Y: %f, Z: %f}" % (x, y, z)
        return Value(value)
    
    @classmethod
    def from_mat33 (self, m1: tuple, m2: tuple, m3: tuple):
        '''
        Defines a way for specifying a particular value based
        on a Matrix3x3 structure.
        '''
        value: str = "{'Values': [%f, %f, %f, %f, %f, %f, %f, %f, %f]}" % (m1[0], m1[1], m1[2], m2[0], m2[1], m2[2], m3[0], m3[1], m3[2])
        return Value(value)
    
    @classmethod
    def from_datetime (self, year: int, month: int, day: int, hour: int = 0, min: int = 0, sec: int = 0) -> None:
        '''
        Defines a way of specifying a particular value based on
        a DateTime structure.
        '''
        dt: datetime = datetime(year, month, day, hour, min, sec)
        value: str = "{'Year': '%d', 'Month': %d, 'Day': %d, 'Hour': %d, 'Minute': %d, 'Second': %d}" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        return Value(value)
    
    @property
    def vec3 (self) -> tuple:
        '''
        Returns the value in the form of a vector3 with
        three components; X, Y and Z.
        '''
        if self.data == None: return (0, 0, 0)
        split = self.data.split(": ")
        x = float(split[1][:-3])
        y = float(split[2][:-3])
        z = float(split[3][:-3])
        return (x, y, z)

    @property
    def mat33 (self) -> tuple:
        '''
        Returns the value in the form of a matrix 3x3 with the
        nine values listed in row form.
        '''
        if self.data == None: return ((0, 0, 0), (0, 0, 0), (0, 0, 0))
        s = self.data.replace("],", "").replace("[", "").split(" ")[1:14]
        if len(s) < 13: return ((0, 0, 0), (0, 0, 0), (0, 0, 0))
        return (
            (float(s[0]),   float(s[1]),     float(s[2])), 
            (float(s[5]),   float(s[6]),     float(s[7])), 
            (float(s[10]),  float(s[11]),    float(s[12]))
        )
    
    def __str__ (self) -> str:
        '''
        Returns the data stored within the value
        as a string cast.
        '''
        return self.data if self.data != None else ""
