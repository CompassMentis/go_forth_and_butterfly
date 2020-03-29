import random

from settings import Settings
import enums
from state_machine import State, Transition


def to_top_of_landing_zone(boid):
    boid.location.y = boid.game.level.landing_zone_top


def not_below_landing_zone(boid):
    boid.location.y = min(boid.game.level.landing_zone_top, boid.location.y)


def start_death_clock(boid):
    boid.death_clock = Settings.time_to_die


def on_start_of_sunrise(boid):
    try:
        boid.flock.level.on_start_of_sunrise()
    except AttributeError:
        pass


class States:
    def __init__(self):
        self.FLYING = State('FLYING')
        self.LANDING = State('LANDING')
        self.LANDED = State('LANDED')
        self.SLEEPING = State('SLEEPING')
        self.DYING = State('DYING')
        self.HUNGRY = State('HUNGRY')
        self.FEEDING = State('FEEDING')

        self.init_states()

    def init_states(self):
        # TOGGLE_LANDING and Flying and not in landing zone: -> Landing
        self.FLYING.add_transition(
            event=enums.Events.TOGGLE_LANDING,
            transition=Transition(
                target_state=self.LANDING,
                guards=[lambda boid: not boid.in_landing_zone]
            )
        )

        # When start landing, cannot be below landing line
        self.LANDING.enter_actions.append(not_below_landing_zone)

        # TOGGLE_LANDING and flying and in landing zone: -> LANDED
        self.FLYING.add_transition(
            event=enums.Events.TOGGLE_LANDING,
            transition=Transition(
                target_state=self.LANDED,
                guards=[lambda boid: boid.in_landing_zone]
            )
        )

        # TOGGLE_LANDING and Landing: -> Flying
        self.LANDING.add_transition(
            event=enums.Events.TOGGLE_LANDING,
            transition=Transition(target_state=self.FLYING)
        )

        # TOGGLE_LANDING and Landed: -> Flying
        self.LANDED.add_transition(
            event=enums.Events.TOGGLE_LANDING,
            transition=Transition(target_state=self.FLYING)
        )

        # SHOUT, Flying and leader is landing or landed
        self.FLYING.add_transition(
            event=enums.Events.SHOUT,
            transition=Transition(
                target_state=self.LANDING,
                guards=[
                    lambda boid: boid.game.leader.state in [self.LANDING, self.LANDED],
                ]
            )
        )

        # LANDING_ZONE_ENTERED and Landing: -> Landed
        self.LANDING.add_transition(
            event=enums.Events.LANDING_ZONE_ENTERED,
            transition=Transition(
                target_state=self.LANDED,
                guards=[
                    lambda boid: not boid.game.time_keeper.is_sunset
                ]
            )
        )

        # When just landed, go to top of landing zone
        self.LANDED.enter_actions.append(to_top_of_landing_zone)

        # Landed and sunset starts: -> Sleeping
        self.LANDED.add_transition(
            event=enums.Events.START_OF_SUNSET,
            transition=Transition(
                target_state=self.SLEEPING
            )
        )

        # Landing, sunset started, and landing zone entered: -> Sleeping
        self.LANDING.add_transition(
            event=enums.Events.LANDING_ZONE_ENTERED,
            transition=Transition(
                target_state=self.SLEEPING,
                guards=[
                    lambda boid: boid.game.time_keeper.is_sunset
                ]
            )
        )

        # Sleeping and sunrise starts: -> Flying
        self.SLEEPING.add_transition(
            event=enums.Events.START_OF_SUNRISE,
            transition=Transition(
                target_state=self.FLYING,
                action=on_start_of_sunrise
            )
        )

        # Landing or flying when night false -> Dying
        self.FLYING.add_transition(
            event=enums.Events.START_OF_NIGHTTIME,
            transition=Transition(
                target_state=self.DYING
            )
        )
        self.LANDING.add_transition(
            event=enums.Events.START_OF_NIGHTTIME,
            transition=Transition(
                target_state=self.DYING
            )
        )
        self.DYING.enter_actions.append(start_death_clock)

        transition = Transition(target_state=self.HUNGRY)
        for state in [
            self.FLYING, self.LANDED, self.LANDING
        ]:
            state.add_transition(
                event=enums.Events.GOT_HUNGRY,
                transition=transition
            )

        # TODO: Make sure this list is complete - probably better way of doing this
        transition = Transition(target_state=self.DYING)
        for state in [
            self.FLYING, self.LANDING, self.LANDING, self.SLEEPING, self.HUNGRY,
        ]:
            state.add_transition(
                event=enums.Events.STARVING,
                transition=transition
            )

        # Start feeding, from hungry
        self.HUNGRY.add_transition(
            event=enums.Events.START_FEEDING,
            transition=Transition(
                target_state=self.FEEDING
            )
        )

        # Done feeding, replete, back to flying
        self.FEEDING.add_transition(
            event=enums.Events.REPLETE,
            transition=Transition(
                target_state=self.FLYING
            )
        )


states = States()
