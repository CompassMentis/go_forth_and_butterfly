import random

import pygame


def angle_lte(angle, maximum_angle):
    angle = angle % 360
    angle = min(angle, 360 - angle)
    return angle <= maximum_angle


def steer_towards(source_velocity, target_velocity, maximum_acceleration, maximum_turn_angle):
    source_speed, source_direction = source_velocity.as_polar()
    target_speed, target_direction = target_velocity.as_polar()

    if target_speed > source_speed:
        target_speed = min(source_speed + maximum_acceleration, target_speed)
    else:
        target_speed = max(source_speed - maximum_acceleration, target_speed)

    delta_direction = (target_direction - source_direction) % 360
    if delta_direction < 180:
        delta_direction = min(delta_direction, maximum_turn_angle)

    else:
        delta_direction = max(delta_direction - 360, -maximum_turn_angle)

    target_direction = (source_direction + delta_direction) % 360

    target_velocity = pygame.Vector2(0, 0)
    target_velocity.from_polar((target_speed, target_direction))

    return target_velocity


def point_centre(points):
    points = list(points)
    total = pygame.Vector2(0, 0)
    for point in points:
        total += point
    return total / len(points)


def average_velocity(velocities):
    return point_centre(velocities)


def distance_between_points(point1, point2):
    return (point2 - point1).length()


def normalise_force_to_weight(force, weight):
    return force.normalize() * weight


def rotate_in_place(image, angle):
    target_image = pygame.Surface(image.get_rect().size, pygame.SRCALPHA)
    rotated_image = pygame.transform.rotate(image, -angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=(0, 0)).center)
    target_image.blit(rotated_image, new_rect.topleft)
    return target_image


# def random_position_away_from(location, distance):
#     delta_position = pygame.Vector2(0, 0)
#     delta_position.from_polar((distance, random.randint(0, 359)))
#     return location + delta_position