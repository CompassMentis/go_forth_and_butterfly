import abc
import random

import pygame

import utilities
import boid
from obstacle import Obstacle
from settings import Settings
import statuses


class Rule(abc.ABC):
    def __init__(self, flock, weight=1.0, distance=0):
        self.flock = flock
        self.weight = weight
        self.distance = distance

    @abc.abstractmethod
    def apply(self, boid, duration):
        pass


class SeparationRule(Rule):
    def apply(self, boid, duration):
        """
           Steer to avoid crowding local flockmates
           Force = -(vector to centre (average location) of neighbours)
        """
        neighbours = self.flock.neighbours(boid, self.distance)
        if not len(neighbours):
            return

        centre = utilities.point_centre(neighbour.location for neighbour in neighbours)

        boid.apply_force(
            (boid.location - centre) * self.weight * duration
        )


class AlignmentRule(Rule):
    def apply(self, boid, duration):
        """
            Steer towards the average heading of local flockmates
            (Average velocity) * x% (suggested: 12.5% - 1/8)
            To keep it simple, use the previous heading
        """
        neighbours = self.flock.neighbours(boid, self.distance)
        if not len(neighbours):
            return

        average_velocity = utilities.average_velocity(neighbour.velocity for neighbour in neighbours)

        boid.apply_force(
            average_velocity * self.weight * duration
        )


class CohesionRule(Rule):
    def apply(self, boid, duration):
        """
            Steer to move towards the average position (center of mass) of local flockmates
            Average location (centre) of neighbouring boids, move x% (suggested: 1%) towards the centre.
        """

        neighbours = self.flock.neighbours(boid, self.distance)
        if not len(neighbours):
            return

        centre = utilities.point_centre(neighbour.location for neighbour in neighbours)

        boid.apply_force(
            (centre - boid.location) * self.weight * duration
        )


class BoundaryBoxRule(Rule):
    def __init__(self, flock, weight, distance, box_size):
        super().__init__(flock, weight, distance)
        self.box_size = box_size

    def apply(self, boid, duration):
        """
        If too close to the boundary, or across it, generate a force pushing back
        """

        # Too far left
        if boid.location.x < self.distance:
            boid.apply_force(
                pygame.Vector2(self.weight, 0)
            )

        # Too far right
        if boid.location.x > self.box_size.x - self.distance:
            boid.apply_force(
                pygame.Vector2(-self.weight, 0)
            )

        # Too high
        if boid.location.y < self.distance:
            boid.apply_force(
                pygame.Vector2(0, self.weight)
            )

        # Too far down
        if boid.location.y > self.box_size.y - self.distance:
            boid.apply_force(
                pygame.Vector2(0, -self.weight)
            )


class SteadyForceRule(Rule):
    def __init__(self, flock, force):
        super().__init__(flock, 1)
        self.force = force

    def apply(self, boid, duration):
        boid.apply_force(self.force * duration)


class Attractor:
    def __init__(self, location, weight):
        self.location = location
        self.weight = weight


class AttractorsRule(Rule):
    def __init__(self, flock, weight, attractors):
        super().__init__(flock, weight, 0)
        self.attractors = attractors

    def apply(self, boid, duration):
        for attractor in self.attractors:
            force = (attractor.location - boid.location).normalize() * attractor.weight
            boid.apply_force(force * duration)


class HungerRule(Rule):
    def __init__(self, flock, weight, food_sources):
        super().__init__(flock, weight, 0)
        self.food_sources = food_sources

    def apply(self, boid, duration):
        # Boid is attracted to the nearest food source, unless recently visited and empty
        if not boid.is_hungry:
            return

        if not self.food_sources:
            return

        food_sources = [
            (utilities.distance_between_points(food_source.location, boid.location), food_source)
            for food_source in self.food_sources
            if food_source not in boid.exhausted_food_sources
        ]

        if not food_sources:
            # food_source = random.choice(self.food_sources)
            return

        food_sources.sort()
        food_source = food_sources[0][1]

        force = (food_source.location - boid.location).normalize() * food_source.weight
        boid.apply_force(force * duration)


