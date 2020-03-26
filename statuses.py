import enum


class BoidStatus(enum.Enum):
    FLYING = 1
    LANDING = 2
    LANDED = 3
    FEEDING = 4
    LANDING_TO_MATE = 5
    WAITING_TO_MATE = 6


class BoidSex(enum.Enum):
    MALE = 1
    FEMALE = 2
