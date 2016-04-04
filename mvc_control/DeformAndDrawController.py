from Constant import *
from mvc_model.GLObject import ACVBO
from ac_opengl.shader.ShaderWrapper import ProgramWrap, ShaderWrap
from OpenGL.GL import *
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
        self.update_uniform_about_b_spline()
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

    def update_uniform_about_b_spline(self):
        glProgramUniform1ui(self._gl_program_name, 1,
                            int(self._controller.cage_size[1] * self._controller.cage_size[2]))
        glProgramUniform1ui(self._gl_program_name, 2, int(self._controller.cage_size[2]))

    def update_uniform_about_adjust_control_point_flag(self):
        glProgramUniform1i(self._gl_program_name, 6, 1 if self._controller.adjust_control_point else -1)


class ModelRendererShader(ProgramWrap):
    def __init__(self, controller):
        super().__init__()
        self._controller = controller  # type: DeformAndDrawController
        self._is_show_splited_edge_uniform = ACVBO(GL_UNIFORM_BUFFER, 0, None, GL_STATIC_DRAW)  # type: ACVBO

    def init_uniform(self):
        self.update_uniform_about_split_edge()

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
    def __init__(self, cage_size: list):
        self._splited_triangle_number = -1
        self._cage_size = cage_size  # type: list

        self._tessellation_level = -1  # type: int
        self._tessellated_point_number_pre_splited_triangle = -1  # type: int
        self._tessellated_triangle_number_pre_splited_triangle = -1  # type: int
        self._tessellation_parameter = None  # type: list
        self._tessellation_index = None  # type: list
        self._tessellation_factor_changed = False  # type: bool
        self._splited_triangle_number_changed = False  # type: bool
        self.init_tessellation_pattern_data(3)

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

        # vbo
        self._vertex_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 6, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._normal_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 7, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._index_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 8, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._parameter_in_splited_triangle_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 10, None,
                                                        GL_DYNAMIC_DRAW)  # type: ACVBO
        self._parameter_in_original_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 11, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._real_position_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 12, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._real_normal_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 13, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._model_vao = -1  # type: int

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
        # specific index buffer
        self._index_vbo.as_element_array_buffer()
        # unbind program
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

    def gl_async_update_buffer_for_self(self):
        if self._vertex_vbo is not None:
            self._vertex_vbo.capacity = self.splited_triangle_number \
                                        * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
        if self._normal_vbo is not None:
            self._normal_vbo.capacity = self.splited_triangle_number \
                                        * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE

        if self._parameter_in_splited_triangle_vbo is not None:
            self._parameter_in_splited_triangle_vbo.capacity = self.splited_triangle_number \
                                                               * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
        if self._parameter_in_original_vbo is not None:
            self._parameter_in_original_vbo.capacity = self.splited_triangle_number \
                                                       * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE

        if self._real_normal_vbo is not None:
            self._real_normal_vbo.capacity = self.splited_triangle_number \
                                             * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
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
        self._normal_vbo.gl_sync()
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
        if self._need_update_uniform_about_b_spline:
            self._deform_program.update_uniform_about_b_spline()
            self._need_update_uniform_about_b_spline = False
        if self._tessellation_factor_changed:
            self._deform_program.update_uniform_about_tessellation()
            self._tessellation_factor_changed = False
        if self._splited_triangle_number_changed:
            self._deform_program.update_uniform_triangle_number()
            self._splited_triangle_number_changed = False
        if self._need_update_adjust_control_point_flag:
            self._deform_program.update_uniform_about_adjust_control_point_flag()
            self._need_update_adjust_control_point_flag = False
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
        glBindVertexArray(self._model_vao)
        number = int(self.splited_triangle_number * self.tessellated_triangle_number_pre_splited_triangle * 3)
        glDrawElements(GL_TRIANGLES, number, GL_UNSIGNED_INT, None)
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
    def cage_size(self):
        return self._cage_size

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

    def set_adjust_control_point(self, v):
        self._adjust_control_point = v
        self._need_update_adjust_control_point_flag = True
        self._need_deform = True

    @need_deform.setter
    def need_deform(self, value):
        self._need_deform = value

    @cage_size.setter
    def cage_size(self, value):
        self._cage_size = value
        self._need_update_uniform_about_b_spline = True

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
