# Following https://mikeash.com/pyblog/fluid-simulation-for-dummies.html

import sys
import numpy as np

import pygame
from pygame import Vector2 as vec2

pygame.init()
sw, sh = 800, 600
screen = pygame.display.set_mode((sw, sh))
pygame.display.set_caption("Fluid simulation, thx Mike Ash and Coding Train !")
clock = pygame.time.Clock()

def ix(pos):
    return pos.x+pos.y*80

size = (80, 60)
viscosity = .5
diffusion = .1
s = np.array([0 for _ in range(size)])
density = np.array([0 for _ in range(size)])

vels = np.array([[0, 0] for _ in range(size)])
vels0 = np.array([[0, 0] for _ in range(size)])

def add_density(pos, amount):
    density[ix(pos)] += amount

def add_vel(pos, amount: np.ndarray):
    vels[ix(pos)] += amount


def set_bnd(b: int, x: np.ndarray):
    for j in range(1, size-1):
        for i in range(1, size-1):
            if -
            x[ix(i,j)] = b


dt = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill((0, 0, 0))
    
    diffuse(1, vels0, vels, viscosity, dt)
    diffuse(2, vels0, vels, viscosity, dt)
    diffuse(3, vels0, vels, viscosity, dt)
    
    project(vels0, vels, 4)
    
    advect(1, vels, vels0, dt)
    advect(2, vels, vels0, dt)
    advect(3, vels, vels0, dt)
    
    project(vels, vels0, 4)
    
    diffuse(0, s, density, diffusion, dt, 4)
    advect(0, density, s, vels, dt)

    pygame.display.flip()
    dt = clock.tick(60)
