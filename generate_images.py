import os

import pygame

"""
Create butterflies

* For each type of butterfly (folder in assets/butterflies/<type>)
    * Source images: size_01.png 
    * Make sure there is a folder of the same name in images/butterflies
    * which contains 24 images, rotated in 5 degree steps, called butterfly_<rotation:03>_step_<step:02>.png
"""


def rotate_and_save(image, angle, target):
    target_image = pygame.Surface(image.get_rect().size, pygame.SRCALPHA)
    rotate_and_draw(target_image, image, (0, 0), angle)
    pygame.image.save(target_image, target)


def create_butterfly_images_for_size(image, target_folder, butterfly_type, size):
    try:
        os.mkdir(target_folder + butterfly_type)
    except FileExistsError:
        pass

    for angle in range(0, 360, 15):
        # TODO: Do 90 degree rotation in source images, not here?
        rotate_and_save(image, (angle - 90) % 360, f'{target_folder}{butterfly_type}/butterfly_{angle:03}_step_{size:02}.png')
        rotate_and_save(image, (angle - 90) % 360, f'{target_folder}{butterfly_type}/butterfly_{angle:03}_step_{(15-size):02}.png')


def main():
    source_folder = 'assets/butterflies/'
    target_folder = 'images/butterflies/'
    for butterfly_type in os.listdir(source_folder):
        if not os.path.isdir(source_folder + butterfly_type):
            continue

        for size in range(8):
            image = pygame.image.load(f'{source_folder}{butterfly_type}/size_{size:02}.png')
            create_butterfly_images_for_size(image, target_folder, butterfly_type, size)


def rotate_and_draw(canvas, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)
    canvas.blit(rotated_image, new_rect.topleft)


def test():
    source_folder = 'assets/butterflies/'
    image = pygame.image.load(source_folder + 'arrow.png')
    canvas = pygame.display.set_mode((700, 2000))
    for i in range(24):
        angle = i * 15
        y = (i // 5) * 75
        x = (i % 5) * 75
        rotate_and_draw(canvas, image, (x, y), angle)
        pygame.draw.rect(canvas, pygame.Color('white'), (x, y, 67, 67), 1)
        rotate_and_save(image, angle, f'images/butterflies/test{i:03}.png')
    pygame.display.flip()

    pygame.image.save(canvas, 'images/butterflies/test.png')


# test()
# a = input()
main()
