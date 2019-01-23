from tkinter import *
import Adafruit_PCA9685
from games import Pong, MissileDefense, Maze
from src.TURRETS import TURRET_2, TURRET_3, TURRET_4
from src import pro_controller_factory


class Picker:

    def __init__(self):
        self.root = Tk()
        self.root.geometry('1920x1080')

        self.maze_button = Button(self.root, text='Maze',
                                  command=self.play_maze,
                                  width=1080)
        self.maze_button.grid(row=0, sticky=E+W)
        self.pong_button = Button(self.root, text='Pong',
                                  command=self.play_pong)
        self.pong_button.grid(row=1, sticky=E+W)
        self.missile_defense_button = Button(self.root, text='Missile Defense',
                                             command=self.play_missile_defense)
        self.missile_defense_button.grid(row=2, sticky=E+W)
        mainloop()

    def play_maze(self):
        left, right = pro_controller_factory()

        pwm = Adafruit_PCA9685.PCA9685()
        pwm.set_pwm_freq(60)

        maze = Maze(375, 100, pwm, left, TURRET_3)
        maze.play_on()

    def play_pong(self):
        c_1, c_2 = pro_controller_factory()
        pwm = Adafruit_PCA9685.PCA9685()
        pwm.set_pwm_freq(60)
        p = Pong(375, 100, pwm, c_1, c_2, TURRET_2, TURRET_4, TURRET_3)
        p.play_on()

    def play_missile_defense(self):
        left_pro, _ = pro_controller_factory()
        pwm = Adafruit_PCA9685.PCA9685()
        pwm.set_pwm_freq(60)
        m = MissileDefense(375, 80, pwm, left_pro, TURRET_2, TURRET_3, TURRET_4)
        m.play_on()


if __name__ == '__main__':
    Picker()
