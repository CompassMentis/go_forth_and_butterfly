import pygame


class Settings:
    screen_size = pygame.math.Vector2(1800, 1000)
    screen_size_as_integer = int(screen_size.x), int(screen_size.y)
    number_of_boids = 10
    border = 30
    background_colour = pygame.Color('black')
    neighbour_distance = 200
    close_neighbour_distance = 100
    maximum_starting_speed = 10
    minimum_starting_speed = 5
    border_avoidance_speed = 5
    maximum_acceleration = 1
    maximum_turn_angle = 5
    viewing_angle = 45

    player_turn_angle = 15
    player_speed_increase = 1
    player_speed_decrease = 0.5
    player_maximum_speed = 20

    scroll_border_size = 100
    scroll_speed = 10

    boid_maximum_speed = 150

    steering_force = 4
    landing_range = 25  # Once within 5 of the ground level, stop moving
    landed_period = 3  # Once landed, wait 3 seconds before moving off again

    gravity_velocity = 9.8

    flower_adult_age = 10
    flower_seed_period = 5
    # flower_adult_age = 1
    # flower_seed_period = 0

    boid_starting_food_level = 40
    boid_maximum_food_level = 100
    boid_hungry_level = 5
    boid_adult_age = 50

    flower_food_source_offset = pygame.Vector2(12, -187)
    flower_food_source_radius = 45
    flower_food_source_starting_level = 100
    flower_food_source_maximum_level = 100
    flower_food_source_weight = 100
    flower_food_source_top_up_speed = 5

    feeding_speed = 5
    mating_attraction_force_weight = 50
    minimum_time_between_matings = 5

    minimum_number_of_babies = 2
    maximum_number_of_babies = 5
    maximum_baby_distance = 20
