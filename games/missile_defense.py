import time
import random
from typing import Generator
from math import sqrt
from paths import Line
from src import Player, NPC
from .game import Game
from src.player_controller import PlayerController
from src.turret import Turret
# TODO: Add lives laser that slowly trickles down


class MissileDefense(Game):
    """
    The player must aim and shoot at missile raining down on a peaceful city.
    """

    '''
    GAME INFO
    '''
    curr_time = 0

    '''
    PLAYER INFO
    '''
    # Delay until the player can fire again
    player_attack_rate = 1
    # Size of player attack
    bomb_radius = 10
    player_fire = False
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

    def __init__(self, center, bound, pwm,
                 controller: PlayerController,
                 player_turret: Turret,
                 missile_turret: Turret):
        super().__init__(center, bound, pwm)
        self.player = Player(bound, bound, pwm, player_turret, controller)
        self.player.laser.on()
        self.missile = NPC(pwm, missile_turret)
        self.missile.laser.on()
        self.player_fired = False

    def play_on(self):
        self.playing = True
        hit = False
        lose = False
        prev_time = 0
        player_score = 0
        homes_destroyed = 0
        missile_rate = 1
        missile = self.missile.follow_path(self.make_missile())
        missile_respawn = False
        respawn_time = time.time()
        while self.playing:
            if hit:
                player_score += 1
                missile_rate += self.rate_increase
            if lose:
                homes_destroyed += 1
            if hit or lose:
                hit = False
                lose = False
                self.missile.laser.off()
                missile = self.make_missile(missile_rate)
                missile_respawn = True
                respawn_time = time.time()
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
                        if not self.player_fired:
                            if self.player.firing():
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

    def make_missile(self, rate=1) -> Generator:
        """
        Creates a new random missile
        :param rate:
        :return:
        """
        y_low = int(self.center + self.bound / 2)
        y_high = int(self.center - self.bound/2)
        x_start = random.randint(y_high, y_low)
        x_end = random.randint(y_high, y_low)
        path = Line(x_start, y_low, x_end, y_high, rate)
        missile = self.missile.follow_path(path.data())
        # Let the servos get into position. Yes, yield twice
        missile.__next__()
        # FIXME: If x or y are too close to each other, this can lead to premature StopIteration
        missile.__next__()
        return missile
