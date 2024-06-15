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
    mat([ .5,  .5, -.5]),
    mat([ .5, -.5, -.5]),
    mat([-.5,  .5, -.5]),
    mat([-.5, -.5, -.5]),
    mat([ .5,  .5,  .5]),
    mat([ .5, -.5,  .5]),
    mat([-.5,  .5,  .5]),
    mat([-.5, -.5,  .5]),
]



clock = pygame.time.Clock()

def connect(a, b, points):
    p1x,p1y = points[a][0:2]
    p2x,p2y = points[b][0:2]
    pygame.draw.aaline(screen, (255,255,255), (p1x, p1y),(p2x, p2y), 3)


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
        scale = 200.
        rotations = rotationY
        
        rotated = (rotationX * (rotationY * (rotationZ * point.reshape((3, 1)))))
        distance = 1.5
        z = 1 / (rotated[2, 0] - distance)
        projectionMatrix = np.matrix([[z, 0, 0],
                                    [0, z, 0],
                                    [0, 0, 1],
                                    ])
        pos = projectionMatrix * rotated * scale
        # pos = projectionMatrix * (rotations * point.reshape((3, 1))) * scale
        projected.append((int(pos[0][0]+sw/2), int(pos[1][0]+sh/2)))
    
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
