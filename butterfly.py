import math
import random

import boid


class Butterfly(boid.Boid):
    def __init__(self, flock, location, velocity):
        super().__init__(flock, location, velocity)
        self.animation_step = random.randint(0, 15)
        self.butterfly_type = 'large_red'

    def draw(self):
        _, angle = self.velocity.as_polar()
        angle = angle % 360
        angle = 15 * math.floor(angle / 15)

        # TODO: Tidy this up?
        angle = 0 if angle == 360 else angle
        # image = self.game.images[f'butterfly_{angle:03}']
        image = self.flock.images[(self.butterfly_type, angle, self.animation_step)]
        rect = image.get_rect(center=self.location)
        rect.move_ip((-self.flock.background_offset, 0))

        self.canvas.blit(image, rect)
        # pygame.draw.circle(self.canvas, pygame.Color('blue'), self.location, 22)

    def update(self):
        super().update()
        if random.randint(0, 2):
            self.animation_step = (self.animation_step + 1) % 16
