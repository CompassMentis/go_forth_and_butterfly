import datetime


class TimeKeeper:
    def __init__(self):
        self.start = datetime.datetime.now()

    @property
    def current_time(self):
        return datetime.datetime.now() - self.start

    @property
    def is_mating_season(self):
        return 5 < self.current_time.seconds < 65
