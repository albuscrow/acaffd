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
        self.program = None

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
                            self.prev_compile_source_code(t, self.get_source_code(f)),
                            t))

        if self.program is None:
            self.program = compileProgram(*shaders)
        return self.program

    def get_source_code(self, file_name):
        with open(self.file_name_prefix + file_name) as file:
            return file.read()

    def prev_compile_source_code(self, shader_type, source_code):
        return source_code

    def invalid_program(self):
        if self.program is not None:
            glDeleteProgram(self.program)
            self.program = None
        self.shaders_info = []


class PrevComputeProgramWrap(ShaderProgramWrap):
    def __init__(self, file_name):
        super().__init__()
        self.file_name_prefix = 'shader/compute/'
        self._max_splited = 20
        self._split_factor = 0.3
        super().add_shader(GL_COMPUTE_SHADER, file_name)

        with open('splite_pattern/%d.txt' % self._max_splited) as file:
            factor, offset_l, indexes_l, parameter_l = file
        self._factor = int(factor)
        self._offset_number = np.asarray([int(x) for x in offset_l.strip().split(" ")], dtype=np.uint32)
        self._indexes = np.asarray([int(x) for x in indexes_l.strip().split(" ")], dtype=np.uint32)
        self._parameter = np.asarray([abs(float(x)) for x in parameter_l.strip().split(" ")], dtype=np.float32)
        self._pattern = self.get_pattern()
        # print(self._pattern)
        # print(self._offset_number)
        # print(self._indexes)
        # print(self._parameter)

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

    # def get_split_data_size(self):
    #     return (self._offset_number + self._indexes + self._parameter) * 4

    def get_pattern(self):
        return "layout(std430, binding=9) buffer SplitedData{\n\
            uvec4 splitIndex[%d];\n\
            vec4 splitParameter[%d];\n\
            uint offset_number[%d];\n\
        };\n\
        const float splite_factor = acacac;\n\
        const int max_splite_factor = %d;\n\
        const uint look_up_table_for_i[%d] = %s;\n" % (
            self._indexes.size / 4, self._parameter.size / 4, self._offset_number.size, self._max_splited,
            self._max_splited,
            self.get_offset_for_i())

    ##[0, 37, 88, 150, 220, 295, 372, 448, 520, 585, 640, 685, 721, 749, 770, 785, 795, 801, 804, 805]
    def get_offset_for_i(self):

        look_up_table_for_i = [0]
        for i in range(1, self._max_splited):
            ii = min(self._max_splited - i, i)
            look_up_table_for_i.append(
                    int(look_up_table_for_i[-1] + (1 + ii) * ii / 2 + max(0, (i + 1) * (self._max_splited - 2 * i))))

        # look_up_table_for_i = [0]
        # for i in range(1, self._max_splited):
        #     ii = min(self._max_splited - i, i)
        #     look_up_table_for_i.append(
        #             int(look_up_table_for_i[-1] + (1 + ii) * ii / 2 + max(0, i * (self._max_splited - 2 * i))))
        res = '{'
        for x in look_up_table_for_i:
            res += (str(x) + ',')
        return res[:-1] + '}'

    def prev_compile_source_code(self, shader_type, source_code):
        return source_code.replace('!?include1', self.get_include1_content())

    def get_include1_content(self):
        return self._pattern.replace('acacac', str(self._split_factor))


class DrawProgramWrap(ShaderProgramWrap):
    def __init__(self, vertex_shader_file_name, fragment_shader_file_name):
        super().__init__()
        self.file_name_prefix = 'shader/renderer/'
        super().add_shader(GL_VERTEX_SHADER, vertex_shader_file_name)
        super().add_shader(GL_FRAGMENT_SHADER, fragment_shader_file_name)


class DeformComputeProgramWrap(ShaderProgramWrap):
    def __init__(self, file_name, splited_triangle_number, b_spline_body, tessellation_factor=3):
        super().__init__()
        self._b_spline_body = b_spline_body
        self._tessellation_factor = tessellation_factor
        self.tessellated_point_number_pre_splited_triangle = (tessellation_factor + 1) * (tessellation_factor + 2) / 2
        self.tessellated_triangle_number_pre_splited_triangle = tessellation_factor * tessellation_factor
        self.file_name_prefix = 'shader/compute/'
        self.file_name = file_name
        self.splited_triangle_number = splited_triangle_number
        super().add_shader(GL_COMPUTE_SHADER, self.file_name)

    def prev_compile_source_code(self, shader_type, source_code):
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

        u, v, w = self._b_spline_body.get_cage_size()

        return 'const uint triangleNumber = {4};\
               const uint vw = {5}; \
               const uint w = {6}; \
               const float x_stride = {7};\
               const float y_stride = {8};\
               const float z_stride = {9};\
               const vec3 tessellatedParameter[{0}] = {1}; \
                    const uvec3 tessellateIndex[{2}] = {3};' \
            .format(*[len(tessellation_parameter),
                      '{' + ','.join(['{' + ','.join([str(y) for y in x]) + '}\n' for x in
                                      tessellation_parameter]) + '}',
                      len(tessellation_index),
                      '{' + ','.join(['{' + ','.join([str(y) for y in x]) + '}\n' for x in
                                      tessellation_index]) + '}', self.splited_triangle_number, v * w, w, 1 / u, 1 / v,
                      1 / w])

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
