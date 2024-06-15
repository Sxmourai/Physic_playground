import pygame

from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    frag = open("fragment.glsl").read()
    glGetUniformLocation(frag, "ourColor")
        
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        
        pygame.display.flip()
        pygame.time.wait(10)


main()
