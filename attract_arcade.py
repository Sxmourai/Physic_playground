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
                         "Fluids", gl_version=(4, 3), resizable=True)
        self.center_window()
        self.set_fullscreen()
        self.fluid_count = 20
        self.selected = None

        self.group_x = 200
        self.group_y = 1

        self.gen_particle_data()

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
        compute_shader_source = open("fluid_compute.glsl").read().replace(
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

        self.ssbo_part_1.bind_to_storage_buffer(binding=0)
        self.ssbo_part_2.bind_to_storage_buffer(binding=1)
        # self.ssbo_spring_1.bind_to_storage_buffer(binding=2)
        # self.ssbo_spring_2.bind_to_storage_buffer(binding=3)

        self.compute_shader.run(group_x=self.group_x, group_y=self.group_y)

        self.vao_2.render(self.program)

        self.ssbo_part_1, self.ssbo_part_2 = self.ssbo_part_2, self.ssbo_part_1
        # self.ssbo_spring_1, self.ssbo_spring_2 = self.ssbo_spring_2, self.ssbo_spring_1
        self.vao_1, self.vao_2 = self.vao_2, self.vao_1

        self.perf_graph_list.draw()
        self.fps_len += 1
        if self.fps_len > 10:  # Skip 10 first values, they are not realistic
            self.fps_sum += arcade.get_fps()
            if self.fps_sum >= self.fps_close:
                raise KeyboardInterrupt
            self.fps_avg = self.fps_sum/(self.fps_len-10)

    def gen_particle_data(self):
        particles = []
        # for x in range(0, WINDOW_WIDTH, 10):
        #     for y in range(0, WINDOW_HEIGHT, 10):
        for i in range(1000):
            x = random.randrange(0, WINDOW_WIDTH)
            y = random.randrange(0, WINDOW_HEIGHT)
            particles += [x, y, 200.0, 3.,
                          1.0, 1.0, 1.0, 1.0,
                          0.0, 0.0, 0.0, 0.0,
                          ]

        self.ssbo_part_1 = self.ctx.buffer(data=array('f', particles))
        self.ssbo_part_2 = self.ctx.buffer(reserve=self.ssbo_part_1.size)

    # def on_mouse_press(self, mx: int, my: int, button: int, modifiers: int):

    # def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
    #     self.selected = None

    # def on_mouse_motion(self, mx: int, my: int, dx: int, dy: int):
    #     self.mx = mx
    #     self.my = my


app = Screen()
try:
    arcade.run()
except KeyboardInterrupt:
    print("Avg fps: ", app.fps_avg)
