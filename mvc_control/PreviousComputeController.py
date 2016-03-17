from Constant import *
from mvc_model.model import OBJ
from mvc_model.GLObject import ACVBO
from mvc_model.aux import BSplineBody
from ac_opengl.shader.ShaderWrapper2 import ProgramWrap, ShaderWrap
from OpenGL.GL import *
from OpenGL.GLU import *
from pyrr.matrix44 import *

PATTERN_FILE_PATH = 'pre_computer_data/split_pattern/pattern_data.txt'


def add_prefix(file_name: str):
    return 'ac_opengl/shader/compute/' + file_name


class PreviousComputeShader(ShaderWrap):
    def __init__(self, shader_type: int, file_name: str, out):
        super().__init__(shader_type, file_name)
        self._out = out  # type : PreviousComputeController

    def pre_compile(self):
        self._source_code = self._source_code \
            .replace('uvec4 splitIndex[]', 'uvec4 splitIndex[%d]' % (self._out.pattern_indexes.size / 4)) \
            .replace('vec4 splitParameter[]', 'vec4 splitParameter[%d]' % (self._out.pattern_parameters.size / 4)) \
            .replace('uint offset_number[]', 'uint offset_number[%d]' % self._out.pattern_offsets.size) \
            .replace('const int max_split_factor = 0',
                     'const int max_split_factor = %d' % self._out.MAX_SEGMENTS) \
            .replace('const uint look_up_table_for_i[0] = {0}',
                     'const uint look_up_table_for_i[%d] = {%s}' % (
                         self._out.MAX_SEGMENTS, self._out.get_offset_for_i()))
        return self


class PreviousComputeController:
    def __init__(self, model: OBJ):
        self._model = model  # type: OBJ

        # init pattern data
        self._split_factor = 0.1  # type: float
        self.MAX_SEGMENTS = -1  # type: int
        self._pattern_offsets = None  # type: np.array
        self._pattern_indexes = None  # type: np.array
        self._pattern_parameters = None  # type: np.array
        self._split_factor_change = False  # type: bool
        self.init_pattern_data()

        # declare buffer
        self._original_vertex_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 0, None, GL_STATIC_DRAW)
        self._original_normal_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 1, None, GL_STATIC_DRAW)
        self._original_index_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 2, None, GL_STATIC_DRAW)
        self._splited_triangle_counter_acbo = ACVBO(GL_ATOMIC_COUNTER_BUFFER, 0, None, GL_DYNAMIC_DRAW)
        self._adjacency_info_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 3, None, GL_STATIC_DRAW)
        self._share_adjacency_pn_triangle_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 4, None, GL_STATIC_DRAW)
        self._splited_triangle_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 5, None, GL_STATIC_DRAW)

        # init shader
        self._program = ProgramWrap().add_shader(
            PreviousComputeShader(GL_COMPUTE_SHADER, add_prefix('previous_compute_shader_oo.glsl'),
                                  self))  # type: ProgramWrap

    def gl_init(self):
        self._program.link()
        self.gl_set_split_factor()
        # init vbo
        self.gl_init_buffer_for_self()

    def gl_init_split_counter(self):
        self._splited_triangle_counter_acbo.async_update(np.array([0], dtype=np.uint32))
        self._splited_triangle_counter_acbo.gl_sync()

    def gl_init_buffer_for_self(self):
        split_info_buffer = glGenBuffers(1)
        indexes_size = self._pattern_indexes.size * self._pattern_indexes.itemsize
        parameter_size = self._pattern_parameters.size * self._pattern_parameters.itemsize
        offset_size = self._pattern_offsets.size * self._pattern_offsets.itemsize
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, split_info_buffer)
        glBufferData(GL_SHADER_STORAGE_BUFFER, offset_size + indexes_size + parameter_size,
                     None,
                     usage=GL_DYNAMIC_DRAW)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, indexes_size, self._pattern_indexes)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, indexes_size, parameter_size, self._pattern_parameters)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, indexes_size + parameter_size, offset_size, self._pattern_offsets)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 9, split_info_buffer)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

        self._original_vertex_ssbo.async_update(self._model.vertex)
        self._original_normal_ssbo.async_update(self._model.normal)
        self._original_index_ssbo.async_update(self._model.index)
        # copy original index to gpu, and bind original_index_vbo to bind point 2
        self._adjacency_info_ssbo.async_update(self._model.adjacency)
        # copy adjacency table to gpu, and bind adjacency_vbo to bind point 3
        self._share_adjacency_pn_triangle_ssbo.capacity = self._model.original_triangle_number \
                                                          * PER_TRIANGLE_PN_NORMAL_TRIANGLE_SIZE
        # 用于储存原始三角面片的PN-triangle
        self._splited_triangle_ssbo.capacity = self._model.original_triangle_number \
                                               * MAX_SPLITED_TRIANGLE_PRE_ORIGINAL_TRIANGLE \
                                               * SPLITED_TRIANGLE_SIZE

    def gl_sync(self):
        self._original_vertex_ssbo.gl_sync()
        self._original_normal_ssbo.gl_sync()
        self._original_index_ssbo.gl_sync()
        self._adjacency_info_ssbo.gl_sync()
        self._share_adjacency_pn_triangle_ssbo.gl_sync()
        self._splited_triangle_ssbo.gl_sync()

    def gl_compute(self):
        self.gl_sync()
        self._program.use()
        self.gl_init_split_counter()
        glDispatchCompute(*self.group_size)

    @property
    def split_factor(self):
        return self._split_factor

    @property
    def group_size(self):
        return [int(self._model.original_triangle_number / 512 + 1), 1, 1]

    @split_factor.setter
    def split_factor(self, split_factor):
        self._split_factor = split_factor
        self._split_factor_change = True

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