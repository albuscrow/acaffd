from functools import reduce

from math import sqrt, acos, pi

from PIL import Image

from Constant import *
from mvc_control.PreviousComputeControllerGPU import PreviousComputeControllerGPU
from mvc_model.GLObject import ACVBO
from ac_opengl.shader.ShaderWrapper import ProgramWrap, ShaderWrap
from OpenGL.GL import *
from OpenGL.GLU import *
from pyrr.matrix44 import *


def add_compute_prefix(file_name: str):
    return 'ac_opengl/shader/compute/' + file_name


def add_renderer_prefix(file_name: str):
    return 'ac_opengl/shader/renderer/' + file_name


class DeformComputeShader(ProgramWrap):
    def __init__(self, controller):
        super().__init__()
        self._controller = controller  # type: DeformAndDrawController
        self._tessellation_parameter = ACVBO(GL_UNIFORM_BUFFER, 2, None, GL_STATIC_DRAW)  # type: ACVBO
        self._tessellation_indexes = ACVBO(GL_UNIFORM_BUFFER, 3, None, GL_STATIC_DRAW)  # type: ACVBO

    def init_uniform(self):
        self.update_uniform_triangle_number()
        self.update_uniform_about_tessellation()
        self.update_uniform_about_adjust_control_point_flag()

    def update_uniform_triangle_number(self):
        glProgramUniform1ui(self._gl_program_name, 0, int(self._controller.splited_triangle_number))

    def update_uniform_about_tessellation(self):
        glProgramUniform1ui(self._gl_program_name, 4,
                            int(self._controller.tessellated_point_number_pre_splited_triangle))
        glProgramUniform1ui(self._gl_program_name, 5,
                            int(self._controller.tessellated_triangle_number_pre_splited_triangle))
        self._tessellation_parameter.async_update(self._controller.tessellation_parameter)
        self._tessellation_parameter.gl_sync()
        self._tessellation_indexes.async_update(self._controller.tessellation_index)
        self._tessellation_indexes.gl_sync()

    def update_uniform_about_adjust_control_point_flag(self):
        glProgramUniform1i(self._gl_program_name, 6, 1 if self._controller.adjust_control_point else -1)

    def update_uniform_about_use_pn_triangle(self):
        glProgramUniform1i(self._gl_program_name, 1, 1 if self._controller.use_pn_normal_for_renderer else -1)


class ModelRendererShader(ProgramWrap):
    def __init__(self, controller):
        super().__init__()
        self._controller = controller  # type: DeformAndDrawController
        self._is_show_splited_edge_uniform = ACVBO(GL_UNIFORM_BUFFER, 0, None, GL_STATIC_DRAW)  # type: ACVBO

    def init_uniform(self):
        self.update_uniform_about_split_edge()
        glProgramUniform1i(self._gl_program_name, 8, 1 if self._controller.has_texture else -1)

    def update_uniform_about_show_original(self):
        glProgramUniform1i(self._gl_program_name, 9, 1 if self._controller.show_original else -1)

    def update_uniform_about_split_edge(self):
        glProgramUniform1i(self._gl_program_name, 3, 1 if self._controller.splited_edge_visibility else -1)

    def update_uniform_about_triangle_quality(self):
        glProgramUniform1i(self._gl_program_name, 4, 1 if self._controller.show_quality else -1)

    def update_uniform_about_normal_diff(self):
        glProgramUniform1i(self._gl_program_name, 5, 1 if self._controller.show_normal_diff else -1)

    def update_uniform_about_position_diff(self):
        glProgramUniform1i(self._gl_program_name, 6, 1 if self._controller.show_position_diff else -1)

    def update_uniform_about_real(self):
        glProgramUniform1i(self._gl_program_name, 7, 1 if self._controller.show_real else -1)


