import random
import collections
import datetime

import pygame

from settings import Settings

# TODO: Remove this
from statuses import BoidStatus, BoidSex
import utilities

random.seed(10)


class AbstractBoid:
    pass


class Boid:
    def __init__(self, flock, location, velocity, sex=None, age=0):
        self.flock = flock
        self.game = flock.game
        self.canvas = flock.canvas
        self.location = location
        self.velocity = velocity
        self.sex = random.choice(list(BoidSex)) if sex is None else sex
        self.mass = 1
        self.history = collections.deque(maxlen=50)
        self.is_leader = False
        self.status = BoidStatus.FLYING
        self.waiting_period = None
        self.food = Settings.boid_starting_food_level * random.randint(90, 110) / 100
        self.age = age
        self.potential_mate = None
        self.last_mated = 0

        # Keep track of which flowers have been visited and exhausted
        self.exhausted_food_sources = collections.deque(maxlen=4)
        self.feeding_from = None

    @property
    def recently_mated(self):
        return (self.age - self.last_mated) < Settings.minimum_time_between_matings

    @property
    def is_adult(self):
        return self.age >= Settings.boid_adult_age

    @property
    def is_hungry(self):
        return self.food <= Settings.boid_hungry_level

    def draw(self):
        if self.is_leader:
            pygame.draw.circle(self.canvas, pygame.Color('black'), self.location, 20, 2)
            pygame.draw.circle(self.canvas, pygame.Color('black'), self.location, 40, 1)
            pygame.draw.circle(self.canvas, pygame.Color('white'), self.location, 41, 1)
            pygame.draw.circle(self.canvas, pygame.Color('black'), self.location, 42, 1)
        colour = pygame.Color('red') \
            if self.is_hungry \
            else {BoidSex.MALE: pygame.Color('blue'), BoidSex.FEMALE: pygame.Color('green')}[self.sex]
        pygame.draw.circle(self.canvas, pygame.Color(colour), self.location, 5)
        # pygame.draw.line(
        #     self.canvas, pygame.Color('blue'), self.location, self.location + self.velocity.normalize() * 50, 2
        # )
        # if len(self.history) > 1:
        #     pygame.draw.lines(self.canvas, pygame.Color('green'), closed=False, points=self.history)

    def apply_force(self, force, essential=False):
        acceleration = force / self.mass
        velocity = self.velocity + acceleration
        speed, direction = velocity.as_polar()

        # Whilst LANDING, any upward force is ignored (anything above 180 degrees)
        if self.status == BoidStatus.LANDING and force and not essential:
            direction = direction % 360
            if direction > 180:
                return

        speed = min(speed, Settings.boid_maximum_speed)
        self.velocity.from_polar((speed, direction))
        # if self.is_leader:
        #     print('New speed: ', speed)

    def turn_left(self):
        # TODO: DRY?
        speed, angle = self.velocity.as_polar()
        force = pygame.Vector2(0, 0)
        force.from_polar((Settings.steering_force, angle - 90))
        self.apply_force(force, essential=True)

    def turn_right(self):
        speed, angle = self.velocity.as_polar()
        force = pygame.Vector2(0, 0)
        force.from_polar((Settings.steering_force, angle + 90))
        self.apply_force(force, essential=True)

    def speed_up(self):
        speed, angle = self.velocity.as_polar()
        force = pygame.Vector2(0, 0)
        force.from_polar((Settings.steering_force, -angle))
        self.apply_force(force)

    def slow_down(self):
        speed, angle = self.velocity.as_polar()
        force = pygame.Vector2(0, 0)
        force.from_polar((Settings.steering_force, angle))
        self.apply_force(force)

    def toggle_landing(self):
        if self.status in [BoidStatus.LANDED, BoidStatus.LANDING]:
            self.status = BoidStatus.FLYING
            print('Flying')
        else:
            self.status = BoidStatus.LANDING
            print('Landing')

    def landed_on_food_source(self):
        for food_source in self.flock.game.food_sources:
            if utilities.distance_between_points(self.location, food_source.location) <= food_source.radius:
                return food_source
        return None

    def update(self, duration):
        self.history.append(list(self.location))
        self.food -= duration
        self.age += duration
        # self.location += (self.velocity * duration)

        if self.potential_mate and (self.potential_mate.recently_mated or self.potential_mate.is_hungry):
            self.potential_mate = None

        # TODO: Separate functions for during_mating_season and start_of_mating_season?
        if self.game.is_mating_season and self.sex == BoidSex.FEMALE and not self.is_hungry and not self.recently_mated:
            if self.potential_mate is None:
                potential_mates = [
                    boid
                    for boid in self.flock.boids
                    if boid.sex == BoidSex.MALE
                       and boid.status == BoidStatus.WAITING_TO_MATE
                       and not boid.recently_mated
                ]
                if potential_mates:
                    self.potential_mate = random.choice(potential_mates)
                    self.status = BoidStatus.LANDING_TO_MATE

        if not self.game.is_mating_season or self.is_hungry:
            self.potential_mate = None

        if self.potential_mate:
            self.apply_force(
                utilities.normalise_force_to_weight(
                    self.potential_mate.location - self.location, Settings.mating_attraction_force_weight
                ), essential=True
            )

        # During mating season, start landing or, if hungry, start flying
        if self.game.is_mating_season and self.sex == BoidSex.MALE and not self.is_hungry:
            if self.status == BoidStatus.FLYING:
                self.status = BoidStatus.LANDING_TO_MATE

        if self.is_hungry and self.status in [BoidStatus.LANDING_TO_MATE, BoidStatus.WAITING_TO_MATE]:
            self.status = BoidStatus.FLYING
            self.apply_force(pygame.Vector2(0, -10), essential=True)

        if not self.game.is_mating_season:
            if self.status == BoidStatus.WAITING_TO_MATE:
                self.status = BoidStatus.FLYING
                self.apply_force(pygame.Vector2(0, -10), essential=True)
            elif self.status == BoidStatus.LANDING_TO_MATE:
                self.status = BoidStatus.FLYING

        if self.status == BoidStatus.FEEDING:

            # Any food left? If so, eat
            if self.feeding_from.level > 0.1:
                food = min(self.feeding_from.level, duration * Settings.feeding_speed, Settings.boid_maximum_food_level - self.food)
                self.feeding_from.level -= food
                self.food += food
                return

            # No food left, start flying
            self.exhausted_food_sources.append(self.feeding_from)
            self.feeding_from = None
            self.status = BoidStatus.FLYING
            return

        if self.is_hungry:
            # Hungry. Have we reached a food source?
            food_source = self.landed_on_food_source()
            if food_source:
                self.status = BoidStatus.FEEDING
                self.feeding_from = food_source

        if self.status in [BoidStatus.FLYING, BoidStatus.LANDING, BoidStatus.LANDING_TO_MATE]:
            self.location += (self.velocity * duration)

        if self.status in [BoidStatus.LANDING, BoidStatus.LANDING_TO_MATE] \
                and self.location.y >= (Settings.screen_size.y - Settings.landing_range):
            self.location.y = Settings.screen_size.y - Settings.landing_range
            if self.status == BoidStatus.LANDING_TO_MATE:
                if self.potential_mate:
                    self.potential_mate.last_mated = self.potential_mate.age
                    self.last_mated = self.age
                    self.flock.make_babies(self.location)
                    self.status = BoidStatus.FLYING
                    self.potential_mate.status = BoidStatus.FLYING
                self.status = BoidStatus.WAITING_TO_MATE
            else:
                self.status = BoidStatus.LANDED
                print('Landed')
                self.waiting_period = Settings.landed_period

        elif self.status == BoidStatus.LANDED:
            self.waiting_period -= duration
            if self.waiting_period <= 0:
                self.status = BoidStatus.FLYING
