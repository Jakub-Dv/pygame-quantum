try:
    import pygame
except:
    import subprocess, sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame

import random, time

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 760

pygame.init()
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((255, 255, 255))
    my_font = pygame.font.SysFont("Comic Sans MS", 28)
    text_surface = my_font.render(
        "See you on Friday ;)", False, (0, 0, 255), (255, 255, 255)
    )
    screen.blit(text_surface, (SCREEN_WIDTH / 8, SCREEN_HEIGHT / 3))
    pygame.display.flip()
    clock.tick(30)
