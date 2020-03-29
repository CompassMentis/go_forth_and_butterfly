import pygame


class Settings:
    screen_size = pygame.math.Vector2(1840, 1035)
    screen_size_as_integer = int(screen_size.x), int(screen_size.y)
    # number_of_boids = 10
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
    player_maximum_speed_multiplier = 2
    player_minimum_speed_multiplier = 0.3

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
    flower_food_source_weight = 500
    flower_food_source_top_up_speed = 5

    feeding_speed = 10
    mating_attraction_force_weight = 50
    minimum_time_between_matings = 5

    minimum_number_of_babies = 2
    maximum_number_of_babies = 5
    maximum_baby_distance = 20

    leader_weighing_factor = 10

    gate_radius = 27

    shouting_distance = 900
    shouting_force = 100

    time_keeper_location = pygame.Vector2(85, 85)
    time_keeper_radius = 49

    sunrise_start_angle = 45
    day_start_angle = 69
    sunset_start_angle = 360 - day_start_angle
    night_start_angle = 360 - sunrise_start_angle

    # To simplify this, calculations (and the game) starts at
    # the start of the day
    time_keeper_angle_offset = day_start_angle

    day_start_angle -= time_keeper_angle_offset
    sunset_start_angle = (sunset_start_angle - time_keeper_angle_offset) % 360
    night_start_angle = (night_start_angle - time_keeper_angle_offset) % 360
    sunrise_start_angle = (sunrise_start_angle - time_keeper_angle_offset) % 360

    day_angle_duration = sunset_start_angle
    sunset_angle_duration = night_start_angle - sunset_start_angle
    night_angle_duration = sunrise_start_angle - night_start_angle
    sunrise_angle_duration = day_start_angle - sunrise_start_angle + 360

    day_duration = 100
    sunset_duration = 20
    sunrise_duration = sunset_duration
    night_duration = 5
    time_keeper_one_day_duration = \
        day_duration + \
        sunset_duration + \
        sunrise_duration + \
        night_duration

    day_start_time = 0
    sunset_start_time = day_start_time + day_duration
    night_start_time = sunset_start_time + sunset_duration
    sunrise_start_time = night_start_time + night_duration

    # The larger this number, the faster the game goes
    # At 1, a day lasts time_keeper_total_duration seconds
    time_keeper_multiplier = 1

    boid_status_icon_offset = pygame.Vector2(16, 0)
    leader_status_icon_offset = pygame.Vector2(33, -9)

    time_to_die = 3

    console_location = pygame.Vector2(33, 835)

    help_text_location = pygame.Vector2(60, 70)
    line_spacing = 40
    font_size = 36

    console_text_location = console_location + pygame.Vector2(20, 5)
