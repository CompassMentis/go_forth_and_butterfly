class StateMachine:
    """
    Finite State Machine which tracks state for a flock of boids and handles transitions triggered by events
    """
    def __init__(self, flock):
        self.states = []
        self.flock = flock

    def handle_event(self, event, boid=None):
        boids = [boid] if boid is not None else self.flock.boids
        for boid in boids:
            boid.state = boid.state.handle_event(event, boid)


class State:
    def __init__(self, flock):
        self.transitions = {}
        self.game = flock.game
        self.exit_actions = []
        self.enter_actions = []

    def handle_event(self, event, boid):
        transition = self.transitions.get(event)
        if transition is None:
            return

        if not transition.guard(boid):
            return

        [exit_action(boid) for exit_action in self.exit_actions]
        transition.action(boid)
        target_state = transition.target_state
        [enter_action(boid) for enter_action in target_state.enter_actions]
        return target_state


class Transition:
    def __init__(self, target_state, guards, action):
        self.guards = guards
        self.target_state = target_state
        self.action = action


class Event:
    pass

"""
Each boid has its own state, with rules that say:
- when an event happens, check which state each boid is in
"""
