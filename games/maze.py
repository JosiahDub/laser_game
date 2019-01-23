import time
from .game import Game
from src import Player, NPC
from paths import Circle
from src.player_controller import PlayerController
from src.turret import Turret


class Wall:
    thickness = 6

    def __init__(self, x_start, y_start, x_end=None, y_end=None):
        self.x_start = x_start
        self.y_start = y_start
        if x_end is None:
            self.x_end = x_start + self.thickness
            self.is_vertical = True
        else:
            self.is_vertical = False
            self.x_end = x_end
        if y_end is None:
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

    # 100 divided into 6 with padding
    wall_positions = {0: 0, 1: 16, 2: 33, 3: 49, 4: 66, 5: 82, 6: 100}

    def __init__(self, x_offset, y_offset):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.walls = []

    def add_wall(self, x_start, y_start, x_end=None, y_end=None):
        if x_end is not None:
            x_end = self.wall_positions[x_end] + self.x_offset
        if y_end is not None:
            y_end = self.wall_positions[y_end] + self.y_offset
        new_wall = Wall(self.wall_positions[x_start] + self.x_offset,
                        self.wall_positions[y_start] + self.x_offset,
                        x_end,
                        y_end)
        self.walls.append(new_wall)

    def check_collision(self, x, y):
        binding = {}
        for wall in self.walls:
            binding.update(wall.has_collided(x, y))
        return binding


WALLS = MazeWalls(325, 325)
# Left most third
WALLS.add_wall(y_start=5, y_end=6,   x_start=5)  # 1
WALLS.add_wall(y_start=4, x_start=5, x_end=6)    # 2
WALLS.add_wall(y_start=5, y_end=6,   x_start=4)  # 3
WALLS.add_wall(y_start=3, y_end=4,   x_start=4)  # 4
WALLS.add_wall(y_start=3, x_start=4, x_end=5)    # 5
WALLS.add_wall(y_start=1, y_end=3,   x_start=5)  # 6
WALLS.add_wall(y_start=0, y_end=2,   x_start=4)  # 7
# Middle third
WALLS.add_wall(y_start=5, x_start=3, x_end=4)    # 8
WALLS.add_wall(y_start=4, y_end=5,   x_start=3)  # 9
WALLS.add_wall(y_start=4, x_start=3, x_end=4)    # 10
WALLS.add_wall(y_start=3, x_start=2, x_end=3)    # 11
WALLS.add_wall(y_start=1, y_end=2,   x_start=3)  # 12
WALLS.add_wall(y_start=1, x_start=3, x_end=4)    # 13
# Right most third
WALLS.add_wall(y_start=1, y_end=5,   x_start=2)  # 14
WALLS.add_wall(y_start=5, x_start=1, x_end=2)    # 15
WALLS.add_wall(y_start=2, y_end=4,   x_start=1)  # 16
WALLS.add_wall(y_start=2, x_start=0, x_end=1)    # 17
WALLS.add_wall(y_start=1, x_start=1, x_end=2)    # 18
WALLS.add_wall(y_start=0, y_end=1,   x_start=1)  # 19


class Maze(Game):
    """
    Find your way to the end!
    """

    '''
    GAME INFO
    '''
    # TOUCHDOWN
    endzone = [[0, 16], [0, 16]]

    lose_time = 360

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
        start_time = time.time()
        while self.playing:
            curr_time = time.time()
            if curr_time - prev_time >= self.time_rate:
                prev_time = curr_time
                x, y = self.player.manual_servo(**binding)
                binding = WALLS.check_collision(x, y)
                centered_x = x - self.center + self.bound/2
                centered_y = y - self.center + self.bound/2
                # Check if the player scored the winning goal!!!
                if self.endzone[0][0] <= centered_x <= self.endzone[0][1] and \
                        self.endzone[1][0] <= centered_y <= self.endzone[1][1]:
                    self.win()
                    self.playing = False
                if curr_time - start_time >= self.lose_time:
                    self.playing = False

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
        for _ in range(0, 600):
            if _ % 100 == 0:
                circle.clockwise = False
            data.__next__()
