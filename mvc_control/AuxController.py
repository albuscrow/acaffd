from mvc_model.GLObject import ACVBO
from mvc_model.aux import BSplineBody
from ac_opengl.shader.ShaderWrapper import ProgramWrap, ShaderWrap
from OpenGL.GL import *
from OpenGL.GLU import *
from pyrr.matrix44 import *

from mvc_model.plain_class import ACRect


def add_prefix(file_name: str):
    return 'ac_opengl/shader/renderer/' + file_name


class AuxController:
    def __init__(self, size: list):
        # check input
        if len(size) != 3:
            raise Exception('b spline body size number error')
        if any(i < 0 for i in size):
            raise Exception('b spline body size < 0, error')

        # init b-spline body
        self._b_spline_body = BSplineBody(*size)  # type: BSplineBody

        # init shader program
        self._program = ProgramWrap().add_shader(ShaderWrap(GL_VERTEX_SHADER, add_prefix('aux.v.glsl'))) \
            .add_shader(ShaderWrap(GL_FRAGMENT_SHADER, add_prefix('aux.f.glsl')))  # type: ProgramWrap
        # init buffer
        self._control_point_position_vbo = ACVBO(GL_ARRAY_BUFFER, -1, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._control_point_for_sample_ubo = ACVBO(GL_UNIFORM_BUFFER, 1, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._b_spline_body_info_ubo = ACVBO(GL_UNIFORM_BUFFER, 0, None, GL_STATIC_DRAW)  # type: ACVBO
        self._vao_control_point = -1  # type: int
        self._normal_control_mode = False  # type: bool
        self._pick_region = None  # type: ACRect
        self._control_points_changed = True  # type: bool
        self._direct_control_point = []  # type:  list

    def change_size(self, size):
        # check input
        if len(size) != 3:
            raise Exception('b spline body size number error')
        if any(i < 0 for i in size):
            raise Exception('b spline body size < 0, error')
        self._b_spline_body = BSplineBody(*size)  # type: BSplineBody
        self.async_upload_to_gpu()

    def gl_init(self):
        # init vao
        self._vao_control_point = glGenVertexArrays(1)
        glBindVertexArray(self._vao_control_point)
        self._control_point_position_vbo.as_array_buffer(0, 4, GL_FLOAT)
        glBindVertexArray(0)

        # upload_to_gpu
        self.async_upload_to_gpu()

    def async_upload_to_gpu(self):
        self._control_point_position_vbo.async_update(self.get_control_point_data())
        self._control_point_for_sample_ubo.async_update(self._b_spline_body.get_control_point_for_sample())
        self._b_spline_body_info_ubo.async_update(self._b_spline_body.get_info())

    def gl_sync_buffer_for_self(self):
        self._control_point_position_vbo.gl_sync()

    def gl_sync_buffer_for_previous_computer(self):
        self._b_spline_body_info_ubo.gl_sync()

    def gl_sync_buffer_for_deformation(self):
        self._control_point_for_sample_ubo.gl_sync()

    def gl_draw(self, model_view_matrix: np.array, perspective_matrix: np.array):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_PROGRAM_POINT_SIZE)
        self._program.use()
        glBindVertexArray(self._vao_control_point)
        self.gl_pick_control_point(model_view_matrix, perspective_matrix)
        self.gl_sync_buffer_for_self()
        self.gl_draw_control_points(model_view_matrix, perspective_matrix)
        glBindVertexArray(0)
        glUseProgram(0)

    def gl_draw_control_points(self, model_view_matrix, perspective_matrix):
        glUniformMatrix4fv(0, 1, GL_FALSE, multiply(model_view_matrix, perspective_matrix))
        glDrawArrays(GL_POINTS, 0, self.get_control_point_number())

    def gl_pick_control_point(self, model_view_matrix, perspective_matrix):
        if not self._pick_region:
            return
        self._b_spline_body.reset_hit_record()
        glSelectBuffer(1024)
        glRenderMode(GL_SELECT)
        glInitNames()
        glPushName(0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        w = max(10, self._pick_region.w)
        h = max(10, self._pick_region.h)
        gluPickMatrix((self._pick_region.x1 + self._pick_region.x2) / 2,
                      (self._pick_region.y1 + self._pick_region.y2) / 2,
                      w, h,
                      glGetDoublev(GL_VIEWPORT))
        glUniformMatrix4fv(0, 1, GL_FALSE, multiply(model_view_matrix,
                                                    multiply(perspective_matrix,
                                                             glGetDoublev(GL_PROJECTION_MATRIX))))
        for i in range(self._b_spline_body.get_control_point_number()):
            glLoadName(i)
            glDrawArrays(GL_POINTS, i, 1)
        hit_info = glRenderMode(GL_RENDER)
        for r in hit_info:
            for select_name in r.names:
                self._b_spline_body.hit_point(select_name)
        self._control_point_position_vbo.async_update(self.get_control_point_data())
        self._pick_region = None

    def pick_control_point(self, region: ACRect):
        self._pick_region = region

    def move_selected_control_points(self, xyz):
        self._b_spline_body.move([d / 10 for d in xyz])
        self._control_point_position_vbo.async_update(self.get_control_point_data())
        self._control_point_for_sample_ubo.async_update(self._b_spline_body.get_control_point_for_sample())
        self._control_points_changed = True

    def get_control_point_data(self):
        if self._normal_control_mode:
            return self._b_spline_body.control_points
        else:
            return np.array(self._direct_control_point, dtype='f4')

    def get_control_point_number(self):
        if self._normal_control_mode:
            return self._b_spline_body.get_control_point_number()
        else:
            return len(self._direct_control_point)

    def get_control_point_for_sample(self):
        return self._b_spline_body.get_control_point_for_sample()

    def get_cage_size(self) -> list:
        return self._b_spline_body.get_cage_size()

    def change_control_point_number(self, u, v, w):
        self._b_spline_body.change_control_point_number(u, v, w)
        self.async_upload_to_gpu()
        pass

    @property
    def b_spline_body(self):
        return self._b_spline_body

    @property
    def is_normal_control_point_mode(self):
        return self._normal_control_mode

    @is_normal_control_point_mode.setter
    def is_normal_control_point_mode(self, v):
        self._normal_control_mode = v
        self._control_point_position_vbo.async_update(self.get_control_point_data())

    def add_direct_control_point(self, intersect_point):
        if intersect_point is not None:
            self._direct_control_point = [np.append(intersect_point, 0)]
            self._control_point_position_vbo.async_update(self.get_control_point_data())

    def clear_direct_control_point(self):
        self._direct_control_point.clear()
        self._control_point_position_vbo.async_update(self.get_control_point_data())

    @property
    def normal_control_mode(self):
        return self._normal_control_mode

    def move_direct_control_point(self, direction):
        direction /= 300
        self._b_spline_body.move_dffd(self._direct_control_point[0], direction)
        target_point = np.append(self._direct_control_point[0][:3] + direction, 1)
        if len(self._direct_control_point) <= 1:
            self._direct_control_point.append(target_point)
        else:
            self._direct_control_point[1] = target_point
        self._control_point_position_vbo.async_update(self.get_control_point_data())
        self._control_point_for_sample_ubo.async_update(self._b_spline_body.get_control_point_for_sample())
        self._control_points_changed = True

    def is_direct_control_point_selected(self):
        return len(self._direct_control_point) != 0
