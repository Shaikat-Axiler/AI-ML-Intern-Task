# Polymorphism
# Create classes:

# Circle
# Rectangle

# Both should have an area() method.

import math

class Circle:
    def area(self, radius):
        self.radius = radius
        print(f"Area of Circle: {math.pi * self.radius ** 2}")

class Rectangle:
    def area(self, length, width):
        self.length = length
        self.width = width
        print(f"Area of Rectangle: {self.length * self.width}")

ob1 = Circle()
ob1.area(5)
ob2 = Rectangle()
ob2.area(5, 3)