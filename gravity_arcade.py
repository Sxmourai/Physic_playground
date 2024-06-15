"""
Compute shader with buffers
"""
import random
from array import array

import math
import sys
import arcade
from arcade.gl import BufferDescription

# Window dimensions
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

# Size of performance graphs
GRAPH_WIDTH = 200
GRAPH_HEIGHT = 120
GRAPH_MARGIN = 5

GRID_ROWS = 19
GRID_COLS = 10

class MyWindow(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT,
                         "Compute Shader",
                         gl_version=(4, 3),
                         resizable=True)
        self.center_window()
        self.particle_count = 2
        
        self.group_x = max(10, int(math.sqrt(self.particle_count)))
        self.group_y = 1

        # Create data buffers for the compute shader
        # We ping-pong render between these two buffers
        # ssbo = shader storage buffer object
        grids, self.particles = self.gen_particle_data(self.particle_count)
        
        self.ssbo_1 = self.ctx.buffer(data=array('f', self.particles))
        self.ssbo_2 = self.ctx.buffer(reserve=self.ssbo_1.size)
        # self.ssbo_grids_1 = self.ctx.buffer(data=array('f', grids))
        # self.ssbo_grids_2 = self.ctx.buffer(reserve=self.ssbo_grids_1.size)

        # Attribute variable names for the vertex shader
        self.attributes = ["in_vertex", "in_color"]
        # Format of the buffer data.
        # 4f = position and size -> x, y, z, radius
        # 4f = color -> rgba
        # 4x4 = Four floats used for calculating velocity. Not needed for visualization. and mass
        self.buffer_format = Particle.FORMAT
        self.vao_1 = self.ctx.geometry(
            [BufferDescription(self.ssbo_1, self.buffer_format, self.attributes)],
            mode=self.ctx.POINTS,
        )
        self.vao_2 = self.ctx.geometry(
            [BufferDescription(self.ssbo_2, self.buffer_format, self.attributes)],
            mode=self.ctx.POINTS,
        )
        compute_shader_source = open("gravity_compute.glsl").read().replace(
            "COMPUTE_SIZE_X", str(self.group_x)).replace(
            "COMPUTE_SIZE_Y", str(self.group_y)).replace(
            "WIN_WIDTH", str(WINDOW_WIDTH)).replace(
            "WIN_HEIGHT", str(WINDOW_HEIGHT)).replace(
            "GRID_ROWS", str(GRID_ROWS)).replace(
            "GRID_COLS", str(GRID_COLS))
        self.compute_shader = self.ctx.compute_shader(source=compute_shader_source)

        self.program = self.ctx.program(
            vertex_shader=open("vertex.glsl").read(),
            geometry_shader=open("geometry.glsl").read(),
            fragment_shader=open("fragment.glsl").read(),
        )

        # --- Create FPS graph
        # Enable timings for the performance graph
        arcade.enable_timings()
        self.fps_avg = 0
        self.fps_sum = 0
        self.fps_len = 0
        if len(sys.argv) == 1 or not sys.argv[1].isdecimal():
            self.fps_close = 4000000
        else:
            self.fps_close = int(sys.argv[1])

        # Create a sprite list to put the performance graph into
        self.perf_graph_list = arcade.SpriteList()

        # Create the FPS performance graph
        graph = arcade.PerfGraph(GRAPH_WIDTH, GRAPH_HEIGHT, graph_data="FPS")
        graph.center_x = GRAPH_WIDTH / 2
        graph.center_y = self.height - GRAPH_HEIGHT / 2
        self.perf_graph_list.append(graph)

    def on_draw(self):
        self.clear()
        # Enable blending so our alpha channel works
        self.ctx.enable(self.ctx.BLEND)

        # Bind buffers
        self.ssbo_1.bind_to_storage_buffer(binding=0)
        self.ssbo_2.bind_to_storage_buffer(binding=1)
        # self.ssbo_grids_1.bind_to_storage_buffer(binding=2)
        # self.ssbo_grids_2.bind_to_storage_buffer(binding=3)

        # Set input variables for compute shader
        # These are examples, although this example doesn't use them
        # self.compute_shader["screen_size"] = self.get_size()
        # self.compute_shader["force"] = force
        # self.compute_shader["frame_time"] = self.run_time

        self.compute_shader.run(group_x=self.group_x, group_y=self.group_y)

        self.vao_2.render(self.program)

        # Swap the buffers around (we are ping-ping rendering between two buffers)
        self.ssbo_1, self.ssbo_2 = self.ssbo_2, self.ssbo_1
        # self.ssbo_grids_1, self.ssbo_grids_2 = self.ssbo_grids_2, self.ssbo_grids_1
        # Swap what geometry we draw
        self.vao_1, self.vao_2 = self.vao_2, self.vao_1

        self.perf_graph_list.draw()
        self.fps_len += 1
        if self.fps_len > 10:  # Skip 10 first values, they are not realistic
            self.fps_sum += arcade.get_fps()
            if self.fps_sum >= self.fps_close:
                raise KeyboardInterrupt
            self.fps_avg = self.fps_sum/(self.fps_len-10)
    def on_mouse_press(self, x,y, button, key_modifs):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            charge = -1
        else:
            charge = 1
        # charge = random.randint(0,1)*2-1
        radius = random.randrange(2.0, 5.)
        
        if charge == 1: # Positive
            r = 1.0
            g = 0.0
            b = 0.0
        else: # Negative
            r = 0.0
            g = 0.0
            b = 1.0
        a = 1.0  # alpha / opacity
        vx,vy = 0,0
        ele_id = float(random.randint(0, 62))
        
        self.ssbo_1 = self.ctx.buffer(data=array('f', self.ssbo_1.read() + array("f", Particle(vec2(x,y), vec2(vx,vy), vec3(r,g,b),a, 0.0, radius, charge).to_floats())))
        self.ssbo_2 = self.ctx.buffer(reserve=self.ssbo_1.size)

        self.vao_1 = self.ctx.geometry(
            [BufferDescription(self.ssbo_1, self.buffer_format, self.attributes)],
            mode=self.ctx.POINTS,
        )
        self.vao_2 = self.ctx.geometry(
            [BufferDescription(self.ssbo_2, self.buffer_format, self.attributes)],
            mode=self.ctx.POINTS,
        )


    def gen_particle_data(self, particle_count):
        g_w = int(self.width/GRID_ROWS)
        g_h = int(self.height/GRID_COLS)
        particles_per_grid = int(particle_count/(GRID_ROWS*GRID_COLS))
        grids = []
        particles = []

        # for ix in range(GRID_ROWS):
        #     for iy in range(GRID_COLS):
        #         grid = []
        #         x = g_w*ix
        #         y = g_h*iy
        #         for j in range(particles_per_grid): # TODO Currently rounding the value, so we don't get the real amount of particles per grid, we would need to add them more nicely
                    # px = random.randrange(x, x+g_w) # Generate particle in grid
                    # py = random.randrange(y, y+g_h)
        for j in range(particle_count):
            px = random.randrange(20, self.width-20)
            py = random.randrange(20, self.height-20)
            charge = random.randint(0,1)*2-1
            radius = random.randrange(20.0, 50.)
            
            if charge == 1: # Positive
                r = 1.0
                g = 0.0
                b = 0.0
            else: # Negative
                r = 0.0
                g = 0.0
                b = 1.0
            a = 1.0  # alpha / opacity
            vx,vy = 0,0
            ele_id = float(random.randint(0, 62))
            particle = Particle(vec2(px,py), vec2(vx,vy), vec3(r,g,b),a, 0.0, radius, charge)
            particles += particle.to_floats()
                
                # grids += [particles_per_grid,]+grid # particles_per_grid is the mass of the whole grid

        return grids, particles

