import pygame

import utilities


def test_angle_lte():
    mut = utilities.angle_lte

    assert mut(5, 10)
    assert mut(355, 10)
    assert mut(170, 175)
    assert mut(190, 175)
    assert not mut(15, 10)
    assert not mut(170, 160)


def test_steer_towards():
    mut = utilities.steer_towards

    source_velocity = pygame.Vector2(0, 0)
    target_velocity = pygame.Vector2(0, 0)

    # Exactly same speed and angle
    source_velocity.from_polar((10, 0))
    target_velocity.from_polar((10, 0))
    assert mut(source_velocity, source_velocity, 1, 5).as_polar()[0] == 10

    # 1 slower - within limit
    source_velocity.from_polar((10, 0))
    target_velocity.from_polar((9, 0))
    assert mut(source_velocity, target_velocity, 1, 5).as_polar()[0] == 9

    # 2 slower - outside limit
    source_velocity.from_polar((10, 0))
    target_velocity.from_polar((8, 0))
    assert mut(source_velocity, target_velocity, 1, 5).as_polar()[0] == 9

    # 4 degrees - within limit
    source_velocity.from_polar((10, 0))
    target_velocity.from_polar((10, 4))
    assert mut(source_velocity, target_velocity, 1, 5).as_polar()[1] == 4

    # 6 degrees - outside limit
    source_velocity.from_polar((10, 0))
    target_velocity.from_polar((10, 6))
    assert mut(source_velocity, target_velocity, 1, 5).as_polar()[1] == 5

    # 4 degrees - around the circle
    source_velocity.from_polar((10, 359))
    target_velocity.from_polar((10, 3))
    assert mut(source_velocity, target_velocity, 1, 5).as_polar()[1] == 3

    # -6 degrees - around the circle
    source_velocity.from_polar((10, 3))
    target_velocity.from_polar((10, 357))
    assert abs(mut(source_velocity, target_velocity, 1, 5).as_polar()[1] + 2) < 0.00001
