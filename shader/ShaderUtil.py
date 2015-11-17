from OpenGL.GL import *
from OpenGL.GL.shaders import *
from PyQt5.QtGui import QOpenGLShaderProgram, QOpenGLShader

__author__ = 'ac'


def get_compute_shader_program(file_name):
    my_computer_shader = gen_shader(GL_COMPUTE_SHADER, get_compute_shader_file_path(file_name))
    return compileProgram(my_computer_shader)
    # program = glCreateProgram()
    # glAttachShader(program, my_computer_shader)
    # glLinkProgram(program)
    # print(glGetProgramInfoLog(program))
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
        return compileShader(source_code, shader_type)


def get_renderer_shader_file_path(file_name):
    return 'shader/renderer/' + file_name


def get_compute_shader_file_path(file_name):
    return 'shader/compute/' + file_name
