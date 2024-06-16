import sys
import math
import random as rd

import pygame
from pygame import Vector2 as vec2

pygame.init()
sw, sh = 800, 600
screen = pygame.display.set_mode((sw, sh))
pygame.display.set_caption("Collisions !")
pygame.font.init() # For FPS counter
fps_font = pygame.font.SysFont('Arial', 30)

class Object:
    def __init__(self, pos: vec2, ) -> None:
        self.pos = pos
        self.vel = vec2(0, 0)
        self.acc = vec2(0, 0)
    
    @property
    def next_pos(self):
        return self.pos+self.vel*dt
    
    def move(self):
        self.vel += self.acc * dt
        self.pos += self.vel * dt
        self.acc = vec2(0, 0)
    
    def draw(self):
        print("Drawing a null object !")
    def collide(self, obj):
        print("Colliding with a null object")
    
    def update(self):
        self.acc.y += 1 # Gravity
        self.vel *= .99 # Drag
        if self.vel.x < .01:
            self.vel.x = 0
        if self.vel.y < .01:
            self.vel.y = 0

# Trying to make some XPBD based physics
class Constraint:
    def __init__(self, Lambda, force, compliance=0.0001) -> None:
        self.Lambda = Lambda
        self.compliance = compliance
        self.force = force
    def solve(self):
        print("Solving null constraint !")

class DragConstraint(Constraint):
    def __init__(self, object: Object, Lambda, force, compliance=0.0001):
        super().__init__(Lambda, force, compliance)
        self.obj = object
    
    def solve(self): # Follwing https://github.com/johnBuffer/Pendulum-NEAT/blob/main/src/user/common/physic/constraints/drag_constraint.hpp
        pass


class Circle(Object):
    def __init__(self, pos: vec2, radius: float):
        super().__init__(pos)
        self.radius = radius
    
    def draw(self):
        pygame.draw.circle(screen, (255,255,255), self.pos, self.radius)
    
    def grid_idx(self):
        x = self.pos.x/100
        y = self.pos.y/100
        return int(x+y*(sw/100))
    
    # Check collision and fix
    def collide(self, obj: Object):
        if isinstance(obj, Circle): # Circle / circle
            # Can use dot product & all, but it's more efficient cuz made in C
            for i in range(10):
                dst_sq = self.pos.distance_squared_to(obj.pos)
                if dst_sq < (self.radius+obj.radius)**2 and dst_sq > 0.001: # Collision response using https://ericleong.me/research/circle-circle/
                    dst = math.sqrt(dst_sq)
                    n = (obj.pos - self.pos) / dst
                    p = (self.vel.x * n.x + self.vel.y * n.y - obj.vel.x * n.x - obj.vel.y * n.y);
                    self.vel -= p * n * .99
                    obj.vel += p * n * .99
                    # if (p * n).length_squared() < .01:
                    #     self.vel = vec2(0)
                    #     self.acc = vec2(0)
                    #     obj.vel = vec2(0)
                    #     obj.acc = vec2(0)
                    dst_sq = obj.next_pos.distance_squared_to(self.next_pos)
                    if dst_sq < (self.radius+obj.radius)**2: # Static circle response because they are still overlapping
                        midpoint = (self.pos+obj.pos)/2
                        self.pos = midpoint + self.radius * (self.pos - obj.pos) / dst
                        obj.pos = midpoint + obj.radius * (obj.pos - self.pos) / dst
                        # print(f"still colliding ({self.vel} and {obj.vel})")
                    else:
                        break
                else:break

            # return c2c_collide(self, obj)
        elif isinstance(obj, Ground): # Ground / circle
            if self.pos.y+self.radius>=obj.pos.y: # Collision
                self.pos.y = obj.pos.y - self.radius
                self.vel.y *= -.9
        elif isinstance(obj, ScreenBoundaries): # Circle outside of screen
            if self.pos.y+self.radius>=sh:
                self.pos.y = sh-self.radius
                self.vel.y *= -.9
            if self.pos.x+self.radius>=sw:
                self.pos.x = sw-self.radius
                self.vel.x *= -.9
            
            if self.pos.y-self.radius<=0:
                self.pos.y = 0+self.radius
                self.vel.y *= -.9
            if self.pos.x-self.radius<=0:
                self.pos.x = 0+self.radius
                self.vel.x *= -.9


class Ground(Object):
    def __init__(self, height: float):
        super().__init__(vec2(0, sh-height))
        self.size = vec2(sw, height)
    
    def move(self):
        pass # Stops object from moving

    def draw(self):
        pygame.draw.rect(screen, (255,255,255), (self.pos, self.size))
    
    def collide(self, *args, **kwargs):
        pass # We don't need to move the object, but other objects can collide with him, it's like (circle -> ground checked but ground -> circle not checked, but it doesn't change anything)

class ScreenBoundaries(Object):
    def move(self):
        pass
    def draw(self):
        pass
    def collide(self, obj: Object):
        pass # same as ground

objects: list[Object] = [
    Ground(100),
    ScreenBoundaries(vec2(0,0)),
]
circles: list[Circle] = []


for i in range(200):
    a = Circle(vec2(rd.randrange(10, sw-10, 20), rd.randrange(10, 300)), 10)
    a.vel = vec2(rd.random()*2-1, -2)
    objects.append(a)
    circles.append(a)

def get_world_grids():
    grids = []
    for x in range(0, sw, 100):
        for y in range(0, sh, 100):
            grids.append([])
    for i,c in enumerate(circles):
        grids[c.grid_idx()].append(i)
    return grids


clock = pygame.time.Clock()
dt = 0.0001
ticks = 0
fps_surface = fps_font.render(f'60 FPS', True, (255, 255, 255))
game_speed = 10
world_grids = get_world_grids()
while True:
    ticks += 1
    if ticks%6==0:
        fps_surface = fps_font.render(f'{round(clock.get_fps())} FPS', True, (255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill((0, 0, 0))
    screen.blit(fps_surface, (10, 10))

    for i,obj in enumerate(objects):
        obj.update()
    for i in range(3):
            for j,obj2 in enumerate(objects):
                if i==j:continue
    for i,obj in enumerate(objects):
        obj.collide(obj)

    for i,obj in enumerate(objects):
        obj.move()
        obj.draw()
    world_grids = get_world_grids()

    pygame.display.flip()
    dt = game_speed/clock.tick(60)

