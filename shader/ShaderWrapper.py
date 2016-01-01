from OpenGL.GL import *
from OpenGL.GL.shaders import *
from PyQt5.QtGui import QOpenGLShaderProgram, QOpenGLShader

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
        super().add_shader(GL_COMPUTE_SHADER, file_name)


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


class TessellationParameters:
    def __init__(self):
        self.tessellated_triangle_number_pre_splited_triangle = 0
        self.tessellated_point_number_pre_splited_triangle = 0
        self.tessellation_index = []
        self.tessellation_parameter = []

    def init_tessllation_level(self, level):
        self.tessellation_parameter = []
        u = level
        for i in range(level + 1):
            v = level - u
            for j in range(i + 1):
                self.tessellation_parameter.append([u / level, v / level, (level - u - v) / level])
                v -= 1
            u -= 1

        self.tessellation_index = []
        for i in range(level):
            start = int((i + 1) * (i + 2) / 2)
            prev = [start, start + 1, start - 1 - i]
            self.tessellation_index.append(prev)
            for j in range(i * 2):
                next_index = [prev[2], prev[2] + 1, prev[1]]
                if j % 2 == 0:
                    self.tessellation_index.append([next_index[1], next_index[0], next_index[2]])
                else:
                    self.tessellation_index.append(next_index)
                prev = next_index

        self.tessellated_triangle_number_pre_splited_triangle = len(self.tessellation_index)
        self.tessellated_point_number_pre_splited_triangle = len(self.tessellation_parameter)

    def get_for_shader(self):
        return 'const vec3 tessellatedParameter[{0}] = {1}; \
                    const uvec3 tessellateIndex[{2}] = {3};' \
            .format(*[len(self.tessellation_parameter),
                      '{' + ','.join(['{' + ','.join([str(y) for y in x]) + '}\n' for x in
                                      self.tessellation_parameter]) + '}',
                      len(self.tessellation_index),
                      '{' + ','.join(['{' + ','.join([str(y) for y in x]) + '}\n' for x in
                                      self.tessellation_index]) + '}'])


shader_parameter = TessellationParameters()
shader_parameter.init_tessllation_level(3)

if __name__ == '__main__':
    shader_parameter.init_tessllation_level(4)
    print(shader_parameter.get_for_shader())
