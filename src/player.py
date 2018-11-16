from gpiozero import LED
from .turret import Turret
from .player_controller import PlayerController


class Player:

    def __init__(self,
                 x_bound: int, y_bound: int,
                 pwm, turret: Turret,
                 controller: PlayerController,
                 x_offset: int=0, y_offset: int=0,
                 no_x: bool=False, no_y: bool=False,
                 fixed_x: int=0, fixed_y: int=0):
        self.controller = controller
        self.turret = turret
        self.laser = LED(turret.laser_pin)
        self.pwm = pwm
        self.x_pin = turret.x_pin
        self.y_pin = turret.y_pin
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.no_x = no_x
        self.no_y = no_y
        self.fixed_x = fixed_x
        if fixed_x:
            self.servo_x = fixed_x
            pwm.set_pwm(self.x_pin, 0, fixed_x + turret.x_cal)
        else:
            self.servo_x = -1
        self.fixed_y = fixed_y
        if fixed_y:
            self.servo_y = fixed_y
            pwm.set_pwm(self.x_pin, 0, fixed_y + turret.y_cal)
        else:
            self.servo_y = -1
        # Calculate the values for y = mx + b
        # x needs to be swapped for our setup
        self.xm = x_bound / (controller.x_min - controller.x_max)
        self.ym = y_bound / (controller.y_max - controller.y_min)
        self.xb = turret.x_center - self.xm * controller.x_center
        self.yb = turret.y_center - self.ym * controller.y_center

    def set_servo(self, restrict_x=False, restrict_y=False):
        x, y = self.controller.joystick()
        if not self.no_x and not restrict_x:
            self.servo_x = int(self.xm * x + self.xb)
            self.pwm.set_pwm(self.x_pin, 0, self.servo_x
                                            + self.turret.x_cal
                                            + self.x_offset)
        if not self.no_y and not restrict_y:
            self.servo_y = int(self.ym * y + self.yb)
            self.pwm.set_pwm(self.y_pin, 0, self.servo_y
                                            + self.turret.y_cal
                                            + self.y_offset)
        return self.servo_x + self.x_offset, self.servo_y + self.y_offset

    def get_position(self):
        return self.servo_x + self.x_offset, self.servo_y + self.y_offset

    def firing(self):
        return self.controller.fire()
