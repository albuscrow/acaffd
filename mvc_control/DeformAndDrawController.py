from Constant import *
from mvc_model.model import OBJ
from mvc_model.GLObject import ACVBO
from ac_opengl.shader.ShaderWrapper import ProgramWrap, ShaderWrap
from OpenGL.GL import *
from OpenGL.GLU import *
from pyrr.matrix44 import *
from mvc_control.BSplineBodyController import BSplineBodyController


def add_compute_prefix(file_name: str):
    return 'ac_opengl/shader/compute/' + file_name


def add_renderer_prefix(file_name: str):
    return 'ac_opengl/shader/renderer/' + file_name


class DeformComputeShader(ProgramWrap):
    def __init__(self, controller):
        super().__init__()
        self._controller = controller  # type: DeformAndDrawController

    def init_uniform(self):
        glProgramUniform1ui(self._gl_program_name, 0, int(self._controller.splited_triangle_number))
        glProgramUniform1ui(self._gl_program_name, 1,
                            int(self._controller.cage_size[1] * self._controller.cage_size[2]))
        glProgramUniform1ui(self._gl_program_name, 2, int(self._controller.cage_size[1]))
        glProgramUniform3f(self._gl_program_name, 3, 1 / self._controller.cage_size[0],
                           1 / self._controller.cage_size[1],
                           1 / self._controller.cage_size[2])
        glProgramUniform1ui(self._gl_program_name, 4,
                            int(self._controller.tessellated_point_number_pre_splited_triangle))
        glProgramUniform1ui(self._gl_program_name, 5,
                            int(self._controller.tessellated_triangle_number_pre_splited_triangle))
        tp = ACVBO(GL_UNIFORM_BUFFER, 2, np.array(self._controller.tessellation_parameter, dtype=np.float32),
                   GL_STATIC_DRAW)
        tp.gl_sync()
        ti = ACVBO(GL_UNIFORM_BUFFER, 3, np.array(self._controller.tessellation_index, dtype=np.uint32), GL_STATIC_DRAW)
        ti.gl_sync()


class DeformAndDrawController:
    def __init__(self, triangle_number: int, cage_size: list):
        self._splited_triangle_number = triangle_number
        self._cage_size = cage_size  # type: list

        self._tessellation_level = -1  # type: int
        self._tessellated_point_number_pre_splited_triangle = -1  # type: int
        self._tessellated_triangle_number_pre_splited_triangle = -1  # type: int
        self._tessellation_parameter = None  # type: list
        self._tessellation_index = None  # type: list
        self.init_tessellation_pattern_data(3)

        self._need_deform = True  # type: bool

        # vbo
        self._vertex_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 6, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._normal_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 7, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._index_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 8, None, GL_DYNAMIC_DRAW)  # type: ACVBO
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
        # specific index buffer
        self._index_vbo.as_element_array_buffer()
        # unbind program
        glBindVertexArray(0)
        self.gl_async_update_buffer_for_self()

    def gl_async_update_buffer_for_self(self):
        self._vertex_vbo.capacity = self.splited_triangle_number * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
        # alloc memory in gpu for tessellated normal
        self._normal_vbo.capacity = self.splited_triangle_number * self.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
        # alloc memory in gpu for tessellated index
        self._index_vbo.capacity = self.splited_triangle_number * self.tessellated_triangle_number_pre_splited_triangle * PER_TRIANGLE_INDEX_SIZE

    def gl_sync_buffer(self):
        self._vertex_vbo.gl_sync()
        self._normal_vbo.gl_sync()
        self._index_vbo.gl_sync()

    def gl_deform(self, b_spline_controller: BSplineBodyController):
        if self.need_deform:
            b_spline_controller.gl_sync_buffer_for_deformation()
            self._deform_program.use()
            glDispatchCompute(*self.group_size)
            self._need_deform = False
            glUseProgram(0)

    def gl_renderer(self, model_view_matrix: np.array, perspective_matrix: np.array,
                    b_spline_controller: BSplineBodyController):
        self.gl_sync_buffer()
        self.gl_deform(b_spline_controller)
        self._renderer_program.use()
        # common bind
        wvp_matrix = multiply(model_view_matrix, perspective_matrix)
        glUniformMatrix4fv(0, 1, GL_FALSE, wvp_matrix)
        glUniformMatrix4fv(1, 1, GL_FALSE, model_view_matrix)
        glEnable(GL_DEPTH_TEST)
        glBindVertexArray(self._model_vao)
        glDrawElements(GL_TRIANGLES, int(
            self.splited_triangle_number *
            self.tessellated_triangle_number_pre_splited_triangle * 3),
                       GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        glUseProgram(0)

    @property
    def splited_triangle_number(self):
        return self._splited_triangle_number

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
        return self._tessellation_parameter

    @property
    def tessellation_index(self):
        return self._tessellation_index

    @property
    def need_deform(self):
        return self._need_deform

    @need_deform.setter
    def need_deform(self, value):
        self._need_deform = value
