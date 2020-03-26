import pygame

from settings import Settings
from food_source import FoodSource
from obstacle import Obstacle


class Flower:
    _flower_image = pygame.image.load('images/yellow-flower.png')
    _flower_rect = _flower_image.get_rect()
    seed_image = pygame.image.load('images/seed.png')
    seed_rect = seed_image.get_rect()

    def __init__(self, game, location):
        self.age = -Settings.flower_seed_period
        self.location = pygame.Vector2(location)
        self.game = game
        self.canvas = game.canvas

    def update(self, duration):
        if self.age >= Settings.flower_adult_age:
            return

        self.age += duration

        # Just became an adult, so create a new food source
        if self.age >= Settings.flower_adult_age:
            location = self.location + Settings.flower_food_source_offset
            radius = Settings.flower_food_source_radius
            weight = Settings.flower_food_source_weight
            self.game.food_sources.append(
                FoodSource(
                    location=location,
                    radius=radius,
                    weight=weight,
                    level=Settings.flower_food_source_starting_level,
                    canvas=self.canvas
                )
            )

            # TODO: Tidy up?
            for flock in self.game.flocks:
                flock.obstacles.append(
                    Obstacle(location, radius, 1)
                )

    def draw(self):
        if self.age < 0:
            # Draw seed
            self.seed_rect.midbottom = self.location
            self.canvas.blit(self.seed_image, self.seed_rect)
            return

        # Draw flower
        scaling_factor = self.age / Settings.flower_adult_age
        if scaling_factor < 0.97:
            size = int(self._flower_rect.width * scaling_factor), int(self._flower_rect.height * scaling_factor)
            image = pygame.transform.scale(self._flower_image, size)
            rect = image.get_rect()
        else:
            rect = self._flower_rect
            image = self._flower_image

        rect.midbottom = self.location
        self.canvas.blit(image, rect)
