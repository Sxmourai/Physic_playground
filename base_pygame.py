import sys
import math

import pygame
from pygame import Vector2 as vec2

pygame.init()
sw, sh = 1520, 980
screen = pygame.display.set_mode((sw, sh))
pygame.display.set_caption("3d projection !")

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))

    pygame.display.flip()
    clock.tick(60)
