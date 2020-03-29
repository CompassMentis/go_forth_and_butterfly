import os
import random
import collections
import datetime

import pygame

from settings import Settings

# TODO: Remove this
from enums import BoidSex, Events
import utilities
from states import states

random.seed(10)


class AbstractBoid:
    pass


class Boid:
    next_id = 0

    def __init__(self, flock, location, velocity, sex=None, age=0):
        self.id = Boid.next_id
        self.death_clock = None
        self.alive = True
        Boid.next_id += 1
        self.flock = flock
        self.game = flock.game
        self.canvas = flock.canvas
        self.location = location
        self.velocity = velocity
        self.sex = random.choice(list(BoidSex)) if sex is None else sex
        self.mass = 1
        # self.history = collections.deque(maxlen=50)
        self.state = states.FLYING
        self.waiting_period = None
        self.food = Settings.boid_starting_food_level * random.randint(90, 110) / 100
        self.age = age
        self.potential_mate = None
        self.last_mated = 0

        # Keep track of which flowers have been visited and exhausted
        self.exhausted_food_sources = collections.deque(maxlen=4)
        self.feeding_from = None
        self.leader_speed_multiplier = 1
        self.in_landing_zone = False
        self.status_icons = {
            state: pygame.image.load(
                os.path.join('images', 'statuses', name + '.png')
            )
            for state, name in [
                (states.LANDED, 'landed'),
                (states.LANDING, 'landing'),
                (states.SLEEPING, 'sleeping'),
                (states.DYING, 'dying'),
                (states.HUNGRY, 'hungry'),
                (states.FEEDING, 'feeding'),
            ]
        }

    @property
    def is_leader(self):
        return self.flock.leader == self

    @property
    def recently_mated(self):
        return (self.age - self.last_mated) < Settings.minimum_time_between_matings

    @property
    def is_adult(self):
        return self.age >= Settings.boid_adult_age

    @property
    def is_hungry(self):
        return self.food <= Settings.boid_hungry_level

    @property
    def image(self):
        size = 'large' if self.is_leader else 'small'
        sex = 'female' if self.sex == BoidSex.FEMALE else 'male'
        _, angle = self.velocity.as_polar()
        angle = (15 * int(angle // 15)) % 360
        return self.game.images[(size, sex, angle)]

    def draw(self):
        image = self.image
        rect = image.get_rect()
        rect.center = self.location
        self.canvas.blit(image, rect)
        icon = self.status_icons.get(self.state)
        if icon:
            icon_offset = Settings.leader_status_icon_offset if self.is_leader else Settings.boid_status_icon_offset
            self.canvas.blit(icon, self.location + icon_offset)

    def apply_force(self, force, essential=False):
        acceleration = force / self.mass
        velocity = self.velocity + acceleration
        speed, direction = velocity.as_polar()

        # Whilst LANDING, any upward force is ignored (anything above 180 degrees)
        if self.state == states.LANDING and force and not essential:
            direction = direction % 360
            if direction > 180:
                return

        maximum_speed = Settings.boid_maximum_speed
        if self.is_leader:
            maximum_speed *= self.leader_speed_multiplier
        speed = min(speed, maximum_speed)
        self.velocity.from_polar((speed, direction))
        # if self.is_leader:
        #     print('New speed: ', speed)

    def turn_left(self):
        # TODO: DRY?
        speed, angle = self.velocity.as_polar()
        force = pygame.Vector2(0, 0)
        force.from_polar((Settings.steering_force, angle - 90))
        self.apply_force(force, essential=True)

    def turn_right(self):
        speed, angle = self.velocity.as_polar()
        force = pygame.Vector2(0, 0)
        force.from_polar((Settings.steering_force, angle + 90))
        self.apply_force(force, essential=True)

    def speed_up(self):
        speed_multiplier = self.leader_speed_multiplier * 1.05
        self.leader_speed_multiplier = min(speed_multiplier, Settings.player_maximum_speed_multiplier)

        speed, angle = self.velocity.as_polar()
        force = pygame.Vector2(0, 0)
        force.from_polar((Settings.steering_force, angle))
        self.apply_force(force)

    def slow_down(self):
        speed_multiplier = self.leader_speed_multiplier / 1.05
        self.leader_speed_multiplier = max(speed_multiplier, Settings.player_minimum_speed_multiplier)

        # speed, angle = self.velocity.as_polar()
        # force = pygame.Vector2(0, 0)
        # force.from_polar((Settings.steering_force * 10, angle))
        # self.apply_force(force)

    def reset_speed(self):
        self.leader_speed_multiplier = 1

    def toggle_landing(self):
        if self.state in [states.LANDED, states.LANDING]:
            self.state = states.FLYING
            print('Flying')
        else:
            self.state = states.LANDING
            print('Landing')

    def landed_on_food_source(self):
        for food_source in self.flock.game.food_sources:
            if utilities.distance_between_points(self.location, food_source.location) <= food_source.radius:
                return food_source
        return None

    # def move_to_next_level(self):

        # self.location = utilities.random_position_away_from(
        #     next_level.entrance_gate_position,
        #     Settings.gate_radius * 1.5
        # )

    def check_gate(self, gate_position, direction):
        if gate_position is None:
            return

        if utilities.distance_between_points(self.location, gate_position) > Settings.gate_radius:
            return

        assert direction in ['previous', 'next']
        if direction == 'next':
            self.game.handle_event(Events.THROUGH_EXIT_GATE, self)
            # target_level = self.game.next_level(self.flock.level)
            # target_position = target_level.entrance_gate_position
        else:
            self.game.handle_event(Events.THROUGH_ENTRANCE_GATE, self)
        #     self
        #     target_level = self.game.previous_level(self.flock.level)
        #     target_position = target_level.exit_gate_position
        #
        # if self.is_leader:
        #     self.flock.leader = None
        #     target_level.flock.leader = self
        #
        # self.flock.boids.remove(self)
        # target_level.flock.boids.append(self)
        # self.flock = target_level.flock
        #
        # self.location = target_position + self.velocity.normalize() * Settings.gate_radius * 2.5

    def check_exit_gate(self):
        # The leader can only exit the level once it is complete
        if self.is_leader and not self.flock.level.level_complete:
            return

        self.check_gate(self.flock.level.exit_gate_position, 'next')

    def check_entrance_gate(self):
        if self.is_leader:
            self.check_gate(self.flock.level.entrance_gate_position, 'previous')

    def check_landing_zone(self):
        if self.location.y > self.flock.level.landing_zone_top:
            if not self.in_landing_zone:
                self.game.handle_event(Events.LANDING_ZONE_ENTERED, self)
                self.in_landing_zone = True
        else:
            self.in_landing_zone = False

    def check_food_sources(self):
        if self.state == states.HUNGRY:
            for food_source in self.flock.level.game.food_sources:
                if utilities.distance_between_points(self.location, food_source.location) < food_source.radius:
                    self.feeding_from = food_source
                    self.game.handle_event(Events.START_FEEDING, self)

    def check_hungry(self, duration):
        was_hungry = self.is_hungry
        if self.game.boids_need_food:
            self.food -= duration
        if self.is_hungry and not was_hungry:
            self.game.handle_event(Events.GOT_HUNGRY, self)
        if self.food < 0 and self.state is not states.DYING:
            self.game.handle_event(Events.STARVING, self)

    def feed(self, duration):
        if self.state is not states.FEEDING:
            return

        self.food += duration * Settings.feeding_speed

        if self.food >= Settings.boid_maximum_food_level:
            self.game.handle_event(Events.REPLETE)

        #     if self.feeding_from.level > 0.1:
        #         food = min(self.feeding_from.level, duration * Settings.feeding_speed, Settings.boid_maximum_food_level - self.food)
        #         self.feeding_from.level -= food
        #         self.food += food
        #         return

    def update(self, duration):
        # self.history.append(list(self.location))

        self.check_hungry(duration)
        self.check_food_sources()
        self.feed(duration)
        self.age += duration
        if self.state not in [states.LANDED, states.SLEEPING, states.FEEDING]:
            self.location += self.velocity * duration
        self.check_exit_gate()
        self.check_entrance_gate()
        self.check_landing_zone()
        if self.state == states.DYING:
            self.death_clock -= duration
            if self.death_clock <= 0:
                self.alive = False

    def __str__(self):
        return f'<leader ({self.state})>' if self.is_leader else f'<boid {self.id} ({self.state})>'