import pygame
from pygame import Vector2 as vec2
from pygame import Vector3 as vec3
class Particle:
    # Pos,Charge,Mass Color Vel,Acc, Other
    FORMAT = "4f 4f 4x4 4x4"
    def __init__(self, pos: vec2, vel: vec2, color: vec3, alpha: float, mass: float, radius: float, charge: float):
        self.pos = pos
        self.vel = vel
        self.mass = mass
        self.radius = radius
        self.charge = charge
        self.color = color,alpha
        self.acc = vec2(0.0, 0.0)
    def to_floats(self) -> list[float]:
        return [self.pos.x, self.pos.y, self.charge, self.radius, 
                self.color[0].x, self.color[0].y, self.color[0].z, self.color[1], 
                self.vel.x, self.vel.y, self.acc.x, self.acc.y,
                self.mass,0.,0.,0.,]

app = MyWindow()
try:
    arcade.run()
except KeyboardInterrupt:
    print("Avg fps: ", app.fps_avg)



                    # yield x
                    # yield y
                    # yield float(charge)  # charge
                    # yield 5.0  # radius

                    # Color
                    # yield x/self.width  # r
                    # yield y/self.height  # g
                    # yield math.sqrt((self.width/2-x)**2+(self.height/2-y)**2)/800  # b

                    # Velocity
                    # yield 0.0
                    # yield 0.0
                    # yield   # Particle element, which is parsed in compute shader, which we translate to get mass, charge, and other values (spin etc)
                    # yield 0.0  # vw (padding)
                    