from mvc_model.GLObject import ACVBO
from mvc_model.aux import BSplineBody
from ac_opengl.shader.ShaderWrapper2 import ProgramWrap, ShaderWrap
from OpenGL.GL import *


def add_prefix(file_name: str):
    return 'ac_opengl/shader/renderer/' + file_name


class BSplineBodyControl:
    def __init__(self, size: list):

        # init b-spline body
        if len(size) != 3:
            raise Exception('b spline body size number error')
        if any(i < 0 for i in size):
            raise Exception('b spline body size < 0, error')
        self._b_spline_body = BSplineBody(*size)

        # init shader program
        self._program = ProgramWrap().add_shader(ShaderWrap(GL_VERTEX_SHADER, add_prefix('aux.v.glsl')).compile()) \
            .add_shader(ShaderWrap(GL_VERTEX_SHADER, add_prefix('aux.f.glsl'))) \
            .link()

        # init buffer
        self._control_point_position_vbo = ACVBO(GL_ARRAY_BUFFER, -1, None, GL_DYNAMIC_DRAW)
        self._control_point_color_vbo = ACVBO(GL_ARRAY_BUFFER, -1, None, GL_DYNAMIC_DRAW)

        # init vao
        self.b_spline_body_vao = glGenVertexArrays(1)
        glBindVertexArray(self.b_spline_body_vao)
        self._control_point_position_vbo.as_array_buffer(0, 3, GL_FLOAT)
        self._control_point_color_vbo.as_array_buffer(1, 1, GL_FLOAT)
        glBindVertexArray(0)

    def async_upload_to_gpu(self):
        self._control_point_position_vbo.async_update(self._b_spline_body.control_points)
        self._control_point_color_vbo.async_update(self._b_spline_body.is_hit)

    def gl_sync_buffer(self):
        self._control_point_position_vbo.gl_sync()
        self._control_point_color_vbo.gl_sync()

    def gl_draw(self):
        self.gl_sync_buffer()
