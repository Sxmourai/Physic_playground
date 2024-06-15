import sys
from modes import *
from shapes import *

import pygame
from pygame import Vector2 as vec2
from pygame import Color

pygame.init()
sw, sh = 800, 600
screen = pygame.display.set_mode((sw, sh))
pygame.display.set_caption("Feynman !")

clock = pygame.time.Clock()

def vec_abs(vec: vec2):
    vec.x = abs(vec.x)
    vec.y = abs(vec.y)
    return vec

hotbar = [
    [DrawingMode.img(), DrawingMode()],
    [LineMode.img(), LineMode()],
    [RunMode.img(), RunMode()],
    [LineMode.img(), LineMode()],
    [LineMode.img(), LineMode()],
    [LineMode.img(), LineMode()],
]
hotbar_margin = 5

_drawing_mode = 0
def drawing_mode():return hotbar[_drawing_mode][1]

diagrams = [
    # [Surface, vec2 pos]
]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            m = pygame.mouse.get_pos()
            mx,my = m
            if my > sh-DrawingMode.HOTBAR_SIZE[1]-hotbar_margin*2:
                i = int((mx-5)/(DrawingMode.HOTBAR_SIZE.x+hotbar_margin*2))
                _drawing_mode = i
            else:
                drawing_mode().on_click(vec2(m), diagrams)

    screen.fill((0, 0, 0))
    for dia in diagrams:
        dia.draw(screen)
    drawing_mode().draw(screen)

    for i, (img, mode) in enumerate(hotbar):
        x = (i)*(DrawingMode.HOTBAR_SIZE.x+hotbar_margin*2)+5
        y = sh-DrawingMode.HOTBAR_SIZE[1]-5
        w = DrawingMode.HOTBAR_SIZE.x
        h = DrawingMode.HOTBAR_SIZE[1]
        screen.blit(img, (x+hotbar_margin, y-hotbar_margin, w, h))
        color = Color(200,200,200)
        if i == _drawing_mode:
            color = Color(255,0,0)
        pygame.draw.rect(screen, color, (x, y-hotbar_margin*2, w+hotbar_margin*2, h+hotbar_margin*2), 1)

    pygame.display.flip()
    clock.tick(60)
