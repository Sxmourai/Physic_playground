from arcade.gl import BufferDescription
import arcade
import sys

class Simulation(arcade.Window):
    def _setup(self, name: str="Simulation", sw=1920, sh=1080, group_x=200, attributes=["in_vertex", "in_color"], buffer_format="4f 4f 4x4", fragment_shader="fragment.glsl",vertex_shader="vertex.glsl",geometry_shader="geometry.glsl",compute_shader=True):
        super().__init__(sw, sh,
                            name, gl_version=(4, 3), resizable=True)
        self.center_window()
        if self.width == 1920 and self.height == 1080:
            self.set_fullscreen()
        
        if compute_shader:
            self.group_x = group_x
            self.group_y = 1
        
            self.gen_particle_data()

        self.attributes = attributes
        self.buffer_format = buffer_format
        
        self.program = self.ctx.program(
            vertex_shader=open(vertex_shader).read(),
            geometry_shader=open(geometry_shader).read(),
            fragment_shader=open(fragment_shader).read(),
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

    def _vaos(self, ssbo1, ssbo2, mode=None):
        if mode == None:
            mode = self.ctx.POINTS
        self.vao_1 = self.ctx.geometry(
            [BufferDescription(
                ssbo1, self.buffer_format, self.attributes)],
            mode=mode,
        )
        self.vao_2 = self.ctx.geometry(
            [BufferDescription(
                ssbo2, self.buffer_format, self.attributes)],
            mode=mode,
        )
        

    def _compute_shader(self, filename):
        compute_shader_source = open(f"{filename}_compute.glsl").read().replace(
            "COMPUTE_SIZE_X", str(self.group_x)).replace(
            "COMPUTE_SIZE_Y", str(self.group_y)).replace(
            "WIN_WIDTH", str(self.width)).replace(
            "WIN_HEIGHT", str(self.height))
        return self.ctx.compute_shader(source=compute_shader_source)
    
    def _draw_fps(self):
        self.perf_graph_list.draw()
        self.fps_len += 1
        if self.fps_len > 10:  # Skip 10 first values, they are not realistic
            self.fps_sum += arcade.get_fps()
            if self.fps_sum >= self.fps_close:
                raise KeyboardInterrupt
            self.fps_avg = self.fps_sum/(self.fps_len-10)
            


def run(sim: Simulation):
    try:
        arcade.run()
    except KeyboardInterrupt:
        print(f"~{round(sim.fps_avg,2)}fps")
