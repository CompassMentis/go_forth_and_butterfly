import random
import os
import datetime

import pygame

from settings import Settings
from flock import Flock
from flower import Flower
from time_keeper import TimeKeeper
import statuses

# TODO: Remove this
random.seed(10)


class Game:
    def __init__(self, canvas):
        self.canvas = canvas
        self.clock = pygame.time.Clock()
        self.time_keeper = TimeKeeper()
        self.images = self.load_images()
        self.background = pygame.image.load('images/background.png')
        self.background_width = self.background.get_rect().width
        self.background_offset = 0
        self.recent_buttons = {}

        self.flowers = []
        self.food_sources = []
        for i in range(1, 8):
            self.flowers.append(
                Flower(self, pygame.Vector2(200 * i, 900))
            )

        flock = Flock(self)
        flock.add_random_boids(Settings.number_of_boids)
        flock.boids[0].is_leader = True
        self.flocks = [flock]

    @property
    def is_mating_season(self):
        return self.time_keeper.is_mating_season

    def load_images(self):
        result = {}
        source_folder = 'images/butterflies/'
        # for butterfly_type in os.listdir(source_folder):
        for butterfly_type in ['large_red']:
            if not os.path.isdir(source_folder + butterfly_type):
                continue

            for angle in range(0, 360, 15):
                for step in range(16):
                    result[(butterfly_type, angle, step)] = pygame.image.load(
                        f'{source_folder}{butterfly_type}/butterfly_{angle:03}_step_{step:02}.png'
                    )
        return result

    def draw(self):
        self.canvas.blit(self.background, (-self.background_offset, 0))
        [flower.draw() for flower in self.flowers]
        [flock.draw() for flock in self.flocks]
        [food_source.draw() for food_source in self.food_sources]
        if self.is_mating_season:
            pygame.draw.rect(self.canvas, pygame.Color('orange'), (20, 20, 50, 50), 5)
        pygame.display.flip()

    def unbounce_button(self, button):
        last_time = self.recent_buttons.get(button)
        now = datetime.datetime.now()
        self.recent_buttons[button] = now

        return last_time is None or (now - last_time) > datetime.timedelta(milliseconds=200)

    def plant_seed(self, location):
        self.flowers.append(Flower(self, location))

    def update(self, duration):
        [flower.update(duration) for flower in self.flowers]
        [flock.update(duration) for flock in self.flocks]
        [food_source.update(duration) for food_source in self.food_sources]

        leader_boids = [
            boid
            for flock in self.flocks
            for boid in flock.boids
            if boid.is_leader
        ]

        for event in pygame.event.get():
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_LEFT:
                [boid.turn_left() for boid in leader_boids]

            elif event.key == pygame.K_RIGHT:
                [boid.turn_right() for boid in leader_boids]

            elif event.key == pygame.K_UP:
                [boid.speed_up() for boid in leader_boids]

            elif event.key == pygame.K_DOWN:
                [boid.slow_down() for boid in leader_boids]

            elif event.key == pygame.K_l and self.unbounce_button(event.key):
                print('L - unbounced')
                [boid.toggle_landing() for boid in leader_boids]

            elif event.key == pygame.K_p and self.unbounce_button(event.key):
                print('P - plant a seed')
                [self.plant_seed(boid.location) for boid in leader_boids if boid.status == statuses.BoidStatus.LANDED]

    def run(self):
        self.clock.tick(30)
        while True:
            duration = self.clock.tick(30) / 1000
            self.update(duration)
            self.draw()
