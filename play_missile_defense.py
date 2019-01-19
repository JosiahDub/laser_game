import Adafruit_PCA9685
from games import MissileDefense
from src import pro_controller_factory
from src.TURRETS import TURRET_2, TURRET_3, TURRET_4

left_pro, _ = pro_controller_factory()
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)
m = MissileDefense(375, 80, pwm, left_pro, TURRET_2, TURRET_3, TURRET_4)
m.play_on()
