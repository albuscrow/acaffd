from Constant import *
from mvc_model.model import OBJ
from mvc_model.GLObject import ACVBO
from ac_opengl.shader.ShaderWrapper import ProgramWrap, ShaderWrap
from OpenGL.GL import *
from OpenGL.GLU import *
from pyrr.matrix44 import *

PATTERN_FILE_PATH = 'pre_computer_data/split_pattern/pattern_data.txt'


def add_prefix(file_name: str):
    return 'ac_opengl/shader/compute/' + file_name


class PreviousComputeShader(ShaderWrap):
    def __init__(self, shader_type: int, file_name: str, controller):
        super().__init__(shader_type, file_name)
        self._controller = controller  # type : PreviousComputeController

    def pre_compile(self):
        self._source_code = self._source_code \
            .replace('uvec4 splitIndex[]', 'uvec4 splitIndex[%d]' % (self._controller.pattern_indexes.size / 4)) \
            .replace('vec4 splitParameter[]',
                     'vec4 splitParameter[%d]' % (self._controller.pattern_parameters.size / 4)) \
            .replace('uint offset_number[]', 'uint offset_number[%d]' % self._controller.pattern_offsets.size) \
            .replace('const int max_split_factor = 0',
                     'const int max_split_factor = %d' % self._controller.MAX_SEGMENTS) \
            .replace('const uint look_up_table_for_i[0] = {0}',
                     'const uint look_up_table_for_i[%d] = %s' % (
                         self._controller.MAX_SEGMENTS, self._controller.get_offset_for_i()))
        return self


