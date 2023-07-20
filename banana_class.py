from numpy import arctan
from math import pi

class banana():
    def __init__(self, x_min, y_min, x_max, y_max, avg_l, avg_r):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.avg_l = avg_l
        self.avg_r = avg_r
        self.size = self.getSize()

    def getSize(self):
        return (self.x_max-self.x_min) * (self.y_max-self.y_min)

    def getRectangle(self):
        return ((self.x_min, self.y_min), (self.x_max, self.y_max))

    def getRotation(self):
        slope = (self.avg_r-self.avg_l)/(self.x_max - self.x_min)

        #Should be (slope)/(pi/2), but works better with (pi/3) due to the object thickness
        return min(1, max(-1, arctan(slope)/(pi/3)))

    def getLinePoints(self):
        return ((int(self.x_min), int(self.avg_l)), (int(self.x_max), int(self.avg_r)))

    def getCenter(self):
        return (self.x_min + (self.x_max - self.x_min)), (self.y_min + (self.y_max - self.y_min))

    def __gt__(self, other_banana):
        return self.size > other_banana.size

    def __str__(self):
        center_x, center_y = self.getCenter()
        return f"A banana of size {self.size}, at position x: {center_x}, y: {center_y}"

    def __repr__(self):
        center_x, center_y = self.getCenter()
        return f"A banana of size {self.size}, at position x: {center_x}, y: {center_y}"      
