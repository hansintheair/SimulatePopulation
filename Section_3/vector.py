from random import random
from math import hypot

class Vector:
    """ A vector stores information and operations regarding the 
        direction and speed of motion.
    
        Parameters:
            vx (int or float):  x component of Vector.
            vy (int or float):  y component of Vector.
        Properties:
            mag (int or float): get/set magnitude of Vector.
            unit (Vector):      Get unit vector of Vector.
    """

    def __init__(self, vx, vy):
        self.vx = vx
        self.vy = vy
    @property
    def mag(self):
        """ Get the magnitude of the vector."""
        return hypot(self.vx, self.vy)
    @mag.setter
    def mag(self, mag):
        """ Set the vector to the specified magnitude, maintaining its direction."""
        scalar = mag / self.mag
        self.vx = self.vx * scalar
        self.vy = self.vy * scalar
    @property
    def unit(self):
        """ Get the unit vector of the vector."""
        mag = self.mag
        return Vector(self.vx / mag, self.vy / mag)

    def __repr__(self):
        return f"Vector({self.vx!r}, {self.vy!r})"

    def __bool__(self):
        """ Check truthiness of vector."""
        return bool(abs(self))

    def __add__(self, other):
        """ Add two vectors."""
        vx = self.vx + other.vx
        vy = self.vy + other.vy
        return Vector(vx, vy)

    def __sub__(self, other):
        """ Subtract two vectors."""
        return self + Vector(-other.vx, other.vy)

    def __mul__(self, other):
        """ Scale the vector up if float or int, calculate dot product if Vector."""
        if type(other) == type(self):
            return self.vx * other.vx + self.vy * other.vy
        return Vector(self.vx * other, self.vy * other)
    
    def __rmul__(self, other):
        """ Called if int or float * Vector."""
        return self.__mul__(other)

    def __truediv__(self, scalar):
        """ Scale the vector down if float or int."""
        return Vector(self.vx / scalar, self.vy / scalar)

    @staticmethod
    def generate(mag):
        vector = Vector(random() - 0.5, random() - 0.5)
        vector.mag = mag
        return vector