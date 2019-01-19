from math import sin, cos, pi, fabs
from .path import Path


class Circle(Path):

    def __init__(self, x_center, y_center, radius, angle, rate, clockwise=True):
        super().__init__(rate)
        self.x_center = x_center
        self.y_center = y_center
        self._radius = radius
        self._angle = angle
        self._clockwise = clockwise
        # Reverse, reverse!
        if clockwise:
            self._rate *= -1

    def data(self):
        x_start = self._radius * sin(self._angle) + self.x_center
        y_start = self._radius * cos(self._angle) + self.y_center
        yield int(x_start), int(y_start)
        angle_rate = self._angle + self._rate
        while True:
            x = self._radius * sin(angle_rate) + self.x_center
            y = self._radius * cos(angle_rate) + self.y_center
            yield int(x), int(y)
            angle_rate += self._rate
            # Check to normalize
            if angle_rate >= 2*pi:
                angle_rate -= 2*pi
            elif angle_rate <= -2*pi:
                angle_rate += 2 * pi

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, angle):
        self._angle = angle

    @Path.rate.setter
    def rate(self, rate):
        self._rate = rate

    @property
    def clockwise(self):
        return self._clockwise

    @clockwise.setter
    def clockwise(self, clockwise):
        self._clockwise = clockwise
        if clockwise:
            self._rate = -1 * fabs(self._rate)
        else:
            self._rate = fabs(self._rate)
