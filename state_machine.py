import collections
import logging
logger = logging.getLogger(__name__)


class NoSuitableTransition(Exception):
    pass


class FailedGuard(Exception):
    pass


class StateMachine:
    """
    Finite State Machine which tracks state for a flock of boids and handles transitions triggered by events
    """
    def __init__(self, game):
        self.states = []
        self.game = game

    def handle_event(self, event, boid=None):
        boids = [boid] if boid is not None else self.game.level.flock.boids
        for boid in boids:
            try:
                old_state = boid.state
                boid.state = boid.state.handle_event(event, boid)
                logger.debug(f'{boid} transitioned from {old_state} to {boid.state}')
            except NoSuitableTransition:
                logger.debug(f'{boid} no transition found for {event} - ignored')


class State:
    def __init__(self, name):
        self.name = name
        self.transitions = collections.defaultdict(list)
        self.game = None
        self.exit_actions = []
        self.enter_actions = []

    def add_transition(self, event, transition):
        self.transitions[event].append(transition)

    def try_transition(self, transition, boid):
        for guard in transition.guards:
            if not guard(boid):
                raise FailedGuard

        [exit_action(boid) for exit_action in self.exit_actions]
        if transition.action:
            transition.action(boid)
        target_state = transition.target_state
        [enter_action(boid) for enter_action in target_state.enter_actions]
        return target_state

    def handle_event(self, event, boid):
        transitions_for_event = self.transitions.get(event, [])

        for transition in transitions_for_event:
            try:
                return self.try_transition(transition, boid)
            except FailedGuard:
                logger.debug(f'{boid} failed guard for {event} - ignored')

        raise NoSuitableTransition

    def __str__(self):
        return self.name


class Transition:
    def __init__(self, target_state, guards=None, action=None):
        self.guards = guards if guards is not None else []
        self.target_state = target_state
        self.action = action
