import struct
import pygame
from pygame import Vector3 as vec3
from pygame import Vector2 as vec2
import random
from array import array
import math
import sys
import arcade

import util

class Screen(util.Simulation):
    def __init__(self):
        self._setup("Fluids")
        self._vaos(self.ssbo_part_1, self.ssbo_part_2)
        
        self.density_compute_shader = self._compute_shader("fluid_density")
        self.compute_shader = self._compute_shader("fluid")

    def on_draw(self):

        sign = 0
        if self.mouse.data.get(1, False) == True:
            sign = 1
        elif self.mouse.data.get(4, False) == True:
            sign = -1
        if sign != 0:
            # print(dir(self.mouse.data), self.mouse.data)
            mx, my = self.mouse.data["x"], self.mouse.data["y"]
            parts = bytearray(self.ssbo_part_1.read())
            for i in range(int(len(parts)/(12*4))):
                x = struct.unpack("f", parts[(i*12*4)+0:(i*12*4)+4])[0]
                y = struct.unpack("f", parts[(i*12*4)+4:(i*12*4)+8])[0]
                dist_sq = (x - mx)**2 + (y-my)**2
                if dist_sq < 300.**2:
                    vx = struct.unpack("f", parts[(i*12*4)+32:(i*12*4)+36])[0]
                    vy = struct.unpack("f", parts[(i*12*4)+36:(i*12*4)+40])[0]
                    force = min(10000, 100./dist_sq)*sign
                    fx = (x-mx)*force
                    fy = (y-my)*force
                    vx += fx
                    vy += fy
                    parts[(i*12*4)+32:(i*12*4)+36] = struct.pack("f", vx)
                    parts[(i*12*4)+36:(i*12*4)+40] = struct.pack("f", vy)
            self.ssbo_part_1.write(parts)
            
        self.clear()
        self.ctx.enable(self.ctx.BLEND)

        self.ssbo_part_1.bind_to_storage_buffer(binding=0)
        self.ssbo_part_2.bind_to_storage_buffer(binding=1)
        self.ssbo_densities.bind_to_storage_buffer(binding=2)

        self.density_compute_shader.run(group_x=self.group_x, group_y=self.group_y)
        self.compute_shader.run(group_x=self.group_x, group_y=self.group_y)

        self.vao_2.render(self.program)

        self.ssbo_part_1, self.ssbo_part_2 = self.ssbo_part_2, self.ssbo_part_1
        self.vao_1, self.vao_2 = self.vao_2, self.vao_1

        self._draw_fps()

    def gen_particle_data(self):
        particles = []
        particle_count = 1000
        for i in range(particle_count):
            x = random.randrange(0, self.width)
            y = random.randrange(0, self.height)
            particles += [x, y, 20.0, 3.,
                          1.0, 1.0, 1.0, 1.0,
                          0.0, 0.0, 0.0, 0.0,
                        ]

        self.ssbo_part_1 = self.ctx.buffer(data=array('f', particles))
        self.ssbo_part_2 = self.ctx.buffer(reserve=self.ssbo_part_1.size)
        self.ssbo_densities = self.ctx.buffer(reserve=particle_count*4) # 1 float = 4 bytes

util.run(Screen())