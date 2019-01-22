import random
from math import sin, cos, copysign, fabs, atan2
from typing import Generator, Tuple
from .path import Path


class Bounce(Path):
    def __init__(self, x_start: int, y_start: int, angle_rad: float, rate: float):
        super().__init__(rate)
        self.x_start = x_start
        self.y_start = y_start
        self._angle = angle_rad
        self.x_rate = rate * cos(self._angle)
        self.y_rate = rate * sin(self._angle)

    def old_data(self) -> Generator[Tuple[int, int], Tuple[bool, bool], None]:
        """
        Coroutine to advance an object at a certain rate until colliding with a wall.

        Call __next__() to initialize and get back the starting position
        Call send((horizontal_hit, vertical_hit)) to keep getting data
        There is no closing condition, so .close() exits
        :return:
        """
        x = self.x_start
        y = self.y_start
        yield x, y
        while True:
            x += self.x_rate
            y += self.y_rate
            # Get whether the object has collided with a wall
            horizontal_hit, vertical_hit = yield int(x), int(y)
            # Simply reverse the x/y rate depending on the wall type
            # TODO: could add a little variance in the angle with every bounce
            if horizontal_hit:
                self.y_rate *= -1
            if vertical_hit:
                self.x_rate *= -1

    def data(self) -> Generator[Tuple[int, int], None, None]:
        """
        Coroutine to advance an object at a certain rate until colliding with a wall.

        Call __next__() to initialize and get back the starting position
        Call send((horizontal_hit, vertical_hit)) to keep getting data
        There is no closing condition, so .close() exits
        :return:
        """
        x = self.x_start
        y = self.y_start
        yield x, y
        while True:
            x += self.x_rate
            y += self.y_rate
            yield int(x), int(y)

    def horizontal_hit(self):
        self.y_rate *= -1

    def vertical_hit(self, random_bounce=False):
        self.x_rate *= -1
        if random_bounce:
            self._angle = atan2(self.y_rate, self.x_rate)
            self.angle += random.uniform(-0.1, 0.1)


    @Path.rate.setter
    def rate(self, rate):
        """
        Change the base rate. X and Y rate are calculated accordingly
        :param rate:
        :return:
        """
        # Get the sign of the rates before calculating
        x_sign = copysign(1, self.x_rate)
        y_sign = copysign(1, self.y_rate)
        self._rate = rate
        # Multiply by the original sign to retain direction
        self.x_rate = x_sign * fabs(rate * cos(self._angle))
        self.y_rate = y_sign * fabs(rate * sin(self._angle))

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, angle):
        """
        Change the angle. X and Y rate are calculated accordingly
        :param angle:
        :return:
        """
        self._angle = angle
        self.x_rate = self._rate * cos(self._angle)
        self.y_rate = self._rate * sin(self._angle)
