import time
from math import fabs
from .game import Game
from src import Player, NPC
from paths import Bounce


class Pong(Game):
    """
    Two players swat a ball back and forth.
    """

    '''
    PLAYER INFO
    '''
    paddle_length = 10
    x_hit = 0

    '''
    BALL INFO
    '''
    ball_rate = 2
    resetting = False
    skip_frame = False
    laser_blink = False
    reset_time = 0
    reset_rate = 1

    def __init__(self, center, bound, pwm, player_1_controller, player_2_controller,
                 player_1_turret, player_2_turret, npc_turret):
        super().__init__(center, bound, pwm)
        self.player_1 = Player(bound, bound, pwm,
                               player_1_turret, player_1_controller,
                               no_x=True, fixed_x=int(center + bound/2))
        self.player_2 = Player(bound, bound, pwm,
                               player_2_turret, player_2_controller,
                               no_x=True, fixed_x=int(center - bound/2))
        self.ball = NPC(pwm, npc_turret)
        self.bounce = None

    def play_on(self):
        player_1_points = 0
        player_2_points = 0
        self.playing = True
        self.ball.laser.on()
        self.player_1.laser.on()
        self.player_2.laser.on()
        # vertical_hit = False
        # horizontal_hit = False
        while self.playing:
            ball = self.make_ball(self.ball_rate)
            prev_time = 0
            # xs, ys = ball.send((horizontal_hit, vertical_hit))
            while self.playing:
                self.curr_time = time.time()
                if self.curr_time - prev_time >= self.time_rate:
                    if not self.resetting:
                        # xs, ys = ball.send((horizontal_hit, vertical_hit))
                        xs, ys = ball.__next__()
                    else:
                        xs = self.center
                        ys = self.center
                    prev_time = self.curr_time
                    x_1, y_1 = self.player_1.set_servo()
                    x_2, y_2 = self.player_2.set_servo()
                    x_1_hit = fabs(x_1 - xs) <= self.x_hit
                    x_2_hit = fabs(x_2 - xs) <= self.x_hit
                    y_1_hit = fabs(y_1 - ys) <= self.paddle_length
                    y_2_hit = fabs(y_2 - ys) <= self.paddle_length
                    # Player 1 or 2 lose
                    if not y_1_hit and x_1_hit:
                        player_2_points += 1
                        self.resetting = True
                        self.reset_time = time.time()
                        break
                    elif not y_2_hit and x_2_hit:
                        player_1_points += 1
                        self.resetting = True
                        self.reset_time = time.time()
                        break
                    else:
                        top_hit = ys >= (self.center + self.bound/2)
                        bottom_hit = ys <= (self.center - self.bound/2)
                        # Player hit
                        if (y_1_hit and x_1_hit) or (y_2_hit and x_2_hit):
                            # vertical_hit = True
                            self.bounce.vertical_hit()
                            # horizontal_hit = False
                            self.bounce.rate += 0.1
                        # Top or bottom wall hit
                        elif top_hit or bottom_hit:
                            # vertical_hit = False
                            # horizontal_hit = True
                            self.bounce.horizontal_hit()
                        # else:
                        #     vertical_hit = False
                        #     horizontal_hit = False
                        # if not self.resetting:
                        #     xs, ys = ball.send((horizontal_hit,
                        #                         vertical_hit))
                    self.handle_ball_resetting()

    def handle_ball_resetting(self):
        """
        Handles all player info after firing, such as laser blinking
        :return:
        """
        if self.resetting:
            if not self.skip_frame:
                self.skip_frame = True
                if self.laser_blink:
                    self.ball.laser.on()
                else:
                    self.ball.laser.off()
                self.laser_blink = not self.laser_blink
            else:
                self.skip_frame = False
            if self.curr_time - self.reset_time > self.reset_rate:
                self.resetting = False
                self.ball.laser.on()

    def make_ball(self, angle=2, rate=2):
        self.bounce = Bounce(self.center, self.center, angle, rate)
        ball_servo = self.ball.follow_path(self.bounce.data())
        # Let the servos get into position. Yes, yield twice
        ball_servo.__next__()
        ball_servo.send((False, False))
        return ball_servo
