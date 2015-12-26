from OpenGL.GL import *
from OpenGL.GL.shaders import *
from PyQt5.QtGui import QOpenGLShaderProgram, QOpenGLShader
from Constant import *

__author__ = 'ac'


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
        print(source_code.replace('!?include1', shader_parameter.get_for_shader()))
        return compileShader(source_code.replace('!?include1', shader_parameter.get_for_shader()), shader_type)


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

if __name__ == '__main__':
    shader_parameter.init_tessllation_level(4)
    print(shader_parameter.get_for_shader())
