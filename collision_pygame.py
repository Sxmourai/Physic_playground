import sys
import math
import random as rd

import pygame
from pygame import Vector2 as vec2

pygame.init()
sw, sh = 800, 600
screen = pygame.display.set_mode((sw, sh))
pygame.display.set_caption("Collisions !")

class Object:
    def __init__(self, pos: vec2, ) -> None:
        self.pos = pos
        self.vel = vec2(0, 0)
        self.acc = vec2(0, 0)
        objects.append(self)
    
    def move(self):
        self.vel += self.acc * dt
        self.pos += self.vel * dt
        self.acc = vec2(0, 0)
    
    def draw(self):
        print("Drawing a null object !")
    def collide(self, obj):
        print("Colliding with a null object")
    
    def update(self):
        self.acc.y += .001 # Gravity
        self.vel *= .99 # Drag

class Circle(Object):
    def __init__(self, pos: vec2, radius: float):
        super().__init__(pos)
        self.radius = radius
        circles.append(self)
    
    def draw(self):
        pygame.draw.circle(screen, (255,255,255), self.pos, self.radius)
    
    # Check collision and fix
    def collide(self, obj: Object):
        if isinstance(obj, Circle): # Circle / circle
            pass
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

objects = []
circles = []

for i in range(100):
    a = Circle(vec2(rd.randrange(10, sw-10, 20), rd.randrange(10, 300)), 10)
    a.vel = vec2(rd.random()*2-1, -.2)
b = Circle(vec2(200, 300), 10)
b.vel = vec2(-.5, .2)
Ground(100)
ScreenBoundaries(vec2(0,0))

clock = pygame.time.Clock()
dt = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill((0, 0, 0))

    for i,obj in enumerate(objects):
        obj.update()
        obj.move()
        for j,obj2 in enumerate(objects):
            if i==j:continue
            obj.collide(obj2)
        obj.draw()

    pygame.display.flip()
    dt = clock.tick(60)
