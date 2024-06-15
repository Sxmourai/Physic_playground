import sys
from math import *
import numpy as np
from numpy import matrix as mat
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import pygame_widgets

import pygame

pygame.init()
sw, sh = 1920, 1080
screen = pygame.display.set_mode((sw, sh))
pygame.display.set_caption("4d projection !")

simulation_angle = 0

# Generates an object in n dimensions (2 = square, 3=cube, 4=hypercube ...)
def obj(n) -> np.matrix:
    if n == 2:
        return mat([
            [ .5,  .5],
            [ .5, -.5],
            [-.5,  .5],
            [-.5, -.5],
        ])
    sub_cube = obj(n-1)
    columns = np.shape(sub_cube)[1]
    normal = np.insert(sub_cube, columns, .5, 1)
    inverted = np.insert(sub_cube, columns, -.5, 1)
    return np.concatenate((normal, inverted))



points = mat([
    [ .5,  .5, -.5,  .5],
    [ .5, -.5, -.5,  .5],
    [-.5,  .5, -.5,  .5],
    [-.5, -.5, -.5,  .5],
    [ .5,  .5,  .5,  .5],
    [ .5, -.5,  .5,  .5],
    [-.5,  .5,  .5,  .5],
    [-.5, -.5,  .5,  .5],

    [ .5,  .5, -.5, -.5],
    [ .5, -.5, -.5, -.5],
    [-.5,  .5, -.5, -.5],
    [-.5, -.5, -.5, -.5],
    [ .5,  .5,  .5, -.5],
    [ .5, -.5,  .5, -.5],
    [-.5,  .5,  .5, -.5],
    [-.5, -.5,  .5, -.5],
])

points = obj(4)

slider = Slider(screen, 30, 30, 200, 20, min=0, max=10, step=.01)

camera_rotation = (3.14/2,0)

def get_rotationXX(angle):
    return np.array([[1, 0, 0, 0],
                          [0, cos(angle), -sin(angle), 0],
                          [0, sin(angle), cos(angle), 0],
                          [0, 0, 0, 1],
                          ])
def get_rotationXZ(angle):
    return np.array([[cos(angle), 0, sin(angle), 0],
                          [0, 1, 0, 0],
                          [-sin(angle), 0, cos(angle), 0],
                          [0, 0, 0, 1],
    ])
def get_rotationXY(angle):
    return np.array([[cos(angle), -sin(angle), 0, 0],
                          [sin(angle), cos(angle), 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1],
                          ])
def get_rotationZW(angle):
    return np.array([[1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, cos(angle), -sin(angle)],
                    [0, 0, sin(angle), cos(angle)],
                    ])

def project(points):
    rotationZW = get_rotationZW(simulation_angle)
    rotationXY = get_rotationXY(simulation_angle)
    rotationXZ = get_rotationXZ(simulation_angle)
    camera_rot_matrix = get_rotationXX(-camera_rotation[1]), get_rotationXY(-camera_rotation[0])
    projected = []
    for point in points:
        scale = 200.
        distance = slider.getValue()
        w = 1 / (distance - point[0, 3])
        projectionMatrix = mat([[w, 0, 0, 0],
                                    [0, w, 0, 0],
                                    [0, 0, w, 0],
                                    [0, 0, 0, 0],
                                    ])
        p = point.reshape((4, 1))
        rotated = camera_rot_matrix[1] * (camera_rot_matrix[0] * (rotationZW * (rotationXY * p)))
        pos = (projectionMatrix * rotated) * scale
        projected.append((int(pos[0, 0]+sw/2), int(pos[1, 0]+sh/2)))

    return projected


def connect(a, b, points):
    p1x,p1y = points[a][0:2]
    p2x,p2y = points[b][0:2]
    pygame.draw.aaline(screen, (255,255,255), (p1x, p1y),(p2x, p2y), 3)

clock = pygame.time.Clock()
dragging = False

while True:
    screen.fill((0, 0, 0))
    
    projected = project(points)

    for i,(p1x, p1y) in enumerate(projected):
        pygame.draw.circle(screen, (255,0,0), (p1x, p1y), 5.)
        p1 = points[i]
        for j,(p2x, p2y) in enumerate(projected):
            if i==j:continue
            p2 = points[j]
            dst = (p2-p1)
            length = dst.dot(np.squeeze(np.asarray(dst)))
            if length <= 1:
                connect(i,j, projected)

    evs = pygame.event.get()
    for event in evs:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging and not slider.selected:
            dx,dy = event.rel
            camera_rotation = (camera_rotation[0] + event.rel[0]/100, camera_rotation[1] + event.rel[1]/100)
    pygame_widgets.update(evs)
    pygame.display.flip()
    # print(clock.get_fps())
    simulation_angle += clock.tick(100)/1000