class DeformAndDrawController:
    def __init__(self, has_texture, previous_controller, controller=None):
        self._previous_controller = previous_controller  # type: PreviousComputeControllerGPU
        self._controller = controller
        self._splited_triangle_number = -1

        self._tessellation_level = -1  # type: int
        self._tessellated_point_number_pre_splited_triangle = -1  # type: int
        self._tessellated_triangle_number_pre_splited_triangle = -1  # type: int
        self._tessellation_parameter = None  # type: list
        self._tessellation_index = None  # type: list
        self._tessellation_factor_changed = False  # type: bool
        self._splited_triangle_number_changed = False  # type: bool
        self.init_tessellation_pattern_data(1)

        self._need_deform = True  # type: bool
        self._need_update_uniform_about_b_spline = False

        self._need_update_show_splited_edge_flag = True
        self._splited_edge_visibility = False

        self._need_update_triangle_quality_flag = True
        self._show_quality = False

        self._need_update_normal_diff_flag = True
        self._show_normal_diff = False

        self._need_update_position_diff_flag = True
        self._show_position_diff = False

        self._need_update_adjust_control_point_flag = True
        self._adjust_control_point = True

        self._show_control_point = False

        self._show_normal = False

        self._need_update_show_real_flag = True
        self._show_real = False

        self._need_comparison = False

        self._need_update_show_original = True
        self._show_original = False

        self._need_update_use_pn_normal_for_renderer = True
        self._use_pn_normal_for_renderer = False

        # vbo
        self._vertex_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 6, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._parameter_in_BSpline_body_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 21, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._normal_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 7, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._tex_coord_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 23, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._index_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 8, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._parameter_in_splited_triangle_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 10, None,
                                                        GL_DYNAMIC_DRAW)  # type: ACVBO
        self._parameter_in_original_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 11, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._real_position_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 12, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._real_normal_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 13, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._model_vao = -1  # type: int
        self._original_model_vao = -1  # type: int

        self._control_point_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 15, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._control_point_index_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 16, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._control_point_vao = -1  # type: int

        self._show_normal_position_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 17, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._show_normal_normal_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 18, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._show_normal_vao = -1  # type: int

        # program
        self._deform_program = DeformComputeShader(self) \
            .add_shader(ShaderWrap(GL_COMPUTE_SHADER, add_compute_prefix('deform_compute_shader_oo.glsl')))

        self._renderer_program = ModelRendererShader(self) \
            .add_shader(ShaderWrap(GL_VERTEX_SHADER, add_renderer_prefix('vertex.glsl'))) \
            .add_shader(ShaderWrap(GL_FRAGMENT_SHADER, add_renderer_prefix('fragment.glsl')))  # type: ProgramWrap

        self._renderer_control_point_program = ProgramWrap() \
            .add_shader(ShaderWrap(GL_VERTEX_SHADER, add_renderer_prefix('control_points.v.glsl'))) \
            .add_shader(
            ShaderWrap(GL_FRAGMENT_SHADER, add_renderer_prefix('control_points.f.glsl')))  # type: ProgramWrap

        self._renderer_normal_program = ProgramWrap() \
            .add_shader(ShaderWrap(GL_VERTEX_SHADER, add_renderer_prefix('normal.v.glsl'))) \
            .add_shader(ShaderWrap(GL_FRAGMENT_SHADER, add_renderer_prefix('normal.f.glsl'))) \
            .add_shader(ShaderWrap(GL_GEOMETRY_SHADER, add_renderer_prefix('normal.g.glsl')))  # type: ProgramWrap

        self._has_texture = has_texture

    def gl_init(self):
        self._model_vao = glGenVertexArrays(1)
        glBindVertexArray(self._model_vao)
        # set vertice attribute
        self._vertex_vbo.as_array_buffer(0, 4, GL_FLOAT)
        # set normal attribute
        self._normal_vbo.as_array_buffer(1, 4, GL_FLOAT)
        # set tessellate parameter attribute
        self._parameter_in_splited_triangle_vbo.as_array_buffer(2, 4, GL_FLOAT)
        # set split parameter attribute
        self._parameter_in_original_vbo.as_array_buffer(3, 4, GL_FLOAT)
        self._real_normal_vbo.as_array_buffer(4, 4, GL_FLOAT)
        self._real_position_vbo.as_array_buffer(5, 4, GL_FLOAT)
        self._tex_coord_vbo.as_array_buffer(6, 2, GL_FLOAT)
        # specific index buffer
        self._index_vbo.as_element_array_buffer()
        # unbind program
        glBindVertexArray(0)

        self._original_model_vao = glGenVertexArrays(1)  # type: int
        glBindVertexArray(self._original_model_vao)
        self._previous_controller.original_vertex_ssbo.as_array_buffer(0, 4, GL_FLOAT)
        self._previous_controller.original_normal_ssbo.as_array_buffer(1, 4, GL_FLOAT)
        self._previous_controller.original_tex_coord_ssbo.as_array_buffer(6, 2, GL_FLOAT)
        self._previous_controller.original_index_ssbo.as_element_array_buffer()
        glBindVertexArray(0)

        self._control_point_vao = glGenVertexArrays(1)
        glBindVertexArray(self._control_point_vao)
        self._control_point_vbo.as_array_buffer(0, 4, GL_FLOAT)
        self._control_point_index_vbo.as_element_array_buffer()
        glBindVertexArray(0)

        self._show_normal_vao = glGenVertexArrays(1)
        glBindVertexArray(self._show_normal_vao)
        self._show_normal_position_vbo.as_array_buffer(0, 4, GL_FLOAT)
        self._show_normal_normal_vbo.as_array_buffer(1, 4, GL_FLOAT)
        glBindVertexArray(0)

        self.gl_async_update_buffer_for_self()

        # init for texture
        texture_name = glGenTextures(1)

        glActiveTexture(GL_TEXTURE1)
        glEnable(GL_TEXTURE_2D)

        # "Bind" the newly created texture : all future texture functions will modify this texture
        glBindTexture(GL_TEXTURE_2D, texture_name)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        image = DeformAndDrawController.load_texture_data('res/3d_model/test1024.png')
        # Give the image to OpenGL
        image_data = np.array(list(image.getdata()), dtype=np.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.size[0], image.size[1],
                     0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glActiveTexture(GL_TEXTURE0)

    @staticmethod
    def load_texture_data(filename):
        return Image.open(filename)

    def gl_async_update_buffer_for_self(self):
        if self._vertex_vbo is not None:
            self._vertex_vbo.capacity = self.splited_triangle_number \
                                        * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
        if self._parameter_in_BSpline_body_vbo is not None:
            self._parameter_in_BSpline_body_vbo.capacity = self.splited_triangle_number \
                                                           * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
        if self._normal_vbo is not None:
            self._normal_vbo.capacity = self.splited_triangle_number \
                                        * self.tessellated_point_number_pre_splited_triangle * NORMAL_SIZE

        if self._tex_coord_vbo is not None:
            self._tex_coord_vbo.capacity = self.splited_triangle_number \
                                           * self.tessellated_point_number_pre_splited_triangle * TEX_COORD_SIZE

        if self._parameter_in_splited_triangle_vbo is not None:
            self._parameter_in_splited_triangle_vbo.capacity = self.splited_triangle_number \
                                                               * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
        if self._parameter_in_original_vbo is not None:
            self._parameter_in_original_vbo.capacity = self.splited_triangle_number \
                                                       * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE

        if self._real_normal_vbo is not None:
            self._real_normal_vbo.capacity = self.splited_triangle_number \
                                             * self.tessellated_point_number_pre_splited_triangle * NORMAL_SIZE
        if self._real_position_vbo is not None:
            self._real_position_vbo.capacity = self.splited_triangle_number \
                                               * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
        if self._index_vbo is not None:
            self._index_vbo.capacity = self.splited_triangle_number \
                                       * self.tessellated_triangle_number_pre_splited_triangle * PER_TRIANGLE_INDEX_SIZE

        if self._control_point_vbo is not None:
            self._control_point_vbo.capacity = self.splited_triangle_number * CONTROL_POINT_NUMBER * VERTEX_SIZE

        if self._control_point_index_vbo is not None:
            self._control_point_index_vbo.capacity = self.splited_triangle_number * CONTROL_POINT_TRIANGLE_NUMBER * PER_TRIANGLE_INDEX_SIZE

        if self._show_normal_position_vbo is not None:
            self._show_normal_position_vbo.capacity = self.splited_triangle_number * SHOW_NORMAL_POINT_NUMBER_PER_TRIANGLE * VERTEX_SIZE

        if self._show_normal_normal_vbo is not None:
            self._show_normal_normal_vbo.capacity = self.splited_triangle_number * SHOW_NORMAL_POINT_NUMBER_PER_TRIANGLE * NORMAL_SIZE

    def gl_sync_buffer(self):
        self._vertex_vbo.gl_sync()
        self._parameter_in_BSpline_body_vbo.gl_sync()
        self._normal_vbo.gl_sync()
        self._tex_coord_vbo.gl_sync()
        self._parameter_in_splited_triangle_vbo.gl_sync()
        self._parameter_in_original_vbo.gl_sync()
        self._real_normal_vbo.gl_sync()
        self._real_position_vbo.gl_sync()
        self._index_vbo.gl_sync()
        self._control_point_vbo.gl_sync()
        self._control_point_index_vbo.gl_sync()
        self._show_normal_position_vbo.gl_sync()
        self._show_normal_normal_vbo.gl_sync()

    def gl_deform(self, operator):
        if not self.need_deform:
            return
        operator()
        self._deform_program.use()
        if self._tessellation_factor_changed:
            self._deform_program.update_uniform_about_tessellation()
            self._tessellation_factor_changed = False
        if self._splited_triangle_number_changed:
            self._deform_program.update_uniform_triangle_number()
            self._splited_triangle_number_changed = False
        if self._need_update_adjust_control_point_flag:
            self._deform_program.update_uniform_about_adjust_control_point_flag()
            self._need_update_adjust_control_point_flag = False
        if self._need_update_use_pn_normal_for_renderer:
            self._deform_program.update_uniform_about_use_pn_triangle()
            self._need_update_use_pn_normal_for_renderer = False

        glDispatchCompute(*self.group_size)
        self._need_deform = False
        glUseProgram(0)

    def gl_renderer(self, model_view_matrix: np.array, perspective_matrix: np.array, operator):
        self.gl_sync_buffer()
        self.gl_deform(operator)
        self._renderer_program.use()
        if self._need_update_show_splited_edge_flag:
            self._renderer_program.update_uniform_about_split_edge()
            self._need_update_show_splited_edge_flag = False

        if self._need_update_show_original:
            self._renderer_program.update_uniform_about_show_original()
            self._need_update_show_original = False

        if self._need_update_triangle_quality_flag:
            self._renderer_program.update_uniform_about_triangle_quality()
            self._need_update_triangle_quality_flag = False

        if self._need_update_normal_diff_flag:
            self._renderer_program.update_uniform_about_normal_diff()
            self._need_update_normal_diff_flag = False

        if self._need_update_position_diff_flag:
            self._renderer_program.update_uniform_about_position_diff()
            self._need_update_position_diff_flag = False

        if self._need_update_show_real_flag:
            self._renderer_program.update_uniform_about_real()
            self._need_update_show_real_flag = False

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # common bind
        wvp_matrix = multiply(model_view_matrix, perspective_matrix)
        glUniformMatrix4fv(0, 1, GL_FALSE, wvp_matrix)
        glUniformMatrix4fv(1, 1, GL_FALSE, model_view_matrix)

        glActiveTexture(GL_TEXTURE1)
        if self._show_original:
            glBindVertexArray(self._original_model_vao)
        else:
            glBindVertexArray(self._model_vao)
        number = int(self.splited_triangle_number * self.tessellated_triangle_number_pre_splited_triangle * 3)
        glDrawElements(GL_TRIANGLES, number, GL_UNSIGNED_INT, None)
        glActiveTexture(GL_TEXTURE0)
        glBindVertexArray(0)
        glUseProgram(0)

        if self._show_control_point:
            glBindVertexArray(self._control_point_vao)
            self._renderer_control_point_program.use()
            glUniformMatrix4fv(0, 1, GL_FALSE, wvp_matrix)
            number = int(self.splited_triangle_number * CONTROL_POINT_TRIANGLE_NUMBER * 3)
            glDrawElements(GL_TRIANGLES, number, GL_UNSIGNED_INT, None)
            glBindVertexArray(0)
            glUseProgram(0)

        if self._show_normal:
            glBindVertexArray(self._show_normal_vao)
            self._renderer_normal_program.use()
            glUniformMatrix4fv(0, 1, GL_FALSE, wvp_matrix)
            glUniformMatrix4fv(1, 1, GL_FALSE, model_view_matrix)
            number = int(self.splited_triangle_number * 3)
            glDrawArrays(GL_TRIANGLES, 0, number)
            glUseProgram(0)
            glBindVertexArray(0)

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)
        if self._vertex_vbo.capacity == 0:
            return
        self.comparison()

    @property
    def splited_triangle_number(self):
        return self._splited_triangle_number

    def set_number_and_need_deform(self, number: int, need_deform: bool):
        self._need_deform = (self._need_deform or need_deform or number != self._splited_triangle_number)
        if number != self._splited_triangle_number:
            self._splited_triangle_number = number
            self.gl_async_update_buffer_for_self()
            self._splited_triangle_number_changed = True

    @property
    def splited_triangle_number_changed(self):
        return self._splited_triangle_number_changed

    @property
    def group_size(self):
        return [int(self.splited_triangle_number / 512 + 1), 1, 1]

    @property
    def tessellation_level(self):
        return self._tessellation_level

    def init_tessellation_pattern_data(self, tessellation_level):
        self._tessellation_level = tessellation_level
        self._tessellated_point_number_pre_splited_triangle = (tessellation_level + 1) * (tessellation_level + 2) / 2
        self._tessellated_triangle_number_pre_splited_triangle = tessellation_level * tessellation_level
        self._tessellation_parameter = []  # type: list
        u = self._tessellation_level
        for i in range(self._tessellation_level + 1):
            v = self._tessellation_level - u
            for j in range(i + 1):
                self._tessellation_parameter.append([u / self._tessellation_level, v / self._tessellation_level,
                                                     (self._tessellation_level - u - v) / self._tessellation_level, 0])
                v -= 1
            u -= 1

        self._tessellation_index = []  # type: list
        for i in range(self._tessellation_level):
            start = int((i + 1) * (i + 2) / 2)
            prev = [start, start + 1, start - 1 - i]
            self._tessellation_index.append(prev)
            for j in range(i * 2):
                next_index = [prev[2], prev[2] + 1, prev[1]]
                if j % 2 == 0:
                    self._tessellation_index.append([next_index[1], next_index[0], next_index[2]])
                else:
                    self._tessellation_index.append(next_index)
                prev = next_index
        self._tessellation_index = [x + [0] for x in self._tessellation_index]
        self._tessellation_factor_changed = True

    @property
    def tessellated_point_number_pre_splited_triangle(self):
        return self._tessellated_point_number_pre_splited_triangle

    @property
    def tessellated_triangle_number_pre_splited_triangle(self):
        return self._tessellated_triangle_number_pre_splited_triangle

    @property
    def tessellation_parameter(self):
        return np.array(self._tessellation_parameter, dtype=np.float32)

    @property
    def tessellation_index(self):
        return np.array(self._tessellation_index, dtype=np.uint32)

    @property
    def need_deform(self):
        return self._need_deform

    @property
    def splited_edge_visibility(self):
        return self._splited_edge_visibility

    @property
    def show_quality(self):
        return self._show_quality

    @property
    def show_normal_diff(self):
        return self._show_normal_diff

    @property
    def show_position_diff(self):
        return self._show_position_diff

    @property
    def adjust_control_point(self):
        return self._adjust_control_point

    def set_show_normal_diff(self, v):
        self._show_normal_diff = v
        self._need_update_normal_diff_flag = True

    def set_show_position_diff(self, v):
        self._show_position_diff = v
        self._need_update_position_diff_flag = True

    def set_splited_edge_visibility(self, v):
        self._splited_edge_visibility = v
        self._need_update_show_splited_edge_flag = True

    def set_show_triangle_quality(self, v):
        self._show_quality = v
        self._need_update_triangle_quality_flag = True

    def set_show_real(self, is_show):
        self._show_real = is_show
        self._need_update_show_real_flag = True

    def set_show_original(self, is_show):
        self._show_original = is_show
        self._need_update_show_original = True

    def set_adjust_control_point(self, v):
        self._adjust_control_point = v
        self._need_update_adjust_control_point_flag = True
        self._need_deform = True

    @need_deform.setter
    def need_deform(self, value):
        self._need_deform = value

    def set_tessellation_factor(self, tessellation_factor):
        self.init_tessellation_pattern_data(tessellation_factor)
        self.gl_async_update_buffer_for_self()
        self._need_deform = True

    @property
    def show_control_point(self):
        return self._show_control_point

    @show_control_point.setter
    def show_control_point(self, is_show):
        self._show_control_point = is_show

    @property
    def show_normal(self):
        return self._show_normal

    @show_normal.setter
    def show_normal(self, is_show):
        self._show_normal = is_show

    @property
    def show_real(self):
        return self._show_real

    def set_need_comparison(self):
        self._need_comparison = True

    @staticmethod
    def comparison_helper(vbo1: ACVBO, vbo2: ACVBO, fun):
        point_number = int(vbo1.capacity / 16)
        acc = 0
        max_e = -1
        es = []
        for i, j in zip(vbo1.get_value(ctypes.c_float, (point_number, 4)),
                        vbo2.get_value(ctypes.c_float, (point_number, 4))):
            e = fun(i, j)
            max_e = max(e, max_e)
            acc += e
            es.append(e)

        average = acc / point_number
        acc = 0
        for e in es:
            acc += ((e - average) ** 2)
        standard_deviation = (acc / point_number) ** 0.5
        return average, max_e, standard_deviation

    def comparison(self):
        if not self._need_comparison:
            return
        self._need_comparison = False

        dr1 = DeformAndDrawController.comparison_helper(self._vertex_vbo, self._real_position_vbo,
                                                        lambda i, j: sqrt(
                                                            reduce(lambda p, x: p + x, [e * e for e in (i - j)[:3]],
                                                                   0)))

        def fun(i, j):
            cos_value = np.dot(i[:3], j[:3])
            if cos_value > 1:
                cos_value = 1
            elif cos_value < -1:
                cos_value = -1
            return acos(cos_value) / pi * 180

        dr2 = DeformAndDrawController.comparison_helper(self._normal_vbo, self._real_normal_vbo, fun)
        self._controller.add_diff_result((dr1, dr2))

    @property
    def has_texture(self):
        return self._has_texture

    @property
    def show_original(self):
        return self._show_original

    @property
    def use_pn_normal_for_renderer(self):
        return self._use_pn_normal_for_renderer

    @use_pn_normal_for_renderer.setter
    def use_pn_normal_for_renderer(self, use):
        self._use_pn_normal_for_renderer = use
        self._need_update_use_pn_normal_for_renderer = True
        self._need_deform = True
