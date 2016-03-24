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
        glProgramUniform3f(self._gl_program_name, 3, 1 / self._controller.cage_size[0],
                           1 / self._controller.cage_size[1],
                           1 / self._controller.cage_size[2])


class DeformAndDrawController:
    def __init__(self, triangle_number: int, cage_size: list):
        self._splited_triangle_number = triangle_number
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

        # vbo
        self._vertex_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 6, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._normal_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 7, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._index_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 8, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self.parameter_in_splited_triangle_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 9, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self.parameter_in_original_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 10, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._model_vao = -1  # type: int

        # program
        self._deform_program = DeformComputeShader(self) \
            .add_shader(ShaderWrap(GL_COMPUTE_SHADER, add_compute_prefix('deform_compute_shader_oo.glsl')))

        self._renderer_program = ProgramWrap() \
            .add_shader(ShaderWrap(GL_VERTEX_SHADER, add_renderer_prefix('vertex.glsl'))) \
            .add_shader(ShaderWrap(GL_FRAGMENT_SHADER, add_renderer_prefix('fragment.glsl')))  # type: ProgramWrap

    def gl_init(self):
        self._model_vao = glGenVertexArrays(1)
        glBindVertexArray(self._model_vao)
        # set vertice attribute
        self._vertex_vbo.as_array_buffer(0, 4, GL_FLOAT)
        # set normal attribute
        self._normal_vbo.as_array_buffer(1, 4, GL_FLOAT)
        # set tessellate parameter attribute
        self.parameter_in_splited_triangle_vbo.as_array_buffer(2, 4, GL_FLOAT)
        # set split parameter attribute
        self.parameter_in_original_vbo.as_array_buffer(3, 4, GL_FLOAT)
        # specific index buffer
        self._index_vbo.as_element_array_buffer()
        # unbind program
        glBindVertexArray(0)
        self.gl_async_update_buffer_for_self()

    def gl_async_update_buffer_for_self(self):
        if self._vertex_vbo is not None:
            self._vertex_vbo.capacity = self.splited_triangle_number \
                                        * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
        if self._normal_vbo is not None:
            self._normal_vbo.capacity = self.splited_triangle_number \
                                        * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE

        if self.parameter_in_splited_triangle_vbo is not None:
            self.parameter_in_splited_triangle_vbo.capacity = self.splited_triangle_number \
                                                              * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
        if self.parameter_in_original_vbo is not None:
            self.parameter_in_original_vbo.capacity = self.splited_triangle_number \
                                                      * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
        if self._index_vbo is not None:
            self._index_vbo.capacity = self.splited_triangle_number \
                                       * self.tessellated_triangle_number_pre_splited_triangle * PER_TRIANGLE_INDEX_SIZE

    def gl_sync_buffer(self):
        self._vertex_vbo.gl_sync()
        self._normal_vbo.gl_sync()
        self.parameter_in_splited_triangle_vbo.gl_sync()
        self.parameter_in_original_vbo.gl_sync()
        self._index_vbo.gl_sync()

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
        glDispatchCompute(*self.group_size)
        self._need_deform = False
        glUseProgram(0)

    def gl_renderer(self, model_view_matrix: np.array, perspective_matrix: np.array, operator):
        self.gl_sync_buffer()
        self.gl_deform(operator)
        self._renderer_program.use()
        # common bind
        wvp_matrix = multiply(model_view_matrix, perspective_matrix)
        glUniformMatrix4fv(0, 1, GL_FALSE, wvp_matrix)
        glUniformMatrix4fv(1, 1, GL_FALSE, model_view_matrix)
        glEnable(GL_DEPTH_TEST)
        glBindVertexArray(self._model_vao)
        number = int(self.splited_triangle_number * self.tessellated_triangle_number_pre_splited_triangle * 3)
        glDrawElements(GL_TRIANGLES, number,
                       GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        glUseProgram(0)

    @property
    def splited_triangle_number(self):
        return self._splited_triangle_number

    @splited_triangle_number.setter
    def splited_triangle_number(self, number: int):
        if number == self._splited_triangle_number:
            return
        self._splited_triangle_number = number
        self.gl_async_update_buffer_for_self()
        self._splited_triangle_number_changed = True
        self._need_deform = True

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
