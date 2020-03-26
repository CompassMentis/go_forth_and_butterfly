import pygame

from settings import Settings
import boid


class Player(boid.Boid):
    def __init__(self, flock):
        velocity = pygame.Vector2(0, 0)
        velocity.from_polar((1, 0))
        super().__init__(flock, pygame.Vector2(1000, 500), velocity)
        self.weight = 10

        # self.game = game
        # self.canvas = game.canvas
        # self.location = pygame.Vector2(500, 500)
        # self.speed = 5
        # self.direction = 0

    def draw(self):
        pygame.draw.circle(self.canvas, pygame.Color('red'), self.location, 50)

    def update(self):
        # # self.location += self.velocity
        # pass

        # TODO: DRY?
        self.location = pygame.mouse.get_pos()

    @property
    def angle(self):
        return self.velocity.as_polar()[1]

    @angle.setter
    def angle(self, new_angle):
        self.velocity.from_polar((self.speed, new_angle))

    @property
    def speed(self):
        return self.velocity.as_polar()[0]

    @speed.setter
    def speed(self, new_speed):
        self.velocity.from_polar((new_speed, self.angle))

    def turn_left(self):
        self.angle = (self.angle - Settings.player_turn_angle) % 360

    def turn_right(self):
        self.angle = (self.angle + Settings.player_turn_angle) % 360

    def speed_up(self):
        self.speed = min(self.speed + Settings.player_speed_increase, Settings.player_maximum_speed)

    def slowdown(self):
        self.speed = max(self.speed - Settings.player_speed_decrease, 0)

    def move(self, key):
        if key == pygame.K_LEFT:
            self.location += pygame.Vector2(-5, 0)
        elif key == pygame.K_RIGHT:
            self.location += pygame.Vector2(5, 0)
        elif key == pygame.K_UP:
            self.location += pygame.Vector2(0, -5)
        elif key == pygame.K_DOWN:
            self.location += pygame.Vector2(0, 5)
