import struct
import pygame
from pygame import Vector3 as vec3
from pygame import Vector2 as vec2
import random
from array import array
import math
import sys
import arcade
from arcade.gl import BufferDescription

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080


class Screen(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT,
                         "Springs", gl_version=(4, 3), resizable=True)
        self.center_window()
        self.spring_count = 20
        self.selected = None

        self.group_x = self.spring_count
        self.group_y = 1

        particles, springs = self.gen_particle_data()

        self.ssbo_part_1 = self.ctx.buffer(data=array('f', particles))
        self.ssbo_part_2 = self.ctx.buffer(reserve=self.ssbo_part_1.size)
        self.ssbo_spring_1 = self.ctx.buffer(data=array('f', springs))
        self.ssbo_spring_2 = self.ctx.buffer(reserve=self.ssbo_spring_1.size)

        self.attributes = ["in_vertex", "in_color"]
        self.buffer_format = "4f 4f 4x4"
        self.vao_1 = self.ctx.geometry(
            [BufferDescription(
                self.ssbo_part_1, self.buffer_format, self.attributes)],
            mode=self.ctx.POINTS,
        )
        self.vao_2 = self.ctx.geometry(
            [BufferDescription(
                self.ssbo_part_2, self.buffer_format, self.attributes)],
            mode=self.ctx.POINTS,
        )
        compute_shader_source = open("spring_compute.glsl").read().replace(
            "COMPUTE_SIZE_X", str(self.group_x)).replace(
            "COMPUTE_SIZE_Y", str(self.group_y)).replace(
            "WIN_WIDTH", str(WINDOW_WIDTH)).replace(
            "WIN_HEIGHT", str(WINDOW_HEIGHT))
        self.compute_shader = self.ctx.compute_shader(
            source=compute_shader_source)

        self.program = self.ctx.program(
            vertex_shader=open("vertex.glsl").read(),
            geometry_shader=open("geometry.glsl").read(),
            fragment_shader=open("fragment.glsl").read(),
        )

        arcade.enable_timings()
        self.fps_avg = 0
        self.fps_sum = 0
        self.fps_len = 0
        if len(sys.argv) == 1 or not sys.argv[1].isdecimal():
            self.fps_close = 4000000
        else:
            self.fps_close = int(sys.argv[1])

        self.perf_graph_list = arcade.SpriteList()

        graph = arcade.PerfGraph(200, 120, graph_data="FPS")
        graph.center_x = 100
        graph.center_y = self.height - 60
        self.perf_graph_list.append(graph)

    def on_draw(self):
        self.clear()
        self.ctx.enable(self.ctx.BLEND)

        if self.selected != None:
            springs = bytearray(self.ssbo_part_1.read())

            offset = self.selected * 12*4
            springs[offset+0:offset+4] = struct.pack("f", self.mx)
            springs[offset+4:offset+8] = struct.pack("f", self.my)
            springs[offset+32:offset+36] = struct.pack("f", 0)  # Reset vel
            springs[offset+36:offset+40] = struct.pack("f", 0)
            self.ssbo_part_1.write(springs)

        self.ssbo_part_1.bind_to_storage_buffer(binding=0)
        self.ssbo_part_2.bind_to_storage_buffer(binding=1)
        self.ssbo_spring_1.bind_to_storage_buffer(binding=2)
        self.ssbo_spring_2.bind_to_storage_buffer(binding=3)

        self.compute_shader.run(group_x=self.group_x, group_y=self.group_y)

        self.vao_2.render(self.program)

        self.ssbo_part_1, self.ssbo_part_2 = self.ssbo_part_2, self.ssbo_part_1
        self.ssbo_spring_1, self.ssbo_spring_2 = self.ssbo_spring_2, self.ssbo_spring_1
        self.vao_1, self.vao_2 = self.vao_2, self.vao_1

        self.perf_graph_list.draw()
        self.fps_len += 1
        if self.fps_len > 10:  # Skip 10 first values, they are not realistic
            self.fps_sum += arcade.get_fps()
            if self.fps_sum >= self.fps_close:
                raise KeyboardInterrupt
            self.fps_avg = self.fps_sum/(self.fps_len-10)

    def on_mouse_press(self, mx: int, my: int, button: int, modifiers: int):
        springs = bytearray(self.ssbo_part_1.read())

        for i in range(int(len(springs)/(12*4))):
            x = struct.unpack("f", springs[(i*12*4)+0:(i*12*4)+4])[0]
            y = struct.unpack("f", springs[(i*12*4)+4:(i*12*4)+8])[0]
            r = struct.unpack("f", springs[(i*12*4)+12:(i*12*4)+16])[0]
            if abs(mx-x) < r and abs(my-y) < r:
                self.selected = i

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        self.selected = None

    def on_mouse_motion(self, mx: int, my: int, dx: int, dy: int):
        self.mx = mx
        self.my = my

    def gen_particle_data(self):
        particles = []
        springs = []
        # for i in range(self.spring_count):
        #     s_len = 100
        #     p1x = self.width / 2 - 50*int(self.spring_count/2) + 50*i
        #     # + Is up, so we want our 1st spring to be up.
        #     p1y = self.height / 2 + s_len/2
        #     p2x = p1x
        #     p2y = self.height / 2 - s_len/2
        #     particles += [p1x, p1y, 0.0, 10.,
        #                   1.0, 1.0, 0.0, 1.0,
        #                   0.0, 0.0, 0.0, 0.0,
        #                   ]
        #     particles += [p2x, p2y, 0.0, 10.,
        #                   1.0, 0.0, 1.0, 1.0,
        #                   0.0, 0.0, 0.0, 0.0,
        #                   ]
        #     springs += [i*2, i*2+1]
        particles += [self.width/2, self.height/2, 0.0, 10.,
                        1.0, 1.0, 1.0, 1.0,
                        0.0, 0.0, 0.0, 0.0,
                        ]
        particles += [self.width/2-100, self.height/2, 0.0, 10.,
                        1.0, 0.0, 1.0, 1.0,
                        0.0, 0.0, 0.0, 0.0,
                        ]
        particles += [self.width/2, self.height/2-100, 0.0, 10.,
                        1.0, 0.0, 1.0, 1.0,
                        0.0, 0.0, 0.0, 0.0,
                        ]
        springs += [0, 1]
        # springs += [1, 2]
        
        return particles, springs


app = Screen()
try:
    arcade.run()
except KeyboardInterrupt:
    print("Avg fps: ", app.fps_avg)
