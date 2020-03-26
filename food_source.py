import math

import pygame

from settings import Settings


class FoodSource:
    def __init__(self, location, radius, weight, level, canvas):
        self.location = location
        self.radius = radius
        self.level = level
        self.canvas = canvas
        self.weight = weight
        # self.font = pygame.font.SysFont('Arial', 24)

    def update(self, duration):
        self.level = min(
            self.level + duration * Settings.flower_food_source_top_up_speed,
            Settings.flower_food_source_maximum_level
        )

    def draw(self):
        rect = [self.location.x - self.radius, self.location.y - self.radius, self.radius * 2, self.radius * 2]
        angle = 359 * self.level / Settings.flower_food_source_maximum_level
        pygame.draw.arc(self.canvas, pygame.Color('white'), rect, 0, math.radians(angle), 5)
        # pygame.draw.circle(self.canvas, pygame.Color('white'), self.location, self.radius, 5)
        # self.canvas.blit(
        #     self.font.render(str(self.level), True, pygame.Color('black')),
        #     self.location
        # )
