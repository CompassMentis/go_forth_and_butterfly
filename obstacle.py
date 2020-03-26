import pygame


class Obstacle:
    def __init__(self, location, radius, weight=None):
        self.location = location
        self.radius = radius
        self.weight = weight

    def draw(self, canvas):
        pygame.draw.circle(canvas, pygame.Color('red'), self.location, self.radius, 2)
