import math

camera_slope = 2

class Vector():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    @staticmethod
    def from_angle(angle):
        return Vector(math.cos(angle), 0.0, math.sin(angle))
        
    def copy(self):
        return Vector(self.x, self.y, self.z)
    
    def magnitude(self):
        return math.sqrt(self.magnitude_squared())
    
    def magnitude_squared(self):
        return self.x * self.x + self.y * self.y + self.z * self.z
    
    def ground_magnitude(self):
        return math.sqrt(self.ground_magnitude_squared())
    
    def ground_magnitude_squared(self):
        return self.x * self.x + self.z * self.z
    
    def ground_angle(self):
        vertical = self.z
        horizontal = self.x
        return math.atan2(vertical, horizontal)
    
    def ground_angle_degrees(self):
        return math.degrees(self.ground_angle())
        
    def draw_angle_degrees(self):
        vertical = self.y + self.z / camera_slope
        horizontal = self.x
        return math.degrees(math.atan2(vertical, horizontal))
    
    def normalized(self):
        return self / self.magnitude()
        
    def ground_cross(self):
        return Vector(-self.z, 0.0, self.x)
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        
    def __mul__(self, other):
        return Vector(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other, self.z / other)
    
    def __str__(self):
        return '(%f, %f, %f)' % (self.x, self.y, self.z)