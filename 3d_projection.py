import sys
from math import *
import numpy as np
from numpy import matrix as mat

import pygame

pygame.init()
sw, sh = 800, 600
screen = pygame.display.set_mode((sw, sh))
pygame.display.set_caption("3d projection !")

angle = 0
points = [
    mat([ 1.,  1., -1]),
    mat([ 1., -1., -1]),
    mat([-1.,  1., -1]),
    mat([-1., -1., -1]),
    mat([ 1.,  1., 1.]),
    mat([ 1., -1., 1.]),
    mat([-1.,  1., 1.]),
    mat([-1., -1., 1.]),
]



projectionMatrix = np.matrix([[1, 0, 0],
                              [0, 1, 0],
                              [0, 0, 1],
                              ])
clock = pygame.time.Clock()
while True:
    screen.fill((0, 0, 0))
    rotation2d = np.array([[cos(angle), -sin(angle), 0],
                     [sin(angle), cos(angle), 0],
                     [0, 0, 1]])
    rotationX = np.array([[1, 0, 0],
                          [0, cos(angle), -sin(angle)],
                          [0, sin(angle), cos(angle)]])
    rotationY = np.array([[cos(angle), 0, sin(angle)],
                          [0, 1, 0],
                          [-sin(angle), 0, cos(angle)]])
    rotationZ = np.array([[cos(angle), -sin(angle), 0],
                          [sin(angle), cos(angle), 0],
                          [0, 0, 1]])
    
    projected = []
    for point in points:
        scale = 100.
        rotations = rotationY
        pos = projectionMatrix * (rotationZ * (rotationX * (rotationY * point.reshape((3, 1))))) * scale
        # pos = projectionMatrix * (rotations * point.reshape((3, 1))) * scale
        projected.append((int(pos[0][0]+sw/2), int(pos[1][0]+sh/2)))
    
    for i,(p1x, p1y) in enumerate(projected):
        pygame.draw.circle(screen, (255,255,255), (p1x, p1y), 10.)
        p1 = points[i]
        for j,(p2x,p2y) in enumerate(projected):
            p2 = points[j]
            dx = abs(p1[0, 0]-p2[0, 0])
            dy = abs(p1[0, 1]-p2[0, 1])
            dz = abs(p1[0, 2]-p2[0, 2])
            if (dx != 0 and dy != 0) or (dy != 0 and dz != 0) or (dx != 0 and dz != 0):
                continue
            pygame.draw.aaline(screen, (255,255,255), (p1x, p1y),(p2x, p2y), 3)
            

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.flip()
    angle += clock.tick(60)/1000
