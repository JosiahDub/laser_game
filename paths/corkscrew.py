from math import sin, cos, atan2, pi, fabs
from .circle import Circle


class Corkscrew(Circle):
    
    def __init__(self, x_center, y_center, x_end, y_end, radius, angle, angular_rate, linear_rate, clockwise=True):
        super().__init__(x_center, y_center, radius, angle, angular_rate, clockwise)
        self.x_end = x_end
        self.y_end = y_end
        self._linear_rate = linear_rate
        self.linear_angle = atan2(y_end - y_center, x_end - x_center)
        self.x_rate = linear_rate * cos(self.linear_angle)
        self.y_rate = linear_rate * sin(self.linear_angle)
        
    def data(self):
        x = self._radius * sin(self._angle) + self.x_center
        y = self._radius * cos(self._angle) + self.y_center
        keep_going = True
        yield int(x), int(y)
        angle_rate = self._angle + self._rate
        while keep_going:
            keep_going = False
            if fabs(x - self.x_end) > fabs(self.x_rate):
                self.x_center += self.x_rate
                keep_going = True
            if fabs(y - self.y_end) > fabs(self.y_rate):
                self.y_center += self.y_rate
                keep_going = True
            x = self._radius * sin(angle_rate) + self.x_center + self.x_rate
            y = self._radius * cos(angle_rate) + self.y_center + self.y_rate
            yield int(x), int(y)
            angle_rate += self._rate
        yield self.x_end, self.y_end
