import sys
from math import *
import numpy as np
from numpy import matrix as mat

import pygame

pygame.init()
sw, sh = 800, 600
screen = pygame.display.set_mode((sw, sh))
pygame.display.set_caption("4d projection !")

angle = 0
points = [
    mat([ .5,  .5, -.5, 1.]),
    mat([ .5, -.5, -.5, 1.]),
    mat([-.5,  .5, -.5, 1.]),
    mat([-.5, -.5, -.5, 1.]),
    mat([ .5,  .5,  .5, 1.]),
    mat([ .5, -.5,  .5, 1.]),
    mat([-.5,  .5,  .5, 1.]),
    mat([-.5, -.5,  .5, 1.]),
]



projectionMatrix = np.matrix([[1, 0, 0, 0],
                              [0, 1, 0, 0],
                              [0, 0, 1, 0],
                              [0, 0, 0, 1],
                              ])

def project(points):
    rotationX = np.array([[1, 0, 0, 0],
                          [0, cos(angle), -sin(angle), 0],
                          [0, sin(angle), cos(angle), 0],
                          [0, 0, 0, 1],
                          ])
    rotationY = np.array([[cos(angle), 0, sin(angle), 0],
                          [0, 1, 0, 0],
                          [-sin(angle), 0, cos(angle), 0],
                          [0, 0, 0, 1],
    ])
    rotationZ = np.array([[cos(angle), -sin(angle), 0, 0],
                          [sin(angle), cos(angle), 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1],
                          ])
    
    projected = []
    for point in points:
        scale = 200.
        rotations = rotationY
        pos = projectionMatrix * (rotationX * (rotationY * (rotationZ * point.reshape((4, 1))))) * scale
        projected.append((int(pos[0][0]+sw/2), int(pos[1][0]+sh/2)))
    
    return projected


def connect(a, b, points):
    p1x,p1y = points[a][0:2]
    p2x,p2y = points[b][0:2]
    pygame.draw.aaline(screen, (255,255,255), (p1x, p1y),(p2x, p2y), 3)

clock = pygame.time.Clock()
while True:
    screen.fill((0, 0, 0))
    
    projected = project(points)

    for i,(p1x, p1y) in enumerate(projected):
        pygame.draw.circle(screen, (255,255,255), (p1x, p1y), 10.)
        p1 = points[i]
        for j,(p2x, p2y) in enumerate(projected):
            if i==j:continue
            p2 = points[j]
            dst = (p2-p1)
            length = dst.dot(np.squeeze(np.asarray(dst)))
            if length <= 1:
                connect(i,j, projected)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.flip()
    angle += clock.tick(60)/1000
