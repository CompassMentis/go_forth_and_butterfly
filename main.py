import pygame

import game
from settings import Settings

pygame.init()

pygame.key.set_repeat(10)
canvas = pygame.display.set_mode(Settings.screen_size_as_integer)
game = game.Game(canvas)
game.run()
