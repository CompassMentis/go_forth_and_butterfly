import datetime
import os
import math

import pygame

from settings import Settings
from enums import Events


class TimeKeeper:
    def __init__(self, game):
        self.start = datetime.datetime.now()
        self.canvas = game.canvas
        self.game = game
        path = 'images', 'time_keeper'
        self.background = pygame.image.load(os.path.join(*path, 'clock_face.png'))
        self.background_rect = self.background.get_rect()
        self.background_rect.center = Settings.time_keeper_location

        self.moon_image = pygame.image.load(os.path.join(*path, 'moon.png'))
        self.sun_image = pygame.image.load(os.path.join(*path, 'sun.png'))
        self.current_period = ''
        self.time_offset = 0

    @property
    def current_time(self):
        real_seconds_since_start = (datetime.datetime.now() - self.start).total_seconds()
        game_seconds_since_start = real_seconds_since_start * Settings.time_keeper_multiplier
        game_seconds_since_start_of_day = game_seconds_since_start % Settings.time_keeper_one_day_duration
        return game_seconds_since_start_of_day

    def set_time(self, seconds):
        """
        Reset clock as it if started running x seconds ago
        """
        self.start = datetime.datetime.now() - datetime.timedelta(seconds=seconds)

    @property
    def is_mating_season(self):
        return 5 < self.current_time.seconds < 65

    @property
    def is_day(self):
        return self.current_time < Settings.sunset_start_time

    @property
    def is_sunset(self):
        return Settings.sunset_start_time <= self.current_time < Settings.night_start_time

    @property
    def is_night(self):
        return Settings.night_start_time <= self.current_time < Settings.sunrise_start_time

    @property
    def is_sunrise(self):
        return Settings.sunrise_start_time <= self.current_time

    def draw(self):
        self.canvas.blit(self.background, self.background_rect)
        # Calculate angle

        if self.is_day:
            period = 'day'
            start_angle = Settings.day_start_angle
            period_duration = Settings.day_duration
            duration_into_period = self.current_time - Settings.day_start_time
            period_angle_duration = Settings.day_angle_duration
            image = self.sun_image
        elif self.is_sunset:
            period = 'sunset'
            start_angle = Settings.sunset_start_angle
            period_duration = Settings.sunset_duration
            duration_into_period = self.current_time - Settings.sunset_start_time
            period_angle_duration = Settings.sunset_angle_duration
            image = self.sun_image
        elif self.is_night:
            period = 'night'
            start_angle = Settings.night_start_angle
            period_duration = Settings.night_duration
            duration_into_period = self.current_time - Settings.night_start_time
            period_angle_duration = Settings.night_angle_duration
            image = self.moon_image
        else:
            period = 'sunrise'
            start_angle = Settings.sunrise_start_angle
            period_duration = Settings.sunrise_duration
            duration_into_period = self.current_time - Settings.sunrise_start_time
            period_angle_duration = Settings.sunrise_angle_duration
            image = self.moon_image

        if period != self.current_period:
            self.current_period = period
            event = {
                'day': Events.START_OF_DAYTIME,
                'sunset': Events.START_OF_SUNSET,
                'night': Events.START_OF_NIGHTTIME,
                'sunrise': Events.START_OF_SUNRISE
            }[period]
            self.game.handle_event(event)

        period_angle = duration_into_period / period_duration * period_angle_duration

        angle = start_angle + period_angle + Settings.time_keeper_angle_offset + 90

        x = -math.cos(math.radians(angle)) * Settings.time_keeper_radius + Settings.time_keeper_location[0]
        y = -math.sin(math.radians(angle)) * Settings.time_keeper_radius + Settings.time_keeper_location[1]
        rect = image.get_rect()
        rect.center = (x, y)

        self.canvas.blit(image, rect)