class PreviousComputeControllerGPU:
    def __init__(self, model: OBJ):
        self._model = model  # type: OBJ

        # init pattern data
        self._split_factor = 0.5  # type: float
        self.MAX_SEGMENTS = -1  # type: int
        self._pattern_offsets = None  # type: np.array
        self._pattern_indexes = None  # type: np.array
        self._pattern_parameters = None  # type: np.array
        self._need_recompute = True  # type: bool
        self._need_update_split_factor = True  # type: bool
        self._splited_triangle_number = -1  # type: int
        self.init_pattern_data()

        # declare buffer
        self._original_vertex_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 0, None, GL_STATIC_DRAW)
        self._original_normal_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 1, None, GL_STATIC_DRAW)
        self._original_tex_coord_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 22, None, GL_STATIC_DRAW)
        self._original_index_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 2, None, GL_STATIC_DRAW)
        self._splited_triangle_counter_acbo = ACVBO(GL_ATOMIC_COUNTER_BUFFER, 0, None, GL_DYNAMIC_DRAW)
        self._adjacency_info_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 3, None, GL_STATIC_DRAW)
        self._share_adjacency_pn_triangle_normal_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 4, None, GL_DYNAMIC_COPY)
        self._share_adjacency_pn_triangle_position_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 19, None, GL_DYNAMIC_COPY)
        self._splited_triangle_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 5, None, GL_STATIC_DRAW)

        # init shader
        self._program = ProgramWrap().add_shader(
            PreviousComputeShader(GL_COMPUTE_SHADER, add_prefix('previous_compute_shader_oo.glsl'),
                                  self))  # type: ProgramWrap

    def change_model(self, model):
        self._model = model
        self.gl_async_update_buffer_for_self_about_model()
        self._need_recompute = True  # type: bool

    def gl_init(self):
        self._program.link()
        self.gl_set_split_factor()
        # async update vbo
        self.gl_async_update_buffer_for_self()

    def gl_init_split_counter(self):
        self._splited_triangle_counter_acbo.async_update(np.array([0], dtype=np.uint32))
        self._splited_triangle_counter_acbo.gl_sync()

    def gl_async_update_buffer_for_self(self):
        indexes_size = self._pattern_indexes.size * self._pattern_indexes.itemsize
        parameter_size = self._pattern_parameters.size * self._pattern_parameters.itemsize
        offset_size = self._pattern_offsets.size * self._pattern_offsets.itemsize
        split_info_buffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, split_info_buffer)
        glBufferData(GL_SHADER_STORAGE_BUFFER, offset_size + indexes_size + parameter_size,
                     None,
                     usage=GL_DYNAMIC_DRAW)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, indexes_size, self._pattern_indexes)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, indexes_size, parameter_size, self._pattern_parameters)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, indexes_size + parameter_size, offset_size, self._pattern_offsets)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 9, split_info_buffer)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

        self.gl_async_update_buffer_for_self_about_model()

    def gl_async_update_buffer_for_self_about_model(self):
        self._original_vertex_ssbo.async_update(self._model.vertex)
        self._original_normal_ssbo.async_update(self._model.normal)
        self._original_tex_coord_ssbo.async_update(self._model.tex_coord)
        self._original_index_ssbo.async_update(self._model.index)
        self._adjacency_info_ssbo.async_update(self._model.adjacency)
        self.gl_async_update_buffer_about_output()

    def gl_async_update_buffer_about_output(self):
        self._share_adjacency_pn_triangle_normal_ssbo.capacity = self._model.original_triangle_number \
                                                                 * PER_TRIANGLE_PN_NORMAL_TRIANGLE_SIZE
        self._share_adjacency_pn_triangle_position_ssbo.capacity = self._model.original_triangle_number \
                                                                   * PER_TRIANGLE_PN_POSITION_TRIANGLE_SIZE
        # 用于储存原始三角面片的PN-triangle
        self._splited_triangle_ssbo.capacity = self._model.original_triangle_number \
                                               * MAX_SPLITED_TRIANGLE_PRE_ORIGINAL_TRIANGLE \
                                               * SPLITED_TRIANGLE_SIZE

    def gl_sync(self):
        self._original_vertex_ssbo.gl_sync()
        self._original_normal_ssbo.gl_sync()
        self._original_tex_coord_ssbo.gl_sync()
        self._original_index_ssbo.gl_sync()
        self._adjacency_info_ssbo.gl_sync()
        self._share_adjacency_pn_triangle_normal_ssbo.gl_sync()
        self._share_adjacency_pn_triangle_position_ssbo.gl_sync()
        self._splited_triangle_ssbo.gl_sync()

    def gl_compute(self) -> int:
        if not self._need_recompute:
            return self._splited_triangle_number, False
        self.gl_sync()
        if self._need_update_split_factor:
            self.gl_set_split_factor()
            self._need_update_split_factor = False
        self._program.use()
        self.gl_init_split_counter()
        glDispatchCompute(*self.group_size)
        glUseProgram(0)
        self._splited_triangle_number = self.get_splited_triangles_number()
        self._need_recompute = False
        print('gl_compute:', 'gpu splited triangle number: %d' % self._splited_triangle_number)
        return self._splited_triangle_number, True

    @property
    def need_compute(self):
        return self._need_recompute

    @need_compute.setter
    def need_compute(self, b):
        self._need_recompute = b

    @property
    def split_factor(self):
        return self._split_factor

    @property
    def group_size(self):
        return [int(self._model.original_triangle_number / 512 + 1), 1, 1]

    @split_factor.setter
    def split_factor(self, split_factor):
        self._split_factor = split_factor
        self._need_recompute = True
        self._need_update_split_factor = True

    def gl_set_split_factor(self):
        glProgramUniform1f(self._program.program, 0, self._split_factor)

    @property
    def pattern_offsets(self):
        return self._pattern_offsets

    @property
    def pattern_indexes(self):
        return self._pattern_indexes

    @property
    def pattern_parameters(self):
        return self._pattern_parameters

    def init_pattern_data(self):
        with open(PATTERN_FILE_PATH) as file:
            max_factor, offset_line, indexes_line, parameter_line = file
        self.MAX_SEGMENTS = int(max_factor)
        self._pattern_offsets = np.asarray([int(x) for x in offset_line.strip().split(" ")], dtype=np.uint32)
        self._pattern_indexes = np.asarray([int(x) for x in indexes_line.strip().split(" ")], dtype=np.uint32)
        self._pattern_parameters = np.asarray([abs(float(x)) for x in parameter_line.strip().split(" ")],
                                              dtype=np.float32)

    def get_offset_for_i(self) -> str:
        look_up_table_for_i = [0]
        for i in range(1, self.MAX_SEGMENTS):
            ii = min(self.MAX_SEGMENTS - i, i)
            look_up_table_for_i.append(
                int(look_up_table_for_i[-1] + (1 + ii) * ii / 2 + max(0, (i + 1) * (self.MAX_SEGMENTS - 2 * i))))
        return '{' + ','.join([str(i) for i in look_up_table_for_i]) + '}'

    def get_splited_triangles_number(self) -> int:
        return self._splited_triangle_counter_acbo.get_value(ctypes.c_uint32)[0]

    @property
    def splited_triangle_number(self):
        return self._splited_triangle_number

    @property
    def share_adjacency_pn_triangle_normal_ssbo(self):
        return self._share_adjacency_pn_triangle_normal_ssbo

    @property
    def share_adjacency_pn_triangle_position_ssbo(self):
        return self._share_adjacency_pn_triangle_position_ssbo

    @property
    def splited_triangle_ssbo(self):
        return self._splited_triangle_ssbo
