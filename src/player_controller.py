from typing import Tuple
from math import atan2, sqrt
from src.WiiController.nunchuk import Nunchuk
from src.WiiController.pro_controller import ProController
from src.WiiController.classic_controller import ClassicController


class PlayerController:

    def __init__(self, x_center, y_center, x_min, x_max, y_min, y_max):
        self.x_center = x_center
        self.y_center = y_center
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def joystick(self) -> Tuple[int, int]:
        ...

    def angle_and_radius(self) -> Tuple[float, float]:
        x, y = self.joystick()
        angle = atan2(y - self.y_center, x - self.x_center)
        radius = sqrt((y - self.y_center) ** 2 + (x - self.x_center) ** 2)
        return angle, radius

    def fire(self):
        ...


class PlayerNunchuk(PlayerController):
    def __init__(self, x_center, y_center, x_min, x_max, y_min, y_max):
        super().__init__(x_center, y_center, x_min, x_max, y_min, y_max)
        try:
            self.n = Nunchuk()
        except OSError:
            raise OSError('Ensure the controller is plugged in') from None

    def joystick(self):
        return self.n.joystick()

    def fire(self):
        return self.n.button_z()


class PlayerLeftPro(PlayerController):
    def __init__(self, x_center, y_center, x_min, x_max, y_min, y_max, pro):
        super().__init__(x_center, y_center, x_min, x_max, y_min, y_max)
        if pro is None:
            try:
                self.pro = ProController()
            except OSError:
                raise OSError('Ensure the controller is plugged in') from None
        else:
            self.pro = pro

    def joystick(self):
        return self.pro.left_joystick()

    def fire(self):
        return self.pro.button_zl()


class PlayerRightPro(PlayerController):
    def __init__(self, x_center, y_center, x_min, x_max, y_min, y_max, pro=None):
        super().__init__(x_center, y_center, x_min, x_max, y_min, y_max)
        if pro is None:
            try:
                self.pro = ProController()
            except OSError:
                raise OSError('Ensure the controller is plugged in') from None
        else:
            self.pro = pro

    def joystick(self):
        return self.pro.right_joystick()

    def fire(self):
        return self.pro.button_zr()


class PlayerLeftClassic(PlayerController):
    def __init__(self, x_center, y_center, x_min, x_max, y_min, y_max, classic):
        super().__init__(x_center, y_center, x_min, x_max, y_min, y_max)
        if classic is None:
            try:
                self.classic = ClassicController()
            except OSError:
                raise OSError('Ensure the controller is plugged in') from None
        else:
            self.classic = classic

    def joystick(self):
        return self.classic.left_joystick()

    def fire(self):
        return self.classic.button_zl()


class PlayerRightClassic(PlayerController):
    def __init__(self, x_center, y_center, x_min, x_max, y_min, y_max, classic=None):
        super().__init__(x_center, y_center, x_min, x_max, y_min, y_max)
        if classic is None:
            try:
                self.classic = ClassicController()
            except OSError:
                raise OSError('Ensure the controller is plugged in') from None
        else:
            self.classic = classic

    def joystick(self):
        return self.classic.right_joystick()

    def fire(self):
        return self.classic.button_zr()


def pro_controller_factory():
    try:
        pro = ProController()
    except OSError:
        raise OSError('Ensure the controller is plugged in') from None
    left = PlayerLeftPro(31, 35, 4, 57, 7, 62, pro=pro)
    right = PlayerRightPro(16, 17, 3, 30, 3, 31, pro=pro)
    return left, right


def classic_controller_factory():
    try:
        classic = ClassicController()
    except OSError:
        raise OSError('Ensure the controller is plugged in') from None
    left = PlayerLeftClassic(32, 32, 5, 59, 5, 59, classic=classic)
    right = PlayerRightClassic(16, 16, 3, 29, 3, 29, classic=classic)
    return left, right
