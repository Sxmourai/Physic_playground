import pygame
from pygame import Vector2 as vec2
from pygame import Color
from shapes import *

class DrawingMode:
    HOTBAR_SIZE = vec2(40,40)
    def on_click(self, m: vec2, diagrams):
        pass
        # print(f"Clicked at {mx} {my}")
    def draw(self, screen: pygame.Surface):
        pass
    def reset(self):
        self.__init__()
    def img():
        img = pygame.Surface(DrawingMode.HOTBAR_SIZE)
        pygame.draw.circle(img, Color(255,0,0), DrawingMode.HOTBAR_SIZE/2, DrawingMode.HOTBAR_SIZE.x/2, 5)
        pygame.draw.line(img, Color(255,0,0), DrawingMode.HOTBAR_SIZE/2-DrawingMode.HOTBAR_SIZE/4, DrawingMode.HOTBAR_SIZE/2+DrawingMode.HOTBAR_SIZE/4, 5)
        return img


class LineMode(DrawingMode):
    def __init__(self,) -> None:
        super().__init__()
        self.start = None
        self.end = None
    def on_click(self, m: vec2, diagrams):
        if self.start == None:
            self.start = m
        elif self.end == None:
            self.end = m
            diagrams.append(Line(self.start,self.end,Color(255,255,255), 1))
            self.reset()
    def draw(self, screen: pygame.Surface):
        if self.start != None:
            pygame.draw.line(screen, Color(200,200,200), self.start, pygame.mouse.get_pos())
        elif self.end != None:
            print("Should never happen", self.end)
    def img():
        img = pygame.Surface(DrawingMode.HOTBAR_SIZE)
        pygame.draw.line(img, Color(255,255,255), (0,0), (img.get_width(),img.get_height()), 2)
        return img
    


class RunMode(DrawingMode):
    def on_click(self, m: vec2, diagrams):
        pass
    def img():
        img = pygame.Surface(DrawingMode.HOTBAR_SIZE)
        w,h = DrawingMode.HOTBAR_SIZE
        pygame.draw.polygon(img, Color(255,255,255), ((0,0), (w,h/2),(0,h)), 2)
        return img

