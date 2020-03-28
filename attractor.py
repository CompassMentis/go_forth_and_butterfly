import pygame


class Attractor:
    def __init__(self, location, weight, distance):
        self.location = location
        self.weight = weight
        self.distance = distance

    def draw(self, canvas):
        pygame.draw.circle(canvas, pygame.Color('red'), self.location, self.distance, 1)
