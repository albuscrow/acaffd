from ctypes import c_uint
import numpy
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from model.RawOBJModel import OBJ
from shader.ShaderUtil import get_shader_render_program_qobj, get_shader_render_program
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from queue import Queue


class Renderer(QObject):
    updateScene = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._t = 0
        self.shader_program = None
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.draw = None
        self.gl_task = Queue()

    def set_view_port(self, x, y, w, h):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

    def set_t(self, t):
        self._t = t

    @pyqtSlot()
    def paint(self):
        if not self.gl_task.empty():
            task = self.gl_task.get()
            self.draw = task()
            self.gl_task.task_done()

        if self.draw:
            self.draw()

    @pyqtSlot(OBJ)
    def handle_new_obj(self, obj):
        def init_task():
            # init program
            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)

            buffers = glGenBuffers(2)
            vvbo = buffers[0]
            ivbo = buffers[1]

            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ivbo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, numpy.array(obj.indexes, dtype='int32'), GL_STATIC_DRAW)
            # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

            glBindBuffer(GL_ARRAY_BUFFER, vvbo)
            glBufferData(GL_ARRAY_BUFFER, len(obj.vertices) * 12,
                         numpy.array([v for p in obj.vertices for v in p], dtype='float32'),
                         usage=GL_STATIC_DRAW)
            self.shader_program = get_shader_render_program('vertex.glsl', 'fragment.glsl')
            glUseProgram(self.shader_program)
            vl = glGetAttribLocation(self.shader_program, 'vertice')
            glEnableVertexAttribArray(vl)
            glVertexAttribPointer(vl, 3, GL_FLOAT, False, 0, None)
            # glDisableVertexAttribArray(vl)
            glUseProgram(0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

            glBindVertexArray(0)
            glDeleteBuffers(2, buffers)

            self.shader_program = get_shader_render_program('vertex.glsl', 'fragment.glsl')

            # set index
            def draw():
                glBindVertexArray(vao)
                glUseProgram(self.shader_program)

                glViewport(self.x, self.y, self.w, self.h)

                glEnable(GL_SCISSOR_TEST)
                glScissor(self.x, self.y, self.w, self.h)

                glDisable(GL_DEPTH_TEST)

                glClearColor(0, 0, 0, 1)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                glDrawElements(GL_TRIANGLES, len(obj.indexes), GL_UNSIGNED_INT, None)

                glDisable(GL_SCISSOR_TEST)

                glUseProgram(0)
                glBindVertexArray(0)

            return draw

        self.gl_task.put(init_task)
