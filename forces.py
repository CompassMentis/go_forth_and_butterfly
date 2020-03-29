import logging
import random
import abc

import pygame

import enums
import utilities
from settings import Settings
from states import states

logger = logging.getLogger(__name__)


class Force(abc.ABC):
    def __init__(self, flock, weight=1.0, distance=0):
        self.flock = flock
        self.weight = weight
        self.distance = distance

    @abc.abstractmethod
    def apply(self, boid, duration):
        pass


class SeparationForce(Force):
    help_text = 'keep a little bit of a distance'

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


class AlignmentForce(Force):
    help_text = 'fly in the same direction as their neighbours, especially the leader'

    def apply(self, boid, duration):
        """
            Steer towards the average heading of local flockmates
            (Average velocity) * x% (suggested: 12.5% - 1/8)
            To keep it simple, use the previous heading
        """
        neighbours = self.flock.neighbours(boid, self.distance, weighted_leader=True)
        if not len(neighbours):
            return

        average_velocity = utilities.average_velocity(neighbour.velocity for neighbour in neighbours)

        boid.apply_force(
            average_velocity * self.weight * duration
        )


class CohesionForce(Force):
    help_text = 'join their neighbours'

    def apply(self, boid, duration):
        """
            Steer to move towards the average position (center of mass) of local flockmates
            Average location (centre) of neighbouring boids, move x% (suggested: 1%) towards the centre.
        """

        neighbours = self.flock.neighbours(boid, self.distance, weighted_leader=True)
        if not len(neighbours):
            return

        centre = utilities.point_centre(neighbour.location for neighbour in neighbours)

        boid.apply_force(
            (centre - boid.location) * self.weight * duration
        )


class BoundaryBoxForce(Force):
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


class ConstantForce(Force):
    def __init__(self, flock, force):
        super().__init__(flock, 1)
        self.force = force

    def apply(self, boid, duration):
        boid.apply_force(self.force * duration)


class AttractorForce(Force):
    def __init__(self, flock):
        super().__init__(flock, 0, 0)

    def apply(self, boid, duration):
        for attractor in self.flock.level.attractors:
            if utilities.distance_between_points(
                    boid.location, attractor.location
            ) < attractor.distance:
                force = (attractor.location - boid.location).normalize() * attractor.weight
                boid.apply_force(force * duration)


class HungerForce(Force):
    def __init__(self, flock, weight, food_sources):
        super().__init__(flock, weight, 0)
        self.food_sources = food_sources

    def apply(self, boid, duration):
        # Boid is attracted to the nearest food source, unless recently visited and empty
        if not boid.is_hungry:
            return

        if not self.food_sources:
            return

        # TODO: Re-introduce later
        # food_sources = [
        #     (utilities.distance_between_points(food_source.location, boid.location), food_source)
        #     for food_source in self.food_sources
        #     if food_source not in boid.exhausted_food_sources
        # ]

        # if not food_sources:
        #     # food_source = random.choice(self.food_sources)
        #     return
        #
        # food_sources.sort()
        # food_source = food_sources[0][1]

        food_source = random.choice(self.food_sources)

        force = (food_source.location - boid.location).normalize() * food_source.weight
        # logger.debug(f'Hungry force applied: {force * duration}')
        boid.apply_force(force * duration)


class ObstacleAvoidanceForce(Force):
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


class GravityLandingForce(Force):
    def __init__(self, flock, weight):
        super().__init__(flock, weight)

    def apply(self, boid, duration):
        if boid.status == states.LANDING:
            boid.apply_force(pygame.Vector2(0, Settings.gravity_velocity) * self.weight)
