from .nunchuck import nunchuck
from .pro_controller import ProController
"""
Defines the data associated with a player's nunchuk
"""
class PlayerController:
    x_center: int = ...
    y_center: int = ...
    x_min: int = ...
    x_max: int = ...
    y_min: int = ...
    y_max: int = ...

    def joystick(self):
        ...

    def fire(self):
        ...



class PlayerNunchuk(PlayerController):
    def __init__(self, x_center, y_center, x_min, x_max, y_min, y_max):
        self.x_center = x_center
        self.y_center = y_center
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        try:
            self.n = nunchuck()
        except OSError:
            raise OSError('Ensure the controller is plugged in') from None

    def joystick(self):
        return self.n.joystick()


class PlayerLeftPro(PlayerController):
    def __init__(self, x_center, y_center, x_min, x_max, y_min, y_max):
        self.x_center = x_center
        self.y_center = y_center
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        try:
            self.pro = ProController()
        except OSError:
            raise OSError('Ensure the controller is plugged in') from None

    def joystick(self):
        return self.pro.left_joystick()

    def fire(self):
        return self.pro.button_zl()


class PlayerRightPro(PlayerController):
    def __init__(self, x_center, y_center, x_min, x_max, y_min, y_max):
        self.x_center = x_center
        self.y_center = y_center
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        try:
            self.pro = ProController()
        except OSError:
            raise OSError('Ensure the controller is plugged in') from None

    def joystick(self):
        return self.pro.right_joystick()

    def fire(self):
        return self.pro.button_zr()
