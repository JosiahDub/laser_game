class Game:
    def __init__(self, center, bound, pwm,):
        self.bound = bound
        self.center = center
        self.pwm = pwm
        self.playing = False
        self.time_rate = 1/60
        self.curr_time = 0

    def play_on(self):
        ...
