import sys
import math

import pygame
from pygame import Vector2 as vec2

pygame.init()
sw, sh = 1920, 1080
screen = pygame.display.set_mode((sw, sh))

pygame.display.set_caption("Fluids !")

class Grid:
    def __init__(self, pos: vec2, density: float, size=vec2(sw/10,sh/10), border_color=pygame.Color(255,255,255),bg_color=pygame.Color(255,255,255)):
        self.pos = pos
        self.size = size
        self.border_color = border_color
        self.bg_color = bg_color
        self.density = density

grids = []
for x in range(0, sw, int(sw/10)):
    for y in range(0, sh, int(sh/10)):
        grids.append(Grid(vec2(x,y), density=1))

clock = pygame.time.Clock()
selected = None
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            grids[int(mx/(sw/10))*10+int(my/(sh/10))].density = 25

        elif event.type == pygame.MOUSEBUTTONUP:
            selected = None

    screen.fill((0, 0, 0))

    for i,g in enumerate(grids):
        b = int(max(0,min(255,255-g.density*10.)))
        g.bg_color = pygame.Color(g.bg_color.r,b,b,255)
        # grids[i] = g

    for g in grids:
        rect = pygame.Rect(g.pos.x,g.pos.y,g.size.x,g.size.y)
        pygame.draw.rect(screen, g.bg_color, rect)
        pygame.draw.rect(screen, g.border_color, rect, width=5)

    pygame.display.flip()
    clock.tick(60)
