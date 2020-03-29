import random
import os
import datetime
import textwrap

import pygame

import levels
from flower import Flower
import utilities
from event_handler import EventHandler
from button import Button
import enums
from settings import Settings

# TODO: Remove this?
random.seed(10)


class Game:
    def __init__(self, canvas, starting_level):
        self.canvas = canvas
        self.clock = pygame.time.Clock()
        self.images = self.load_images()
        self.help_image = pygame.image.load(os.path.join('images', 'help.png'))
        self.event_handler = EventHandler(self)
        self.boids_need_food = False
        self.state = enums.GameState.READ_INTRO
        self.font = pygame.font.Font(
            os.path.join('fonts', 'Acme-Regular.ttf'),
            Settings.font_size
        )

        lines = """Your butterfly will be affected by the others around it and vice versa
        But you do have some control over it. And, as the leader, you have the most influence
        
        Left and right arrow keys to steer your butterfly
        Up and down arrows keys to go faster and slower
        Space bar to reset speed to normal
        
        You can move to the next level once you have fullfilled your mission
        You, and only you, can also go back to the previous level
        
        Don't worry if you fly off the screen - wait and you'll get back
        """

        self.help_lines = [line.strip() for line in lines.split('\n')]

        self.time_keeper = None
        self.recent_buttons = {}

        self.food_sources = []

        self.active_forces = {
            'Separation', 'Alignment', 'Cohesion', 'Boundaries', 'Attractor',
        }
        self.levels = [
            levels.Level01(self),
            levels.Level02(self),
            levels.Level03(self),
            levels.Level04(self),
            levels.Level05(self),
        ]

        # Start at level starting_level - 1
        # Zero index the level first
        starting_level -= 1
        self.level = self.levels[starting_level]

        if starting_level > 0:
            # Move the flock to the starting level
            for boid in self.levels[0].flock.boids:
                self.level.flock.boids.append(boid)
                boid.flock = self.level.flock
            self.levels[0].flock.boids = []
            leader = self.levels[0].flock.leader
            self.levels[0].flock.leader = None
            self.level.flock.leader = leader

        for level in self.levels[:starting_level + 1]:
            level.leader_enters()

        self.buttons = {
            'ok': Button(self, 'ok', pygame.Vector2(1723, 915)),
            'help': Button(self, 'help', pygame.Vector2(1723, 915)),
            'pause': Button(self, 'pause', pygame.Vector2(1655, 915)),
            'play': Button(self, 'play', pygame.Vector2(1655, 915)),
        }

        for name in 'help', 'pause', 'play':
            self.buttons[name].visible = False

    def next_level(self, level):
        current_level_index = self.levels.index(level)
        if current_level_index > len(self.levels):
            return None

        return self.levels[current_level_index + 1]

    def previous_level(self, level):
        current_level_index = self.levels.index(level)

        if current_level_index == 0:
            return None

        return self.levels[current_level_index - 1]

    @property
    def leader(self):
        return self.level.flock.leader

    @property
    def is_mating_season(self):
        return self.time_keeper.is_mating_season

    def handle_event(self, event, boid=None):
        self.event_handler.handle_event(event, boid)

    def load_images(self):
        result = {}
        for size in 'small', 'large':
            for sex in 'male', 'female':
                source_image = pygame.image.load(
                    os.path.join('images', 'butterflies', f'{size}_{sex}.png')
                )

                for angle in range(0, 360, 15):
                    result[(size, sex, angle)] = utilities.rotate_in_place(source_image, angle + 90)

        # for butterfly_type in os.listdir(source_folder):
        # for butterfly_type in ['large_red']:
        #     if not os.path.isdir(source_folder + butterfly_type):
        #         continue
        #
        #     for angle in range(0, 360, 15):
        #         for step in range(16):
        #             result[(butterfly_type, angle, step)] = pygame.image.load(
        #                 f'{source_folder}{butterfly_type}/butterfly_{angle:03}_step_{step:02}.png'
        #             )
        return result

    def write_text(self, lines, location):
        for i, line in enumerate(lines):
            y = location.y + i * Settings.line_spacing
            self.canvas.blit(
                self.font.render(line, True, pygame.Color('white')),
                (location.x, y)
            )

    def show_intro(self):
        lines = [line.strip() for line in self.level.introduction_text.split('\n') if line.strip()]
        self.write_text(lines, Settings.console_text_location)

    def show_help(self):
        self.canvas.blit(self.help_image, (0, 0))
        self.write_text(self.help_lines, Settings.help_text_location)

    def show_play_console(self):
        lines = [self.level.aim_text]
        boid_count = [(i, len(level.flock.boids)) for (i, level) in enumerate(self.levels, 1)]
        status = ', '.join(f'{i}: {count}' for (i, count) in boid_count)
        lines.append(f'Butterflies by level: {status}')
        self.write_text(lines, Settings.console_text_location)

    def show_console(self):
        for button in self.buttons.values():
            button.visible = False
        if self.state == enums.GameState.READ_INTRO:
            self.buttons['ok'].visible = True
            self.show_intro()
        elif self.state == enums.GameState.PLAY:
            self.buttons['pause'].visible = True
            self.buttons['help'].visible = True
            self.show_play_console()
        elif self.state == enums.GameState.PAUSE:
            self.buttons['play'].visible = True
        elif self.state == enums.GameState.HELP:
            self.buttons['ok'].visible = True
            self.show_help()

        [button.draw() for button in self.buttons.values()]

    def draw(self):
        # self.canvas.blit(self.background, (-self.background_offset, 0))
        # [flower.draw() for flower in self.flowers]
        # [flock.draw() for flock in self.flocks]
        # [food_source.draw() for food_source in self.food_sources]
        # if self.is_mating_season:
        #     pygame.draw.rect(self.canvas, pygame.Color('orange'), (20, 20, 50, 50), 5)
        self.level.draw()

        if self.time_keeper:
            self.time_keeper.draw()
        self.show_console()
        pygame.display.flip()

    def unbounce_button(self, button):
        if button in [
            pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN
        ]:
            return True
        last_time = self.recent_buttons.get(button)
        now = datetime.datetime.now()
        self.recent_buttons[button] = now

        return last_time is None or (now - last_time) > datetime.timedelta(milliseconds=200)

    def plant_seed(self, location):
        self.flowers.append(Flower(self, location))

    def set_current_level(self):
        for level in self.levels:
            if level.contains_leader:
                self.level = level
                return

    # TODO: Tidy this up, in wrong place
    def mouse_pressed(self, name):
        if name in ['ok', 'play']:
            self.state = enums.GameState.PLAY
        elif name == 'pause':
            # self.state = enums.GameState.PAUSE
            self.state = enums.GameState.READ_INTRO
        elif name == 'help':
            self.state = enums.GameState.HELP

    def update(self, duration):
        # [flower.update(duration) for flower in self.flowers]
        # [flock.update(duration) for flock in self.flocks]
        # [food_source.update(duration) for food_source in self.food_sources]

        # leader_boids = [
        #     boid
        #     for flock in self.flocks
        #     for boid in flock.boids
        #     if boid.is_leader
        # ]
        done = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if self.unbounce_button(event.key):
                    self.event_handler.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                [button.handle_mouse_click(mouse_position) for button in self.buttons.values()]
            elif event.type == pygame.QUIT:
                done = True

        if self.state == enums.GameState.PLAY:
            # [level.update(duration) for level in self.levels]
            self.level.update(duration)
            self.set_current_level()

        return done

    def run(self):
        self.clock.tick(30)
        done = False
        while not done:
            duration = self.clock.tick(30) / 1000
            done = self.update(duration)
            self.draw()
