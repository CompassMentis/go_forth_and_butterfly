import random
import os
import datetime

import pygame

from settings import Settings
from flock import Flock
import levels
import forces
from flower import Flower
from time_keeper import TimeKeeper
import utilities
import statuses

# TODO: Remove this
random.seed(10)


class Game:
    def __init__(self, canvas):
        self.canvas = canvas
        self.clock = pygame.time.Clock()
        self.time_keeper = TimeKeeper()
        self.images = self.load_images()
        # self.background = pygame.image.load('images/background.png')
        # self.background_width = self.background.get_rect().width
        # self.background_offset = 0
        self.recent_buttons = {}

        self.levels = [
            levels.Level01(self),
            levels.Level02(self),
            levels.Level03(self),
            levels.Level04(self),
        ]

        # Start at level 0
        self.level = self.levels[0]

        # Start with basic flocking behaviour
        # and stay within the screen

        self.active_forces = {
            'Separation', 'Alignment', 'Cohesion', 'Boundaries', 'Attractor',
        }

        # self.flowers = []
        # self.food_sources = []
        # for i in range(1, 8):
        #     self.flowers.append(
        #         Flower(self, pygame.Vector2(200 * i, 900))
        #     )
        #
        # flock = Flock(self)
        # flock.add_random_boids(Settings.number_of_boids)
        # flock.boids[0].is_leader = True
        # self.flocks = [flock]

    def next_level(self, level):
        current_level_index = self.levels.index(level)
        if current_level_index > len(self.levels):
            return None

        return self.levels[current_level_index + 1]

    def previous_level(self, level):
        current_level_index = self.levels.index(level)

        if current_level_index == 0:
            return None

        return self.levels[current_level_index - 1]

    @property
    def is_mating_season(self):
        return self.time_keeper.is_mating_season

    def load_images(self):
        result = {}
        for size in 'small', 'large':
            for sex in 'male', 'female':
                source_image = pygame.image.load(
                    os.path.join('images', 'butterflies', f'{size}_{sex}.png')
                )

                for angle in range(0, 360, 15):
                    result[(size, sex, angle)] = utilities.rotate_in_place(source_image, angle + 90)

        # for butterfly_type in os.listdir(source_folder):
        # for butterfly_type in ['large_red']:
        #     if not os.path.isdir(source_folder + butterfly_type):
        #         continue
        #
        #     for angle in range(0, 360, 15):
        #         for step in range(16):
        #             result[(butterfly_type, angle, step)] = pygame.image.load(
        #                 f'{source_folder}{butterfly_type}/butterfly_{angle:03}_step_{step:02}.png'
        #             )
        return result

    def draw(self):
        # self.canvas.blit(self.background, (-self.background_offset, 0))
        # [flower.draw() for flower in self.flowers]
        # [flock.draw() for flock in self.flocks]
        # [food_source.draw() for food_source in self.food_sources]
        # if self.is_mating_season:
        #     pygame.draw.rect(self.canvas, pygame.Color('orange'), (20, 20, 50, 50), 5)
        self.level.draw()
        pygame.display.flip()

    def unbounce_button(self, button):
        last_time = self.recent_buttons.get(button)
        now = datetime.datetime.now()
        self.recent_buttons[button] = now

        return last_time is None or (now - last_time) > datetime.timedelta(milliseconds=200)

    def plant_seed(self, location):
        self.flowers.append(Flower(self, location))

    def set_current_level(self):
        for level in self.levels:
            if level.contains_leader:
                self.level = level
                return

    def update(self, duration):
        # [flower.update(duration) for flower in self.flowers]
        # [flock.update(duration) for flock in self.flocks]
        # [food_source.update(duration) for food_source in self.food_sources]

        # leader_boids = [
        #     boid
        #     for flock in self.flocks
        #     for boid in flock.boids
        #     if boid.is_leader
        # ]

        leader = self.level.flock.leader

        for event in pygame.event.get():
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_LEFT:
                leader.turn_left()

            elif event.key == pygame.K_RIGHT:
                leader.turn_right()

            elif event.key == pygame.K_UP:
                leader.speed_up()

            elif event.key == pygame.K_DOWN:
                leader.slow_down()

            elif event.key == pygame.K_SPACE:
                leader.reset_speed()

            # elif event.key == pygame.K_l and self.unbounce_button(event.key):
            #     leader.toggle_landing()
            #
            # elif event.key == pygame.K_p and self.unbounce_button(event.key):
            #     [self.plant_seed(boid.location) for boid in leader_boids if boid.status == statuses.BoidStatus.LANDED]

        self.level.update(duration)

        self.set_current_level()

    def run(self):
        self.clock.tick(30)
        while True:
            duration = self.clock.tick(30) / 1000
            self.update(duration)
            self.draw()
