import enum


# class BoidStatus(enum.Enum):
#     FLYING = 1
#     LANDING = 2
#     LANDED = 3
#     FEEDING = 4
#     LANDING_TO_MATE = 5
#     WAITING_TO_MATE = 6


class BoidSex(enum.Enum):
    MALE = 1
    FEMALE = 2


class Events(enum.Enum):
    THROUGH_ENTRANCE_GATE = 1
    THROUGH_EXIT_GATE = 2
    SHOUT = 3
    TOGGLE_LANDING = 4
    LANDING_ZONE_ENTERED = 5
    START_OF_SUNSET = 6
    START_OF_DAYTIME = 7
    START_OF_NIGHTTIME = 8
    START_OF_SUNRISE = 9
    GOT_HUNGRY = 10
    STARVING = 11
    START_FEEDING = 12
    REPLETE = 13
    PLANT_FLOWER = 14


class GameState(enum.Enum):
    READ_INTRO = 1
    PLAY = 2
    PAUSE = 3
    HELP = 4
