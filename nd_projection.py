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
DIMS = 4
pygame.display.set_caption(f"{DIMS}d projection !")

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

points = obj(DIMS)
slider = Slider(screen, 30, 30, 200, 20, min=0, max=10, step=.01, initial=1.5)

camera_rotation = (300.,150)

# Generates a transformation matrix from coordinates of sines and cosines
# Coordinates are (x,y)
def rotation_matrix(angle, cos1: tuple[int, int], cos2, sin_coord, minus_sin, dims: int=DIMS):
    matrix = mat(np.zeros((dims, dims)))
    for i in range(dims): # Diagonal ones
        matrix[i, i] = 1
    matrix[cos1[1], cos1[0]] = cos(angle)
    matrix[cos2[1], cos2[0]] = cos(angle)
    matrix[sin_coord[1], sin_coord[0]] = sin(angle)
    matrix[minus_sin[1], minus_sin[0]] = -sin(angle)
    return matrix

def R(mat: np.matrix, row: int, col: int, angle: float):
    mR = np.matrix(np.zeros(mat.shape))
    for m in range(mR.shape[0]):
        for n in range(mR.shape[1]):
            if m == row and n == row:
                mR[m, n] = cos(angle)
            elif m == col and n == col:
                mR[m, n] = -sin(angle)
            elif m == row and n == col:
                mR[m, n] = -sin(angle)
            elif m == col and n == row:
                mR[m, n] = sin(angle)
            elif m == n and m != row and n != col:
                mR[m, n] = 1

    return mR

def invert(matrix):
    return mat([[1/float(x[0]) for x in line] for line in matrix])

# Following Aguilera-Pérez Algorithm at http://wscg.zcu.cz/wscg2004/Papers_2004_Short/N29.pdf
def rotate(mat: np.matrix, angle: float, n: int):
    if n <= 2:
        if n == 0:
            return np.array(mat) * np.array(R(mat, n, 2, angle)) * np.array(invert(mat))
        else:
            return np.array(mat) * np.array(R(mat, n - 1, n, angle)) * np.array(invert(mat))
    
    mM = np.zeroes(mat.shape)
    v = np.zeroes(mat.shape)
    v[0] = mat
    mM[1] = invert(mat)
    v[1] = mat * mM[1]
    mM[0] = mM[1]
    
    k = 1
    for r in range(2, n, 1):
        c = n
        while c >= r:
            c -= 1
            k += 1
            mM[k] = R(mat, c, c-1, atan2(v[k-1][r, c], v[k-1][r, c-1]))
            v[k] = v[k-1] * mM[k]
            mM[0] *= mM[k]
            
    return mM[0] * R(mat, n - 1, n, angle) * invert(mM[0])

# Same as
# return mat([[cos(angle), -sin(angle), 0],
#                  [sin(angle), cos(angle), 0],
#                  [0, 0, 1]])
def get_rotationXX(angle):
    return rotation_matrix(angle, cos1=(1,1), cos2=(2,2), sin_coord=(1,2), minus_sin=(2,1))
def get_rotationXZ(angle):
    return rotation_matrix(angle, cos1=(0,0), cos2=(2,2), sin_coord=(2,0), minus_sin=(0,2))
def get_rotationXY(angle):
    return rotation_matrix(angle, cos1=(0,0), cos2=(1,1), sin_coord=(0,1), minus_sin=(1,0))
def get_rotationZW(angle):
    return rotation_matrix(angle, cos1=(2,2), cos2=(3,3), sin_coord=(2,3), minus_sin=(3,2))

def project(points):
    rotationZW = get_rotationZW(simulation_angle)
    rotationXY = get_rotationXY(simulation_angle)
    rotationXZ = get_rotationXZ(simulation_angle)
    camera_rot_matrix = get_rotationXX(-camera_rotation[1]), get_rotationXY(-camera_rotation[0])
    projected = []
    for point in points:
        scale = 200.
        distance = slider.getValue()
        p = point.reshape((DIMS, 1))
        rotated = camera_rot_matrix[1] * (camera_rot_matrix[0] * (rotationZW * (rotate(p, simulation_angle, 1))))
        w = 1 / (distance - rotated[DIMS-1])
        projectionMatrix = np.zeros((DIMS,DIMS))
        np.fill_diagonal(projectionMatrix, w)
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
    simulation_angle += clock.tick(100)/1000

