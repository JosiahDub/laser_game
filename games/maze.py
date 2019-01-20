import time
from .game import Game
from src import Player, NPC
from paths import Circle
from src.player_controller import PlayerController
from src.turret import Turret


class Wall:
    thickness = 6

    def __init__(self, x_start, y_start, x_end=0, y_end=0):
        self.x_start = x_start
        self.y_start = y_start
        if not x_end:
            self.x_end = x_start + self.thickness
            self.is_vertical = True
        else:
            self.is_vertical = False
            self.x_end = x_end
        if not y_end:
            self.y_end = y_start + self.thickness
            self.is_horizontal = True
        else:
            self.is_horizontal = False
            self.y_end = y_end

    def has_collided(self, x, y):
        binding_values = {}
        if self.x_start <= x <= self.x_end and self.y_start <= y <= self.y_end:
            if self.is_vertical:
                if self.x_end - self.thickness/2 - x > 0:
                    binding_values['min_x'] = self.x_start
                else:
                    binding_values['max_x'] = self.x_end
            else:
                if self.y_end - self.thickness/2 - y > 0:
                    binding_values['min_y'] = self.y_start
                else:
                    binding_values['max_y'] = self.y_end
        return binding_values


class MazeWalls:
    def __init__(self, x_offset, y_offset):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.walls = []

    def add_wall(self, x_start, y_start, x_end=0, y_end=0):
        if x_end:
            x_end += self.x_offset
        if y_end:
            y_end += self.y_offset
        new_wall = Wall(x_start + self.x_offset, y_start + self.x_offset,
                        x_end, y_end)
        self.walls.append(new_wall)

    def check_collision(self, x, y):
        binding = {}
        for wall in self.walls:
            binding.update(wall.has_collided(x, y))
        return binding

# 100 divided into 6 with padding
# 0
# 16
# 33
# 49
# 66
# 82
# 100


WALLS = MazeWalls(325, 325)
# Left most third
WALLS.add_wall(y_start=82, y_end=100,  x_start=82)  # 1
WALLS.add_wall(y_start=66, x_start=82, x_end=100)   # 2
WALLS.add_wall(y_start=82, y_end=100,  x_start=66)  # 3
WALLS.add_wall(y_start=16, y_end=66,   x_start=66)  # 4
WALLS.add_wall(y_start=49, x_start=66, x_end=82)    # 5
WALLS.add_wall(y_start=33, x_start=66, x_end=82)    # 6
WALLS.add_wall(y_start=0,  y_end=16,   x_start=82)  # 7
# Middle third
WALLS.add_wall(y_start=82, x_start=49, x_end=66)    # 8
WALLS.add_wall(y_start=66, y_end=82,   x_start=49)  # 9
WALLS.add_wall(y_start=66, x_start=49, x_end=66)    # 10
WALLS.add_wall(y_start=16, y_end=82,   x_start=33)  # 11
WALLS.add_wall(y_start=49, x_start=33, x_end=49)    # 12
WALLS.add_wall(y_start=0,  y_end=33,   x_start=49)  # 13
# Right most third
WALLS.add_wall(y_start=49, y_end=82,   x_start=16)  # 14
WALLS.add_wall(y_start=49, x_start=0,  x_end=16)    # 15
WALLS.add_wall(y_start=33, x_start=0,  x_end=16)    # 16
WALLS.add_wall(y_start=16, x_start=16, x_end=33)    # 17
WALLS.add_wall(y_start=0,  y_end=16,   x_start=16)  # 18


class Maze(Game):

    # TOUCHDOWN
    endzone = [[0, 16], [0, 16]]

    def __init__(self, center, bound, pwm,
                 controller: PlayerController,
                 player_turret: Turret,
                 ):
        super().__init__(center, bound, pwm)
        self.player_turret = player_turret
        self.player = Player(bound, bound, pwm, player_turret, controller,
                             initial_x=415, initial_y=415,
                             x_center=375, y_center=375)
        self.player.laser.on()

    def play_on(self):
        self.playing = True
        binding = {}
        prev_time = 0
        while self.playing:
            curr_time = time.time()
            if curr_time - prev_time >= self.time_rate:
                prev_time = curr_time
                x, y = self.player.manual_servo(**binding)
                binding = WALLS.check_collision(x, y)
                centered_x = x - self.center
                centered_y = y - self.center
                # Check if the player scored the winning goal!!!
                if self.endzone[0][0] <= centered_x <= self.endzone[0][1] and \
                        self.endzone[1][0] <= centered_y <= self.endzone[1][1]:
                    self.win()
                    break

    def win(self):
        # Free up the GPIO pin
        del self.player.laser
        npc = NPC(self.pwm, self.player_turret)
        radius = 20
        rate = 0.1
        circle = Circle(375, 375, radius, 0, rate)
        data = npc.follow_path(circle.data())
        data.__next__()
        data.__next__()
        npc.laser.on()
        for _ in range(0, 400):
            if _ % 100 == 0:
                circle.clockwise = False
