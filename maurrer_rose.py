import sys
from math import *
import pygame
from pygame import Vector2 as vec2
from pygame_widgets.slider import Slider
import pygame_widgets
from colorsys import *

pygame.init()
s = vec2(1920, 1080)
screen = pygame.display.set_mode(s)
pygame.display.set_caption("Maurrer rose !")
slider = Slider(screen, 40, 40, 500, 40, min=0, max=99, step=.001, initial=0)

def polar_to_cartesian(theta, distance) -> vec2:
    x = distance * cos(theta)
    y = distance * sin(theta)
    return vec2(x,y)

clock = pygame.time.Clock()
while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill((0, 0, 0))
    n = slider.getValue()

    d = 29
    ps = []
    ps2 = []
    for theta in range(361):
        k = theta*d
        r = sin(n * k)
        ps.append((s/2+polar_to_cartesian(k, r*(s.y/2-20)), hls_to_rgb(theta/(360), 100, 255)))
        k = theta
        r = sin(n * k)
        ps2.append(s/2+polar_to_cartesian(k, r*(s.y/2-20)))

    pygame.draw.aalines(screen, (255,255,255), True, list(map(lambda x: x[0], ps)))
    for l1,l2,l3 in zip(ps[::2], ps[1::2], ps[2::2]):
        color = max(0, min(int(l1[1][0]), 255)),max(0, min(int(l1[1][1]), 255)),max(0, min(int(l1[1][2]), 255), 100)
        pygame.draw.aaline(screen, color, l1[0], l2[0])
        color = max(0, min(int(l2[1][0]), 255)),max(0, min(int(l2[1][1]), 255)),max(0, min(int(l2[1][2]), 255), 100)
        pygame.draw.aaline(screen, color, l2[0], l3[0])
        
    # pygame.draw.aalines(screen, (255,0,0), True, ps2)
    # for theta in range(360):
    #     pygame.draw.aaline(screen, (255,255,255), s/2, s/2+polar_to_cartesian(r, theta))

    n += .000001
    slider.setValue(n)
    pygame_widgets.update(events)
    pygame.display.flip()
    clock.tick(60)
    # n = 7
    # d = 29
    # ps = []
    # for theta in range(361):
    #     r = sin(n * theta*d)
    #     ps.append(s/2+polar_to_cartesian(theta, r*d*10))

    # pygame.draw.aalines(screen, (255,255,255), True, ps)