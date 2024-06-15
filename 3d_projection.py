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
    [ .5,  .5, -.5],
    [ .5, -.5, -.5],
    [-.5,  .5, -.5],
    [-.5, -.5, -.5],
    [ .5,  .5,  .5],
    [ .5, -.5,  .5],
    [-.5,  .5,  .5],
    [-.5, -.5,  .5],
])
points = obj(3)



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
        rotated = (1 * (rotationZ.dot(rotationX.dot(point.reshape(3,1)))))
        distance = 2.0
        z = 1
        # Perspective:
        z = 1 / (distance - rotated[2, 0])
        projectionMatrix = mat([[z, 0, 0],
                                    [0, z, 0],
                                    [0, 0, 1],
                                ])
        pos = (projectionMatrix * rotated) * (distance * scale) # Scale by distance so we always have same size, but we have a different perspective effect
        projected.append((int(pos[0, 0]+sw/2), int(pos[1, 0]+sh/2)))
    
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
