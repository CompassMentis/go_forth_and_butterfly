import logging
logger = logging.getLogger(__name__)

import pygame

import state_machine
from settings import Settings
from enums import Events, GameState
import utilities
from flower import Flower


# class DelayedEvent:
#     def __init__(self, event, event_time):
#         self.event = event
#         self.event_time = event_time


class EventHandler:
    def __init__(self, game):
        self.game = game
        self.state_machine = state_machine.StateMachine(game)

        # self.event_queue = []

        # TODO: Very easy to forget to add an event - any better solutions?
        self.active_events = {
            Events.THROUGH_EXIT_GATE,
            Events.THROUGH_ENTRANCE_GATE,
            Events.LANDING_ZONE_ENTERED,
            Events.START_OF_SUNRISE,
            Events.START_OF_SUNSET,
            Events.START_OF_DAYTIME,
            Events.START_OF_NIGHTTIME,
            Events.GOT_HUNGRY,
            Events.STARVING,
            Events.START_FEEDING,
            Events.REPLETE,
        }

        # In debug mode all events are active from the start
        if logger.getEffectiveLevel() <= logging.DEBUG:
            self.active_events.update([
                Events.SHOUT
            ])

    # def add_delayed_event(self, delay, event):
    #     self.event_queue.append(Event(event))

    def activate(self, events):
        self.active_events.update(events)

    def handle_shout(self, _):
        flock = self.game.level.flock
        leader = flock.leader
        for boid in flock.boids:
            if boid.is_leader:
                continue

            vector_to_leader = leader.location - boid.location
            if vector_to_leader.length() > Settings.shouting_distance:
                continue

            boid.apply_force(vector_to_leader.normalize() * Settings.shouting_force)

    def handle_plant_flower(self, leader):
        if not(self.game.level.minimum_plant_level < leader.location.y < self.game.level.maximum_plant_level):
            return

        leader.flock.level.flowers.append(
            Flower(self.game, leader.location, age=-Settings.flower_seed_period)
        )

    def handle_through_gate(self, boid, target_level, target_position):
        if boid.is_leader:
            boid.flock.leader = None
            target_level.flock.leader = boid
            target_level.leader_enters()

        boid.flock.boids.remove(boid)
        target_level.flock.boids.append(boid)
        boid.flock = target_level.flock

        boid.location = target_position + boid.velocity.normalize() * Settings.gate_radius * 2.5

    def handle_through_exit_gate(self, boid):
        if not boid.flock.level.exit_gate_open:
            return

        target_level = self.game.next_level(boid.flock.level)
        target_position = target_level.entrance_gate_position
        self.handle_through_gate(boid, target_level, target_position)

    def handle_through_entrance_gate(self, boid):
        target_level = self.game.previous_level(boid.flock.level)
        target_position = target_level.exit_gate_position
        self.handle_through_gate(boid, target_level, target_position)

    def handle_key(self, key):
        leader = self.game.level.flock.leader

        if key == pygame.K_LEFT:
            leader.turn_left()

        elif key == pygame.K_RIGHT:
            leader.turn_right()

        elif key == pygame.K_UP:
            leader.speed_up()

        elif key == pygame.K_DOWN:
            leader.slow_down()

        elif key == pygame.K_SPACE:
            leader.reset_speed()

        elif key == pygame.K_s:
            self.handle_event(Events.SHOUT)
            self.state_machine.handle_event(Events.SHOUT)

        elif key == pygame.K_l:
            self.handle_event(Events.TOGGLE_LANDING, self.game.level.flock.leader)

        elif key == pygame.K_p:
            self.handle_event(Events.PLANT_FLOWER, self.game.level.flock.leader)

        # TODO: Tidy this up - should go in the event handler
        elif key == pygame.K_h:
            self.game.state = GameState.HELP

        elif key == pygame.K_RETURN and self.game.state in [GameState.HELP, GameState.READ_INTRO]:
            self.game.state = GameState.PLAY

    def handle_event(self, event, boid=None):
        if event not in self.active_events:
            logger.debug(f'Ignored event {event}')
            return

        logger.debug(f'Handling event {event}')

        # Todo: just pass through all?
        if event in [
            Events.TOGGLE_LANDING,
            Events.LANDING_ZONE_ENTERED,
            Events.START_OF_SUNRISE,
            Events.START_OF_SUNSET,
            Events.START_OF_DAYTIME,
            Events.START_OF_NIGHTTIME,
            Events.GOT_HUNGRY,
            Events.STARVING,
            Events.START_FEEDING,
            Events.REPLETE,
        ]:
            self.state_machine.handle_event(event, boid)
            return

        action = {
            Events.THROUGH_ENTRANCE_GATE: self.handle_through_entrance_gate,
            Events.THROUGH_EXIT_GATE: self.handle_through_exit_gate,
            Events.SHOUT: self.handle_shout,
            Events.PLANT_FLOWER: self.handle_plant_flower,
        }[event]
        action(boid)



        # if self.potential_mate and (self.potential_mate.recently_mated or self.potential_mate.is_hungry):
        #     self.potential_mate = None
        #
        # # TODO: Separate functions for during_mating_season and start_of_mating_season?
        # if self.game.is_mating_season and self.sex == BoidSex.FEMALE and not self.is_hungry and not self.recently_mated:
        #     if self.potential_mate is None:
        #         potential_mates = [
        #             boid
        #             for boid in self.flock.boids
        #             if boid.sex == BoidSex.MALE
        #                and boid.status == BoidStatus.WAITING_TO_MATE
        #                and not boid.recently_mated
        #         ]
        #         if potential_mates:
        #             self.potential_mate = random.choice(potential_mates)
        #             self.status = BoidStatus.LANDING_TO_MATE
        #
        # if not self.game.is_mating_season or self.is_hungry:
        #     self.potential_mate = None
        #
        # if self.potential_mate:
        #     self.apply_force(
        #         utilities.normalise_force_to_weight(
        #             self.potential_mate.location - self.location, Settings.mating_attraction_force_weight
        #         ), essential=True
        #     )
        #
        # # During mating season, start landing or, if hungry, start flying
        # if self.game.is_mating_season and self.sex == BoidSex.MALE and not self.is_hungry:
        #     if self.status == BoidStatus.FLYING:
        #         self.status = BoidStatus.LANDING_TO_MATE
        #
        # if self.is_hungry and self.status in [BoidStatus.LANDING_TO_MATE, BoidStatus.WAITING_TO_MATE]:
        #     self.status = BoidStatus.FLYING
        #     self.apply_force(pygame.Vector2(0, -10), essential=True)
        #
        # if not self.game.is_mating_season:
        #     if self.status == BoidStatus.WAITING_TO_MATE:
        #         self.status = BoidStatus.FLYING
        #         self.apply_force(pygame.Vector2(0, -10), essential=True)
        #     elif self.status == BoidStatus.LANDING_TO_MATE:
        #         self.status = BoidStatus.FLYING
        #
        # if self.status == BoidStatus.FEEDING:
        #
        #     # Any food left? If so, eat
        #     if self.feeding_from.level > 0.1:
        #         food = min(self.feeding_from.level, duration * Settings.feeding_speed, Settings.boid_maximum_food_level - self.food)
        #         self.feeding_from.level -= food
        #         self.food += food
        #         return
        #
        #     # No food left, start flying
        #     self.exhausted_food_sources.append(self.feeding_from)
        #     self.feeding_from = None
        #     self.status = BoidStatus.FLYING
        #     return
        #
        # if self.is_hungry:
        #     # Hungry. Have we reached a food source?
        #     food_source = self.landed_on_food_source()
        #     if food_source:
        #         self.status = BoidStatus.FEEDING
        #         self.feeding_from = food_source
        #
        # if self.status in [BoidStatus.FLYING, BoidStatus.LANDING, BoidStatus.LANDING_TO_MATE]:
        #     self.location += (self.velocity * duration)
        #
        # if self.status in [BoidStatus.LANDING, BoidStatus.LANDING_TO_MATE] \
        #         and self.location.y >= (Settings.screen_size.y - Settings.landing_range):
        #     self.location.y = Settings.screen_size.y - Settings.landing_range
        #     if self.status == BoidStatus.LANDING_TO_MATE:
        #         if self.potential_mate:
        #             self.potential_mate.last_mated = self.potential_mate.age
        #             self.last_mated = self.age
        #             self.flock.make_babies(self.location)
        #             self.status = BoidStatus.FLYING
        #             self.potential_mate.status = BoidStatus.FLYING
        #         self.status = BoidStatus.WAITING_TO_MATE
        #     else:
        #         self.status = BoidStatus.LANDED
        #         print('Landed')
        #         self.waiting_period = Settings.landed_period
        #
        # elif self.status == BoidStatus.LANDED:
        #     self.waiting_period -= duration
        #     if self.waiting_period <= 0:
        #         self.status = BoidStatus.FLYING
