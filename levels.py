import os
import abc
import random

import pygame

from flock import Flock
from boid import Boid
from attractor import Attractor
from settings import Settings
from statuses import BoidSex


class Level(abc.ABC):
    entrance_gate_position = None
    exit_gate_position = None

    def __init__(self, game):
        self.game = game
        self.canvas = game.canvas
        self.background = pygame.image.load(os.path.join('images', self.name.lower(), 'background.png'))
        self.attractors = []
        self.flock = None
        self.flock = Flock(self)
        self.has_visited = False
        self._level_complete = False

        if self.exit_gate_position:
            self.attractors.append(
                Attractor(self.exit_gate_position, 500, Settings.gate_radius * 2)
            )
        # 'Attractors': AttractorsRule(self, 1, [Attractor((300, 300), 50)]),

        self.init_level()

    @abc.abstractmethod
    def init_level(self):
        pass

    @abc.abstractmethod
    def level_complete_check(self):
        pass

    @property
    def level_complete(self):
        # Once passed, a level stays done, even if the test starts failing again
        if self._level_complete:
            return True
        if self.level_complete_check():
            self._level_complete = True
        return self._level_complete

    @property
    def contains_leader(self):
        return self.flock.leader is not None

    def update(self, duration):
        self.flock.update(duration)

    def draw(self):
        self.canvas.blit(self.background, (0, 0))
        # [
        #     item.draw(self.canvas)
        #     for item in self.attractors
        # ]
        self.flock.draw()
        if self.entrance_gate_position:
            pygame.draw.circle(self.canvas, pygame.Color('green'), self.entrance_gate_position, Settings.gate_radius, 2)

        if self.exit_gate_position:
            colour = pygame.Color('green') if self.level_complete else pygame.Color('red')

            pygame.draw.circle(self.canvas, colour, self.exit_gate_position, Settings.gate_radius, 2)


class Level01(Level):
    name = 'Level01'
    exit_gate_position = pygame.Vector2(1622, 554)
    introduction_text = """
    Welcome to our rainbow of butterflies, Oh Glorious Leader. 
    To prove your leadership skills, we look to you to guide us out of this dark forest and beyond.
    """
    aim_text = """Get at least 6 other butterflies through the gate and out of the forest"""

    def init_level(self):
        self.create_starting_flock()
        self.has_visited = True

    def level_complete_check(self):
        return len(self.flock.boids) <= 9

    def create_starting_flock(self):
        for i in range(10):
            location = pygame.Vector2(
                random.randint(275, 485),
                random.randint(840, 925)
            )
            velocity = pygame.Vector2(0, 0)
            velocity.from_polar((10, random.randint(220, 320)))
            sex = {0: BoidSex.FEMALE, 1: BoidSex.MALE}[i % 2]
            self.flock.boids.append(Boid(self.flock, location, velocity, sex, Settings.boid_adult_age))
            self.flock.leader = random.choice(self.flock.boids)


class Level02(Level):
    name = 'Level02'
    entrance_gate_position = pygame.Vector2(160, 430)
    exit_gate_position = pygame.Vector2(1552, 483)

    def init_level(self):
        pass

    def level_complete_check(self):
        pass


class Level03(Level):
    name = 'Level03'
    entrance_gate_position = pygame.Vector2(274, 608)
    exit_gate_position = pygame.Vector2(475, 339)

    def init_level(self):
        pass

    def level_complete_check(self):
        pass


class Level04(Level):
    name = 'Level04'
    entrance_gate_position = pygame.Vector2(1553, 400)
    # exit_gate_position = pygame.Vector2(114, 660)

    def init_level(self):
        pass

    def level_complete_check(self):
        pass
