import random

import pygame

import boid
from obstacle import Obstacle
import forces
from settings import Settings


class Flock:
    def __init__(self, level):
        self.level = level
        self.game = level.game
        self.canvas = level.game.canvas
        # self.attractors = []

        # self.obstacles = [
        #     Obstacle(pygame.Vector2(300, 300), 50),
        #     Obstacle(pygame.Vector2(600, 300), 50),
        #     Obstacle(pygame.Vector2(300, 600), 50),
        # ] + \
        # [
        #     Obstacle(pygame.Vector2(1000, 150 + i * 50), 50)
        #     for i in range(5)
        # ]

        self.obstacles = []

        self.forces = {
            'Separation': forces.SeparationForce(self, 8, 50),
            'Alignment': forces.AlignmentForce(self, 1.0, 200),
            'Cohesion': forces.CohesionForce(self, 0.1, 200),
            'Boundaries': forces.BoundaryBoxForce(self, 8, 100, Settings.screen_size),
            'Obstacles': forces.ObstacleAvoidanceForce(self, 0.3, 400, self.obstacles),
            'LandingGravity': forces.GravityLandingForce(self, 10),
            'Attractor': forces.AttractorForce(self),
            'Hunger': forces.HungerForce(self, 550, self.game.food_sources),
            # 'Wind': SteadyForceRule(self, pygame.Vector2(50, 0)),
            # 'Attractors': AttractorsRule(self, 1, [Attractor((300, 300), 50)]),
        }

        self._distances = {}
        self._neighbours = {}
        self.boids = []
        self.leader = None

    @property
    def active_forces(self):
        return [self.forces[force_name] for force_name in self.game.active_forces]

    # def add_random_boids(self, number_of_boids):
    #     for _ in range(number_of_boids):
    #         location = pygame.Vector2(
    #             random.randint(Settings.border, Settings.screen_size.x - Settings.border),
    #             random.randint(Settings.border, Settings.screen_size.y - Settings.border)
    #         )
    #         velocity = pygame.Vector2(0, 0)
    #         speed = Settings.minimum_starting_speed + \
    #                 random.random() * (Settings.maximum_starting_speed - Settings.minimum_starting_speed)
    #         angle = random.randint(0, 360)
    #         velocity.from_polar((speed, angle))
    #         self.boids.append(
    #             boid.Boid(self, location=location, velocity=velocity)
    #         )

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
        maximum_distance = max(rule.distance for rule in self.active_forces)

        self._neighbours = {}
        for a in self.boids:
            self._neighbours[a] = [
                boid
                for boid in self.boids
                if boid is not a and self._distances[(a, boid)] < maximum_distance
            ]

    def weighted_leader(boids, factor):
        """
        Count the leader multiple times
        """
        result = []
        for boid in boids:
            if boids.is_leader:
                result += [boid] * factor
            else:
                result.append(boid)

        return result

    def neighbours(self, boid, maximum_distance, weighted_leader=False):
        result = []
        for neighbour in self._neighbours[boid]:
            if self._distances[(boid, neighbour)] > maximum_distance:
                continue

            if weighted_leader and neighbour.is_leader:
                result += [neighbour] * Settings.leader_weighing_factor
            else:
                result.append(neighbour)

        return result

        # return [
        #     neighbour
        #     for neighbour in self._neighbours[boid]
        #     if self._distances[(boid, neighbour)] <= maximum_distance
        # ]

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
            for force in self.active_forces:
                force.apply(boid, duration)
            # for rule in self.rules.values():
            #     rule.apply(boid, duration)
        [boid.update(duration) for boid in self.boids]
        # angle, speed = self.leader.velocity.as_polar()
        # print(int(angle), int(speed))

        # Remove deceased boids
        self.boids = [boid for boid in self.boids if boid.alive]
        if self.leader and not self.leader.alive:
            if self.boids:
                self.leader = random.choice(self.boids)

    def draw(self):
        [boid.draw() for boid in self.boids]

        # [
        #     item.draw(self.canvas)
        #     for item in self.obstacles
        # ]
