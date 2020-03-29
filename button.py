import os

import pygame


class Button:
    def __init__(self, game, name, location):
        self.game = game
        self.canvas = game.canvas
        self.name = name
        self.location = location

        self.active = True
        self.visible = True

        self.active_image = pygame.image.load(os.path.join('images', 'buttons', f'{self.name}.png'))
        self.inactive_image = pygame.image.load(os.path.join('images', 'buttons', f'{self.name}_inactive.png'))

    def draw(self):
        if not self.visible:
            return

        image = self.active_image if self.active else self.inactive_image
        self.canvas.blit(image, self.location)

    def handle_mouse_click(self, mouse_location):
        if not self.visible:
            return

        if mouse_location[0] < self.location.x\
                or mouse_location[0] > self.location.x + 60 \
                or mouse_location[1] < self.location.y \
                or mouse_location[1] > self.location.y + 60:
            return

        self.game.mouse_pressed(self.name)
