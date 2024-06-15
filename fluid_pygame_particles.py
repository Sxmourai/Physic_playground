import sys
import math
import random

import pygame
from pygame import Vector2 as vec2

pygame.init()
sw, sh = 800, 600
screen = pygame.display.set_mode((sw, sh))

pygame.display.set_caption("Fluids !")

class Particle:
    def __init__(self, pos: vec2, radius:float=5., color=pygame.Color(255,255,255)):
        self.pos = pos
        self.radius = radius
        self.radius_effect = 40
        self.vel = vec2(0,0)
        self.color = color
        self.prev = pos
class Spring:
    def __init__(self, p1:int,p2:int, rest_len:float):
        self.p1=p1
        self.p2=p2
        self.rest_len = rest_len

def applyViscosity():
    viscosity_1 = .000001
    viscosity_2 = .0000001
    for i,p in enumerate(particles):
        for j in range(len(particles)):
            if i==j:continue
            p2 = particles[j]
            dst = (p.pos - p2.pos).length()
            q = dst / p.radius_effect
            if q < 1:
                dvel = (p.vel - p2.vel)
                u = dvel.dot(dvel)
                if u > 0 and u < 1000000000:
                    impulse = (1-q)*(viscosity_1 * u + viscosity_2*(u**2)) * dvel
                    p.vel = p.vel - impulse/2
                    p2.vel = p2.vel - impulse/2


def adjustSprings():
    yield_ratio = 0.1 # Typically between 0-0.2
    # for i,p in enumerate(particles):
    #     for j in range(len(particles)):
    #         if i==j:continue
    #         p2 = particles[j]
    #         dst = (p.pos - p2.pos).length()
    #         q = dst / p.radius_effect
    #         if q < 1:
    #             spring = Spring(i,j, p.radius_effect)
    #             if spring not in springs:
    #                 springs.append(spring)
    #             # tolerable deformation = yield ratio * rest length
    #             d = yield_ratio * Lij
    #             if dst > L+d: # Stretch
    #                 Lij = Lij + alpha * (dst - L - d)
    #             elif dst < L - d: # Compress
    #                 Lij = Lij - alpha * (L - d - dst)
                
    # for spring in springs[:]:
    #     p = particles[spring.p1]
    #     if Lij > p.radius_effect:
    #         springs.remove(spring)

def applySpringDisplacements():
    for spring in springs:
        p = particles[spring.p1]
        # p2 = particles[spring.p2]
        # dst = (p.pos - p2.pos).length()
        # dvel = (p.vel - p2.vel)
        # D = (1 - Lij/p.radius_effect)*(Lij-dst)*dvel
        # p.pos -= D/2.
        # p2.pos += D/2.

def doubleDensityRelaxation():
    rest_density = 2
    stiffness = 1.
    near_stiffness = .5
    
    # Neighbor cache
    neighborIndices = []
    neighborUnitX = []
    neighborUnitY = []
    neighborCloseness = []
    for i,p in enumerate(particles):
        density = 0
        density_near = 0
        n_neighbors = 0
        for j in range(len(particles)):
            if i==j:continue
            p2 = particles[j]
            dst = (p2.pos - p.pos)
            q = dst.length() / p.radius_effect
            if q < 1:
                density += (1 - q)**2
                density_near += (1-q)**3
                neighborIndices.append(j)
                neighborUnitX.append(dst.x / dst.length())
                neighborUnitY.append(dst.y / dst.length())
                neighborCloseness.append((1 - q))
                n_neighbors += 1
                
        # Walls
        closest = vec2(min(p.pos.x, sw-p.pos.x),min(p.pos.y, sh-p.pos.y))
        
        # if closest.x < p.radius_effect:
        #     q = closest.x / p.radius_effect
        #     closeness = 1 - q
        #     density += closeness**2
        #     density_near += closeness**3
        # if closest.y < p.radius_effect:
        #     q = closest.y / p.radius_effect
        #     closeness = 1 - q
        #     density += closeness**2
        #     density_near += closeness**3
        pressure = stiffness * (density-rest_density)
        pressure_near = near_stiffness * density_near
        p.color.r = min(255, int(pressure*100))
        p.color.g = min(255, int(pressure_near*200))
        disp = vec2(0,0)
        for j in range(n_neighbors):
            p2 = particles[neighborIndices[j]]
            closeness = neighborCloseness[j]
            D = dt*dt*(pressure * closeness + pressure_near * closeness * closeness) / 2
            DISP = vec2(D * neighborUnitX[j], D * neighborUnitY[j])
            p2.pos += DISP
            disp -= DISP
        p.pos += disp
    


particles = []
springs = []
for i in range(200):
    x = random.randrange(0, sw)
    y = random.randrange(0, sh)
    particles.append(Particle(vec2(x,y), radius=10))

collisionDamping = 0.5
clock = pygame.time.Clock()
selected = None
dt = 0.1
while True:
    print(dt)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            

        elif event.type == pygame.MOUSEBUTTONUP:
            selected = None

    screen.fill((0, 0, 0))

    for i,p in enumerate(particles):
        p.vel.y += .5 * dt

    # applyViscosity()
    
    for p in particles:
        p.prev = p.pos
        p.pos += p.vel * dt
        
    # adjustSprings()
    # applySpringDisplacements()
    doubleDensityRelaxation()

    for p in particles:
        boundaryMul = 1.5 * dt # 1 is no bounce, 2 is full bounce
        boundaryMinX = 0 + p.radius
        boundaryMaxX = sw - p.radius
        boundaryMinY = 0 + p.radius
        boundaryMaxY = sh - p.radius
        if p.pos.x < boundaryMinX:
            p.pos.x += boundaryMul * (boundaryMinX - p.pos.x)
        if p.pos.x > boundaryMaxX:
            p.pos.x += boundaryMul * (boundaryMaxX - p.pos.x)
        
        if p.pos.y < boundaryMinY:
            p.pos.y += boundaryMul * (boundaryMinY - p.pos.y)
        if p.pos.y > boundaryMaxY:
            p.pos.y += boundaryMul * (boundaryMaxY - p.pos.y)
            
        p.vel = (p.pos - p.prev) / dt
        
        pygame.draw.circle(screen, p.color, p.pos, p.radius)

    pygame.display.flip()
    dt = clock.tick(60) / 10