class ObstacleAvoidanceRule(Rule):
    def __init__(self, flock, weight, distance, obstacles):
        super().__init__(flock, weight, distance)
        self.obstacles = obstacles

    def apply(self, boid, duration):
        for obstacle in self.obstacles:
            distance = (boid.location - obstacle.location).length()
            if distance > self.distance:
                continue

            # If we were to travel forward the same distance as that to the centre of the obstacle
            # how far are we from the obstacle?
            passing_point = boid.location + boid.velocity.normalize() * distance

            obstacle_centre_to_passing_point = passing_point - obstacle.location
            if obstacle_centre_to_passing_point.length() > obstacle.radius * 1.5:
                continue

            weight = obstacle.weight if obstacle.weight else self.weight
            boid.apply_force(obstacle_centre_to_passing_point * weight * duration)


class GravityLandingRule(Rule):
    def __init__(self, flock, weight):
        super().__init__(flock, weight)

    def apply(self, boid, duration):
        if boid.status == statuses.BoidStatus.LANDING:
            boid.apply_force(pygame.Vector2(0, Settings.gravity_velocity) * self.weight)


class Flock:
    def __init__(self, game):
        self.game = game
        self.canvas = game.canvas

        self.obstacles = [
            Obstacle(pygame.Vector2(300, 300), 50),
            Obstacle(pygame.Vector2(600, 300), 50),
            Obstacle(pygame.Vector2(300, 600), 50),
        ] + \
        [
            Obstacle(pygame.Vector2(1000, 150 + i * 50), 50)
            for i in range(5)
        ]

        self.rules = {
            'Separation': SeparationRule(self, 8, 50),
            'Alignment': AlignmentRule(self, 1.0, 200),
            'Cohesion': CohesionRule(self, 0.1, 200),
            'Boundaries': BoundaryBoxRule(self, 8, 100, Settings.screen_size),
            'Obstacles': ObstacleAvoidanceRule(self, 0.3, 400, self.obstacles),
            'LandingGravity': GravityLandingRule(self, 10),
            'Hunger': HungerRule(self, 50, game.food_sources),
            # 'Wind': SteadyForceRule(self, pygame.Vector2(50, 0)),
            # 'Attractors': AttractorsRule(self, 1, [Attractor((300, 300), 50)]),
        }

        self._distances = {}
        self._neighbours = {}
        self.boids = []

    def add_random_boids(self, number_of_boids):
        for _ in range(number_of_boids):
            location = pygame.Vector2(
                random.randint(Settings.border, Settings.screen_size.x - Settings.border),
                random.randint(Settings.border, Settings.screen_size.y - Settings.border)
            )
            velocity = pygame.Vector2(0, 0)
            speed = Settings.minimum_starting_speed + \
                    random.random() * (Settings.maximum_starting_speed - Settings.minimum_starting_speed)
            angle = random.randint(0, 360)
            velocity.from_polar((speed, angle))
            self.boids.append(
                boid.Boid(self, location=location, velocity=velocity)
            )

    def calculate_distances(self):
        self._distances = {}
        for a in self.boids:
            for b in self.boids:
                if (a, b) in self._distances:
                    continue

                if a == b:
                    self._distances[(a, b)] = 0
                    continue

                distance = a.location.distance_to(b.location)
                self._distances[(a, b)] = distance
                self._distances[(b, a)] = distance

    def calculate_neighbours(self):
        maximum_distance = max(rule.distance for rule in self.rules.values())

        self._neighbours = {}
        for a in self.boids:
            self._neighbours[a] = [
                boid
                for boid in self.boids
                if boid is not a and self._distances[(a, boid)] < maximum_distance
            ]

    def neighbours(self, boid, maximum_distance):
        return [
            neighbour
            for neighbour in self._neighbours[boid]
            if self._distances[(boid, neighbour)] <= maximum_distance
        ]

    def make_babies(self, location):
        for _ in range(random.randint(Settings.minimum_number_of_babies, Settings.maximum_number_of_babies)):
            baby_location = pygame.Vector2(
                location.y + random.randint(-Settings.maximum_baby_distance, Settings.maximum_baby_distance),
                location.x + random.randint(-Settings.maximum_baby_distance, Settings.maximum_baby_distance),
            )
            self.boids.append(boid.Boid(self, location=baby_location, velocity=pygame.Vector2(0, -3), age=0))

    def update(self, duration):
        self.calculate_distances()
        self.calculate_neighbours()
        for boid in self.boids:
            for rule in self.rules.values():
                rule.apply(boid, duration)
        [boid.update(duration) for boid in self.boids]

        # Remove starved boids
        self.boids = [boid for boid in self.boids if boid.food > 0]

    def draw(self):
        [boid.draw() for boid in self.boids]
        [obstacle.draw(self.canvas) for obstacle in self.obstacles]
