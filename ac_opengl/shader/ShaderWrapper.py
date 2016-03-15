from OpenGL.GL import *
from OpenGL.GL.shaders import *
from PyQt5.QtGui import QOpenGLShaderProgram, QOpenGLShader
import numpy as np

__author__ = 'ac'


class ShaderProgramWrap:
    def __init__(self):
        self.program = None
        self.shaders_info = []
        self.file_name_prefix = ''

    def add_shader(self, shader_type, file_name):
        self.shaders_info.append((shader_type, file_name))

    def get_program(self):
        '''
        import!!! should bu call in GL thread
        :return:
        '''
        shaders = []
        for t, f in self.shaders_info:
            shaders.append(
                compileShader(
                    self.prev_compile_source_code(self.get_source_code(f)),
                    t))

        if self.program is None:
            self.program = compileProgram(*shaders)
            self.init_uniform()
        return self.program

    def init_uniform(self):
        pass

    def get_source_code(self, file_name):
        with open(self.file_name_prefix + file_name) as file:
            return file.read()

    def prev_compile_source_code(self, source_code):
        return source_code

    def invalid_program(self):
        if self.program is not None:
            glDeleteProgram(self.program)
            self.program = None
        self.shaders_info = []


class PrevComputeProgramWrap(ShaderProgramWrap):
    def __init__(self, file_name):
        super().__init__()
        self.file_name_prefix = 'ac_opengl/shader/compute/'
        self._max_splited = 20
        self._split_factor = 0.3
        super().add_shader(GL_COMPUTE_SHADER, file_name)

        with open('pre_computer_data/split_pattern/%d.txt' % self._max_splited) as file:
            factor, offset_l, indexes_l, parameter_l = file
        self._factor = int(factor)
        self._offset_number = np.asarray([int(x) for x in offset_l.strip().split(" ")], dtype=np.uint32)
        self._indexes = np.asarray([int(x) for x in indexes_l.strip().split(" ")], dtype=np.uint32)
        self._parameter = np.asarray([abs(float(x)) for x in parameter_l.strip().split(" ")], dtype=np.float32)
        split_info_buffer = glGenBuffers(1)
        indexes, indexes_size = self.indexes
        parameter, parameter_size = self.parameter
        offset_number, offset_number_size = self.offset_number
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, split_info_buffer)
        glBufferData(GL_SHADER_STORAGE_BUFFER, offset_number_size + indexes_size + parameter_size,
                     None,
                     usage=GL_DYNAMIC_DRAW)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, indexes_size, indexes)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, indexes_size, parameter_size, parameter)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, indexes_size + parameter_size, offset_number_size, offset_number)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 9, split_info_buffer)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

    def init_uniform(self):
        glProgramUniform1f(self.program, 0, self._split_factor)

    @property
    def offset_number(self):
        return self._offset_number, self._offset_number.size * 4

    @property
    def indexes(self):
        return self._indexes, self._indexes.size * 4

    @property
    def parameter(self):
        return self._parameter, self._parameter.size * 4

    @property
    def split_factor(self):
        return self._split_factor

    @split_factor.setter
    def split_factor(self, split_factor):
        self._split_factor = split_factor
        glProgramUniform1f(self.program, 0, self._split_factor)

    def get_offset_for_i(self) -> str:
        look_up_table_for_i = [0]
        for i in range(1, self._max_splited):
            ii = min(self._max_splited - i, i)
            look_up_table_for_i.append(
                int(look_up_table_for_i[-1] + (1 + ii) * ii / 2 + max(0, (i + 1) * (self._max_splited - 2 * i))))
        res = '{'
        for x in look_up_table_for_i:
            res += (str(x) + ',')
        return res[:-1] + '}'

    def prev_compile_source_code(self, source_code: str) -> str:
        source_code = source_code.replace('uvec4 splitIndex[]',
                                          'uvec4 splitIndex[%d]' % (self._indexes.size / 4)) \
            .replace('vec4 splitParameter[]', 'vec4 splitParameter[%d]' % (self._parameter.size / 4)) \
            .replace('uint offset_number[]', 'uint offset_number[%d]' % self._offset_number.size) \
            .replace('const int max_splite_factor = 0', 'const int max_splite_factor = %d' % self._max_splited) \
            .replace('const uint look_up_table_for_i[0] = {0}',
                     'const uint look_up_table_for_i[%d] = {%s}' % (self._max_splited, self.get_offset_for_i()))
        return source_code


class DrawProgramWrap(ShaderProgramWrap):
    def __init__(self, vertex_shader_file_name, fragment_shader_file_name):
        super().__init__()
        self.file_name_prefix = 'ac_opengl/shader/renderer/'
        super().add_shader(GL_VERTEX_SHADER, vertex_shader_file_name)
        super().add_shader(GL_FRAGMENT_SHADER, fragment_shader_file_name)


