import logging
logger = logging.getLogger(__name__)
import argparse

import pygame

import game
from settings import Settings

# pygame.init()
pygame.font.init()
pygame.display.init()
pygame.key.set_repeat(10)

canvas = pygame.display.set_mode(Settings.screen_size_as_integer)

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true')
parser.add_argument('--level', type=int, default=1)
args = parser.parse_args()
if args.debug:
    logging.basicConfig(level=logging.DEBUG)

game = game.Game(canvas, starting_level=args.level)
game.run()
