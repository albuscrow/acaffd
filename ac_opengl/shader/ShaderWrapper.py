from OpenGL.GL.shaders import *
from OpenGL.GL import *
from util.util import filter_for_speed

__author__ = 'ac'


class ShaderWrap:
    def __init__(self, shader_type: int, file_name: str):
        self._shader_type = shader_type  # type: int
        self._file_name = file_name  # type: str
        self._source_code = None  # type: str
        with open(file_name) as file:
            self._source_code = file.read()
        self._gl_shader_name = -1  # type: int

    def pre_compile(self):
        return self

    def compile(self):
        self._gl_shader_name = compileShader(filter_for_speed(self._source_code), self._shader_type)
        return self

    @property
    def shader(self):
        return self._gl_shader_name

    def __del__(self):
        glDeleteShader(self._gl_shader_name)
        self._gl_shader_name = -1


class ProgramWrap:
    def __init__(self):
        self._gl_program_name = -1  # type: int
        self._shaders = []  # type: list

    @property
    def program(self):
        return self._gl_program_name

    def add_shader(self, shader: ShaderWrap):
        self._shaders.append(shader)
        return self

    def link(self):
        if self._gl_program_name == -1:
            self._gl_program_name = compileProgram(*[s.pre_compile().compile().shader for s in self._shaders])
            self.init_uniform()
        return self

    def init_data(self):
        pass

    def use(self):
        self.link()
        glUseProgram(self._gl_program_name)

    def init_uniform(self):
        pass

    def __del__(self):
        glDeleteProgram(self._gl_program_name)
        self._gl_program_name = -1
