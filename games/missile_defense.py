import time
import random
from typing import Generator
from math import sqrt
from paths import Line, Circle, Corkscrew
from src import Player, NPC
from .game import Game
from src.player_controller import PlayerController
from src.turret import Turret
# TODO: Add missiles remaining counter that counts up until win
# TODO: Corkscrew missiles!


class MissileDefense(Game):
    """
    The player must aim and shoot at missile raining down on a peaceful city.
    """

    '''
    GAME INFO
    '''
    curr_time = 0
    num_missiles = 20

    '''
    PLAYER INFO
    '''
    # Delay until the player can fire again
    player_attack_rate = 1
    # Size of player attack
    bomb_radius = 10
    player_fired = False
    fire_time = 0
    skip_frame = False
    laser_blink = False
    '''
    MISSILE INFO
    '''
    # How long to delay until the missile comes alive
    missile_delay = 1
    # How much to increase the missile speed per success
    rate_increase = 0.1
    '''
    LIVES INFO
    '''
    lives = 10
    life_pos = 0

    def __init__(self, center, bound, pwm,
                 controller: PlayerController,
                 player_turret: Turret,
                 missile_turret: Turret,
                 life_turret: Turret):
        super().__init__(center, bound, pwm)
        '''
        INIT PLAYER
        '''
        self.player_turret = player_turret
        self.player = Player(bound, bound, pwm, player_turret, controller)
        self.player.laser.on()
        '''
        INIT MISSILE
        '''
        self.missile_turret = missile_turret
        self.missile = NPC(pwm, missile_turret)
        self.missile.laser.on()
        '''
        INIT LIFE COUNTER
        '''
        self.life_turret = life_turret
        self.life_counter = NPC(pwm, life_turret)
        self.life_pos = int(center + bound/2)
        # Put life counter out of bounds
        self.life_counter.set_servo(int(center - bound/2) - 10, int(center + bound/2))
        self.life_counter.laser.on()
        self.life_distance = int(bound/self.lives)

    def play_on(self):
        self.playing = True
        hit = False
        lose = False
        prev_time = 0
        missile_rate = 1
        missile = self.make_missile()
        missile_respawn = False
        respawn_time = time.time()
        while self.playing:
            if hit:
                missile_rate += self.rate_increase
            elif lose:
                self.lives -= 1
                self.life_pos -= self.life_distance
                self.life_counter.set_servo(int(self.center - self.bound/2) - 10,
                                            self.life_pos)
            if hit or lose:
                self.num_missiles -= 1
                hit = False
                lose = False
                self.missile.laser.off()
                missile = self.make_missile(missile_rate)
                missile_respawn = True
                respawn_time = time.time()
            # Win/lose conditions. Check lose first in case of lives=missiles=0
            if self.lives == 0:
                self.lose()
                break
            elif self.num_missiles == 0:
                self.win()
                break
            self.curr_time = time.time()
            if self.curr_time - prev_time >= self.time_rate:
                prev_time = self.curr_time
                p_x, p_y = self.player.set_servo()
                if not missile_respawn:
                    try:
                        m_x, m_y = missile.__next__()
                    except StopIteration:
                        lose = True
                    else:
                        if not self.player_fired and self.player.firing():
                            self.player_fired = True
                            self.fire_time = time.time()
                            dist_2_bomb = sqrt((m_y - p_y)**2 + (m_x - p_x)**2)
                            if dist_2_bomb <= self.bomb_radius:
                                hit = True
                else:
                    if self.curr_time - respawn_time > self.missile_delay:
                        missile_respawn = False
                        self.missile.laser.on()
                self.handle_player_firing()

    def handle_player_firing(self):
        """
        Handles all player info after firing, such as laser blinking
        :return:
        """
        if self.player_fired:
            if not self.skip_frame:
                self.skip_frame = True
                if self.laser_blink:
                    self.player.laser.on()
                else:
                    self.player.laser.off()
                self.laser_blink = not self.laser_blink
            else:
                self.skip_frame = False
            if self.curr_time - self.fire_time > self.player_attack_rate:
                self.player_fired = False
                self.player.laser.on()

    def make_missile(self, rate=1, npc: NPC=None) -> Generator:
        """
        Creates a new random missile
        :param rate:
        :param npc:
        :return:
        """
        y_low = int(self.center - self.bound / 2)
        y_high = int(self.center + self.bound / 2)
        x_start = random.randint(y_low, y_high)
        # Since the controllers can't reach the corners, restrict them
        x_end = random.randint(y_low + 15, y_high - 15)
        if self.num_missiles > 5:
            path = Line(x_start, y_high, x_end, y_low, rate)
        else:
            # Last five missiles get cray-cray
            path = Corkscrew(x_start, y_high, x_end, y_low, 10, 0, 1, rate)
        if npc is None:
            missile = self.missile.follow_path(path.data())
        else:
            missile = npc.follow_path(path.data())
        # Let the servos get into position. Yield once for init, yield again to move servos
        missile.__next__()
        missile.__next__()
        return missile

    def win(self):
        """
        "We're in the endgame now" - Wizard guy.
        :return:
        """
        # Free up the GPIO pin
        del self.player.laser
        del self.missile.laser
        del self.life_counter.laser
        npc1 = NPC(self.pwm, self.player_turret)
        npc2 = NPC(self.pwm, self.missile_turret)
        npc3 = NPC(self.pwm, self.life_turret)
        radius = 20
        rate = 0.1
        circle1 = Circle(415, 375, radius, 0, rate)
        circle2 = Circle(375, 375, radius, 0, rate)
        circle3 = Circle(335, 375, radius, 0, rate, clockwise=False)
        data1 = npc1.follow_path(circle1.data())
        data1.__next__()
        data1.__next__()
        npc1.laser.on()
        data2 = npc2.follow_path(circle2.data())
        data2.__next__()
        data2.__next__()
        npc2.laser.on()
        data3 = npc3.follow_path(circle3.data())
        data3.__next__()
        data3.__next__()
        npc3.laser.on()
        for _ in range(0, 400):
            if _ % 100 == 0:
                circle3.clockwise = False
            data1.__next__()
            data2.__next__()
            data3.__next__()

    def lose(self):
        """
        "Did we just lose?" - Sun-Count.
        :return:
        """
        # Free up the GPIO pin
        del self.player.laser
        del self.missile.laser
        del self.life_counter.laser
        npc1 = NPC(self.pwm, self.player_turret)
        npc2 = NPC(self.pwm, self.missile_turret)
        npc3 = NPC(self.pwm, self.life_turret)
        rate = 3
        m1 = self.make_missile(rate, npc1)
        m2 = self.make_missile(rate, npc2)
        m3 = self.make_missile(rate, npc3)
        prev_time = 0
        num_losers = 15
        while True:
            if num_losers == 0:
                break
            self.curr_time = time.time()
            if self.curr_time - prev_time >= self.time_rate:
                prev_time = self.curr_time
                try:
                    m1.__next__()
                except StopIteration:
                    m1 = self.make_missile(rate, npc1)
                    num_losers -= 1
                try:
                    m2.__next__()
                except StopIteration:
                    m2 = self.make_missile(rate, npc2)
                    num_losers -= 1
                try:
                    m3.__next__()
                except StopIteration:
                    m4 = self.make_missile(rate, npc3)
                    num_losers -= 1
