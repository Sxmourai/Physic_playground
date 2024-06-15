from array import array
import random
import util
from arcade.experimental import shadertoy

class Screen(util.Simulation):
    def __init__(self):
        self._setup("Raycast", compute_shader=False)
        self.shader = shadertoy.Shadertoy((self.width, self.height), open("raycast_2nd.glsl").read())

    def on_draw(self):
        self.shader.render()

        self._draw_fps()

util.run(Screen())
