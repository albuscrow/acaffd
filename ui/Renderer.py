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
            task()
            self.gl_task.task_done()

    @pyqtSlot(OBJ)
    def handle_new_obj(self, obj):
        def init_task():
            # init program
            self.shader_program = get_shader_render_program_qobj('vertex.glsl', 'fragment.glsl')
            self.shader_program.bind()
            # self.shader_program.enableAttributeArray('vertice')
            # self.shader_program.setAttributeArray('vertice', obj.vertices)

            vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, len(obj.vertices) * 4, numpy.array(obj.vertices, dtype='float32'),
                         usage=GL_STATIC_DRAW)
            program = self.shader_program.programId()
            l = glGetAttribLocation(program, 'vertice')
            glEnableVertexAttribArray(l)
            glVertexAttribPointer(l, 3, GL_FLOAT, False, 0, 0)
            print(gluErrorString(glGetError()))

            # set index
            # index_vbo = glGenBuffers(1)
            # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, index_vbo)
            # glBufferData(GL_ELEMENT_ARRAY_BUFFER, numpy.array(obj.indexes, dtype='int32'), GL_STATIC_DRAW)

            glViewport(self.x, self.y, self.w, self.h)
            glEnable(GL_SCISSOR_TEST)
            glScissor(self.x, self.y, self.w, self.h)

            glDisable(GL_DEPTH_TEST)

            glClearColor(0.5, 0.5, 0.5, 1)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)

            glDrawArrays(GL_TRIANGLE_STRIP, 0, len(obj.vertices))
            # glDrawElements(GL_POINTS, len(obj.indexes), GL_UNSIGNED_INT, obj.indexes)

            glDisable(GL_SCISSOR_TEST)

            self.shader_program.disableAttributeArray('vertice')
            self.shader_program.release()

        self.gl_task.put(init_task)