class DeformComputeProgramWrap(ShaderProgramWrap):
    def __init__(self, file_name, splited_triangle_number, b_spline_body, tessellation_factor=3):
        super().__init__()
        self._b_spline_body = b_spline_body
        self._tessellation_factor = tessellation_factor
        self.tessellated_point_number_pre_splited_triangle = (tessellation_factor + 1) * (tessellation_factor + 2) / 2
        self.tessellated_triangle_number_pre_splited_triangle = tessellation_factor * tessellation_factor
        self.file_name_prefix = 'ac_opengl/shader/compute/'
        self.file_name = file_name
        self.splited_triangle_number = splited_triangle_number
        self._cage_size = None
        super().add_shader(GL_COMPUTE_SHADER, self.file_name)

    def prev_compile_source_code(self, source_code):
        return source_code.replace('!?include1', self.get_include1_content())

    def get_include1_content(self):
        level = self._tessellation_factor
        tessellation_parameter = []
        u = level
        for i in range(level + 1):
            v = level - u
            for j in range(i + 1):
                tessellation_parameter.append([u / level, v / level, (level - u - v) / level])
                v -= 1
            u -= 1

        tessellation_index = []
        for i in range(level):
            start = int((i + 1) * (i + 2) / 2)
            prev = [start, start + 1, start - 1 - i]
            tessellation_index.append(prev)
            for j in range(i * 2):
                next_index = [prev[2], prev[2] + 1, prev[1]]
                if j % 2 == 0:
                    tessellation_index.append([next_index[1], next_index[0], next_index[2]])
                else:
                    tessellation_index.append(next_index)
                prev = next_index

        self._cage_size = self._b_spline_body.get_cage_size()

        return 'const vec3 tessellatedParameter[{0}] = {1}; \
                    const uvec3 tessellateIndex[{2}] = {3};' \
            .format(*[len(tessellation_parameter),
                      '{' + ','.join(['{' + ','.join([str(y) for y in x]) + '}\n' for x in
                                      tessellation_parameter]) + '}',
                      len(tessellation_index),
                      '{' + ','.join(['{' + ','.join([str(y) for y in x]) + '}\n' for x in
                                      tessellation_index]) + '}'])

    @property
    def tessellation_factor(self):
        return self._tessellation_factor

    @tessellation_factor.setter
    def tessellation_factor(self, factor):
        self._tessellation_factor = factor
        self.tessellated_point_number_pre_splited_triangle = (factor + 1) * (factor + 2) / 2
        self.tessellated_triangle_number_pre_splited_triangle = factor ** 2
        self.invalid_program()

    def invalid_program(self):
        super().invalid_program()
        super().add_shader(GL_COMPUTE_SHADER, self.file_name)

    def init_uniform(self):
        glProgramUniform1ui(self.get_program(), 0, int(self.splited_triangle_number))
        glProgramUniform1ui(self.get_program(), 1, int(self._cage_size[1] * self._cage_size[2]))
        glProgramUniform1ui(self.get_program(), 2, int(self._cage_size[1]))
        glProgramUniform3f(self.get_program(), 3, 1 / self._cage_size[0], 1 / self._cage_size[1],
                           1 / self._cage_size[2])


def get_compute_shader_program(file_name):
    my_computer_shader = gen_shader(GL_COMPUTE_SHADER, get_compute_shader_file_path(file_name))
    return compileProgram(my_computer_shader)
    # program = glCreateProgram()
    # glAttachShader(program, my_computer_shader)
    # glLinkProgram(program)
    # print(str(glGetProgramInfoLog(program)))
    # return program


def get_renderer_shader_program_qobj(vertex_shader_file_name, fragment_shader_file_name):
    """
    :param vertex_shader_file_name:
    :param fragment_shader_file_name:
    :return:
    """
    program = QOpenGLShaderProgram()
    program \
        .addShaderFromSourceFile(QOpenGLShader.Vertex,
                                 get_renderer_shader_file_path(vertex_shader_file_name))
    program \
        .addShaderFromSourceFile(QOpenGLShader.Fragment,
                                 get_renderer_shader_file_path(fragment_shader_file_name))
    program.link()
    return program


def get_renderer_shader_program(vertex_shader_file_name, fragment_shader_file_name):
    """
    :param vertex_shader_file_name:
    :param fragment_shader_file_name:
    :type vertex_shader_file_name: str
    :type fragment_shader_file_name: str
    :return:
    """
    my_vertex_shader = gen_shader(GL_VERTEX_SHADER, get_renderer_shader_file_path(vertex_shader_file_name))
    my_fragment_shader = gen_shader(GL_FRAGMENT_SHADER, get_renderer_shader_file_path(fragment_shader_file_name))
    return compileProgram(my_vertex_shader, my_fragment_shader)


def gen_shader(shader_type, shader_file_name):
    """
    :param shader_file_name:
    :param shader_type:
    :return:
    """
    with open(shader_file_name) as file:
        source_code = file.read()
        # print(source_code.replace('!?include1', shader_parameter.get_for_shader()))
        if shader_type == GL_COMPUTE_SHADER:
            return compileShader(source_code.replace('!?include1', shader_parameter.get_for_shader()), shader_type)
        else:
            return compileShader(source_code, shader_type)


def get_renderer_shader_file_path(file_name):
    return 'shader/renderer/' + file_name


def get_compute_shader_file_path(file_name):
    return 'shader/compute/' + file_name


# test code
if __name__ == '__main__':
    t = PrevComputeProgramWrap(None)
