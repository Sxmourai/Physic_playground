from array import array
import random
import util
from arcade.experimental import shadertoy

class Screen(util.Simulation):
    def __init__(self):
        self._setup("Raycast", buffer_format="3f", attributes=["aPos",])
        # self.program = self.ctx.program(vertex_shader=open("vertex_raycast.glsl").read(),fragment_shader=open("frag_raycast.glsl").read())
        # self._vaos(self.ssbo_1, self.ssbo_2, mode=self.ctx.TRIANGLES)
        
        # self.compute_shader = self._compute_shader("raycast")
        self.shader = shadertoy.Shadertoy((self.width, self.height), open("raycast.glsl").read())

    def on_draw(self):
        self.shader.render()
        # self.clear()
        # self.ctx.enable(self.ctx.BLEND)

        # self.ssbo_1.bind_to_storage_buffer(binding=0)
        # self.ssbo_2.bind_to_storage_buffer(binding=1)

        # self.vao_2.render(self.program)

        # self.ssbo_1, self.ssbo_2 = self.ssbo_2, self.ssbo_1
        # self.vao_1, self.vao_2 = self.vao_2, self.vao_1

        self._draw_fps()

    def gen_particle_data(self):
        vertices = []
        vertices += [
            -1.0, -1.0, 0.0,
            1.0, -1., 0.0,
            -1.0, 1., 0.0,
        ]

        self.ssbo_1 = self.ctx.buffer(data=array('f', vertices))
        self.ssbo_2 = self.ctx.buffer(reserve=self.ssbo_1.size)

util.run(Screen())
