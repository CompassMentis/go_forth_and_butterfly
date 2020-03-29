import logging

import os
import abc
import random

import pygame

from flock import Flock
from boid import Boid
from attractor import Attractor
from settings import Settings
from enums import BoidSex, Events, GameState
from time_keeper import TimeKeeper
from flower import Flower

logger = logging.getLogger(__name__)


class Level(abc.ABC):
    entrance_gate_position = None
    exit_gate_position = None
    new_events = []
    landing_zone_top = 820
    maximum_plant_level = landing_zone_top
    minimum_plant_level = 600
    exit_gate_open = True
    name = None
    extra_help_lines = []

    def __init__(self, game):
        self.game = game
        self.canvas = game.canvas
        self.background = pygame.image.load(os.path.join('images', self.name.lower(), 'background.png'))

        self.console_image = pygame.image.load(os.path.join('images', self.name.lower(), 'console.png'))
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
        self.flowers = []

        self.init_level()

    @abc.abstractmethod
    def init_level(self):
        pass

    @abc.abstractmethod
    def level_complete_check(self):
        pass

    def on_first_entry(self):
        pass

    def leader_enters(self):
        if not self.has_visited:
            self.game.event_handler.activate(self.new_events)
            self.game.help_lines += self.extra_help_lines
            self.on_first_entry()
            self.game.state = GameState.READ_INTRO


    # def first_visitor(self):
    #     """First time any boid visits this level"""
    #
    # def visit(self):
    #     if not self.has_visited:
    #         self.first_visitor()
    #         self.has_visited = True

    @property
    def level_complete(self):
        if logger.getEffectiveLevel() <= logging.DEBUG:
            return True

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
        [flower.update(duration) for flower in self.flowers]

    def draw(self):
        self.canvas.blit(self.background, (0, 0))
        # [
        #     item.draw(self.canvas)
        #     for item in self.flowers
        # ]
        [flower.draw() for flower in self.flowers]
        self.flock.draw()
        if self.entrance_gate_position:
            pygame.draw.circle(self.canvas, pygame.Color('green'), self.entrance_gate_position, Settings.gate_radius, 2)

        if self.exit_gate_position:
            if not self.exit_gate_open:
                colour = pygame.Color('red')
            elif not self.level_complete:
                colour = pygame.Color('blue')
            else:
                colour = pygame.Color('green')
            pygame.draw.circle(self.canvas, colour, self.exit_gate_position, Settings.gate_radius, 2)

        self.canvas.blit(self.console_image, (0, 0))


class Level01(Level):
    name = 'Level01'
    exit_gate_position = pygame.Vector2(1622, 554)
    introduction_text = """
    Welcome to our rainbow of butterflies, Oh Glorious Leader. 
    To prove your leadership skills, we look to you to guide us out of this dark forest
    and beyond.
    """
    aim_text = """Get at least 6 other butterflies through the gate and out of the forest"""

    def init_level(self):
        self.create_starting_flock()
        self.has_visited = True

    def level_complete_check(self):
        return len(self.flock.boids) <= 4

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
    introduction_text = """
    Lots of space here. A good place to try out your voice.
    Use the 'S' key to sing, and watch the others fly towards you
    """
    aim_text = """Get all butterflies through the gate"""
    extra_help_lines = ["'S' to sing and attract the others towards you"]
    entrance_gate_position = pygame.Vector2(160, 430)
    exit_gate_position = pygame.Vector2(1552, 483)
    new_events = [
        Events.SHOUT
    ]

    def init_level(self):
        pass

    def level_complete_check(self):
        return len(self.flock.boids) <= 1


class Level03(Level):
    name = 'Level03'
    entrance_gate_position = pygame.Vector2(274, 608)
    exit_gate_position = pygame.Vector2(475, 339)
    exit_gate_open = False
    introduction_text = """It is getting late. Everyone will need to get some sleep.
    Use 'L' to start landing, fly down to stop. Then Sing to attract the others.
    Everyone who is landed at night will be safe. The others will perish.
    """
    aim_text = "Get 5 butterflies to the next level, not counting yourself"
    extra_help_lines = ["""'L' to land. Sleep at night or perish"""]
    new_events = [
        Events.TOGGLE_LANDING
    ]

    def init_level(self):
        pass

    def level_complete_check(self):
        next_level = self.game.next_level(self)
        return len(next_level.flock.boids) >= 5

    def on_first_entry(self):
        self.game.time_keeper = TimeKeeper(self.game)
        self.game.time_keeper.set_time(60/Settings.time_keeper_multiplier)

    def on_start_of_sunrise(self):
        self.exit_gate_open = True


class Level04(Level):
    name = 'Level04'
    entrance_gate_position = pygame.Vector2(1553, 400)
    exit_gate_position = pygame.Vector2(114, 660)
    introduction_text = """Everyone will need to eat, or they will perish.
    Those flowers look tasty"""
    aim_text = "Eat, then move everyone to the next level"

    def init_level(self):
        for location in [(235, 892), (570, 775), (970, 810)]:
            self.flowers.append(
                Flower(self.game, location, age=Settings.flower_adult_age * random.randint(50, 100) / 100)
            )
        self.game.active_forces.add('Hunger')

    def level_complete_check(self):
        return len(self.flock.boids) <= 1

    def on_first_entry(self):
        self.game.boids_need_food = True
        # if logger.getEffectiveLevel() <= logging.DEBUG:
        self.game.time_keeper.set_time(0)
        for boid in self.flock.boids:
            boid.food = Settings.boid_hungry_level * random.randint(100, 180) / 100
            logger.debug(f'{boid} food set to {boid.food}')


class Level05(Level):
    name = 'Level05'
    entrance_gate_position = pygame.Vector2(655, 600)
    # exit_gate_position = pygame.Vector2(1642, 690)
    introduction_text = """Lots of space but nothing to eat.
    Use the 'P' button to plant some flowers"""
    aim_text = """Last level - for now - watch this space - no goal (yet)"""
    extra_help_lines = ["""'P' to plant flowers - in the soil, not the sky"""]
    new_events = [
        Events.PLANT_FLOWER,
    ]

    def init_level(self):
        pass

    def level_complete_check(self):
        # TODO: Complete this
        return False
