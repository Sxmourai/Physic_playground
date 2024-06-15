import pygame
from pygame import Vector2 as vec2
from pygame import Color

class Shape:
    def draw(self, screen):
        pass

class Line(Shape):
    def __init__(self, start: vec2, end: vec2, color: Color, width: int):
        self.start = start
        self.end = end
        self.color = color
        self.width = width
    def draw(self, screen):
        pygame.draw.line(screen, self.color, self.start, self.end, self.width)

class Circle(Shape):
    def __init__(self, center: vec2, radius: vec2, color: Color, width: int):
        self.center = center
        self.radius = radius
        self.color = color
        self.width = width
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.center, self.radius, self.width)

