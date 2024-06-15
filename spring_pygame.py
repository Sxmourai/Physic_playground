import sys
import math

import pygame
from pygame import Vector2 as vec2

pygame.init()
sw, sh = 1520, 980
screen = pygame.display.set_mode((sw, sh))

pygame.display.set_caption("Springs !")


class Spring:
    def __init__(self, p1: int, p2: int, desired_len: float = 100., solid: bool = False):
        self.p1 = p1
        self.p2 = p2
        self.desired_len = desired_len
        self.solid = solid


class Particle:
    def __init__(self, pos: vec2, vel: vec2 = vec2(0., 0.), color: pygame.Color = pygame.Color(255, 255, 255, 255), fixed: bool = False):
        self.pos = pos
        self.vel = vel
        self.color = color
        self.fixed = fixed


springs = []
particles = []
spring_count = 20
# for i in range(spring_count):
#     d_len = 100
#     p1x = sw / 2 - 50*int(spring_count/2) + 50*i
#     p1y = sh / 2 - d_len/2
#     p2x = p1x
#     p2y = sh / 2 + d_len/2
#     particles += [Particle(vec2(p1x, p1y), vec2(0., 0.), pygame.Color(255, 255, 255, 255)),
#                   Particle(vec2(p2x, p2y), vec2(0., 0.), pygame.Color(255, 255, 0, 255)),]
#     springs.append(Spring(i*2, i*2+1, d_len))

particles += [
              Particle(vec2(sw/2, sh/2), fixed=True),
              Particle(vec2(sw/2-100, sh/2)),
              Particle(vec2(sw/2-200, sh/2), vec2(0., 3.)),
            #   Particle(vec2(sw/2-100, sh/2-100)),
            #   Particle(vec2(sw/2-100, sh/2)),
            #   Particle(vec2(sw/2, sh/2)),
            #   Particle(vec2(sw/2, sh/2-100)),
            #   Particle(vec2(sw/2+100, sh/2)),
            #   Particle(vec2(sw/2+200, sh/2)),
            #   Particle(vec2(sw/2+300, sh/2)),
              ]
springs.append(Spring(0, 1,solid=True))
springs.append(Spring(1, 2,solid=True))
# springs.append(Spring(2, 3))
# springs.append(Spring(3, 4))
# springs.append(Spring(3, 5))
# springs.append(Spring(3, 6))

clock = pygame.time.Clock()
selected = None
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for i, p in enumerate(particles):
                # 10 is p.radius, so click on particle
                if abs(mx-p.pos.x) < 10 and abs(my-p.pos.y) < 10:
                    selected = i

        elif event.type == pygame.MOUSEBUTTONUP:
            selected = None

    # print(particles[0].vel)
    for s in springs:
        p1 = particles[s.p1]
        p2 = particles[s.p2]
        dist = p1.pos - p2.pos
        dist_sq = dist.dot(dist)
        if dist_sq < 0.2:continue
        force = (math.sqrt(dist_sq) - s.desired_len)/10.
        dir = dist.normalize()
        if s.solid:
            # Mult by 10 cuz divide by 10 up
            if p1.fixed is False and p2.fixed is False:
                p1.vel = p1.vel - (force*10 * dir)
                p2.vel = p2.vel + (force*10 * dir)
            elif p1.fixed:
                p2.vel = p2.vel + (force*10 * dir)*2
            elif p2.fixed:
                p1.vel = p1.vel - (force*10 * dir)*2
                
        else:
            p1.vel = p1.vel - (force * dir)
            p2.vel = p2.vel + (force * dir)

        particles[s.p1] = p1
        particles[s.p2] = p2

    for p1 in particles:
        pass
        # p1.vel.y += .5

    for p in particles:
        if p.pos.y+10+p.vel.y > sh:
            p.vel.y *= -.5
            p.pos.y = sh-10
        elif p.pos.y-10+p.vel.y < 0:
            p.vel.y *= -.5
            p.pos.y = 10
        if p.pos.x+10+p.vel.x > sw:
            p.vel.x *= -.5
            p.pos.x = sw-10
        elif p.pos.x-10+p.vel.x < 0:
            p.vel.x *= -.5
            p.pos.x = 10

    for p in particles:
        if p.fixed is True:
            # Can velocity become > than screen in a frame, in this case we should always set vel to 0 cuz up ^^
            p.vel = vec2(0.)
            # p.color.g = 255
            # p.color.b = 0
            # p.color.r = 0
        else:
            p.pos += p.vel
            # p.color.g = 0
            # p.color.b = 255
            # p.color.r = 0

            # p.color.g = max(0, int(255 - (p.vel.length()*4.)))
            # p.color.b = max(0, int(255 - (p.vel.length()*4.)))

            # p.vel *= .9

    # print(particles[0].vel)
    # print("------")
    
    if selected != None:
        mx, my = pygame.mouse.get_pos()
        particles[selected].pos.x = mx
        particles[selected].pos.y = my
        particles[selected].vel.x = 0
        particles[selected].vel.y = 0

    screen.fill((0, 0, 0))

    for s in springs:
        p1 = particles[s.p1]
        p2 = particles[s.p2]
        w = max(2, int(10 - (p1.pos - p2.pos).length()/50))
        # TODO Width en fonction taille
        pygame.draw.line(screen, (255, 255, 255), p1.pos, p2.pos, w)

    for p in particles:
        pygame.draw.circle(screen, p.color, p.pos, 10.)

    pygame.display.flip()
    clock.tick(60)
