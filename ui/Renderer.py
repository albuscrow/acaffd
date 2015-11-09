import math
import numpy
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

from model import BSplineBody
from model.RawOBJModel import OBJ
from shader.ShaderUtil import get_shader_render_program_qobj, get_shader_render_program
from OpenGL.GL import *
from pyrr.matrix44 import *
from pyrr.euler import *
from OpenGL.GLUT import *
from queue import Queue


class Renderer(QObject):
    updateScene = pyqtSignal()
    resetOpenglStatus = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.shader_program = None
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.gl_task = Queue()
        self.rotate_y = 0
        self.rotate_x = 0
        self.initCommand = None
        self.drawCommand = None
        self.bindCommand = None
        self.unbindCommand = None

    def set_view_port(self, x, y, w, h):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

    @pyqtSlot()
    def paint(self):
        if not self.gl_task.empty():
            task = self.gl_task.get()
            task()
            self.gl_task.task_done()

        if self.initCommand:
            self.initCommand()
            self.initCommand = None

        if not self.bindCommand or not self.drawCommand or not self.unbindCommand:
            return

        self.bindCommand()

        perspective_matrix = create_perspective_projection_matrix(30, self.w / self.h, 2, 100,
                                                                  dtype='float32')
        # common bind
        pml = glGetUniformLocation(self.shader_program, 'perspective_matrix')
        glUniformMatrix4fv(pml, 1, GL_FALSE, perspective_matrix)

        vml = glGetUniformLocation(self.shader_program, 'view_matrix')
        glUniformMatrix4fv(vml, 1, GL_FALSE, create_identity(dtype='float32'))

        world_matrix = create_from_translation(numpy.array([0, 0, -10]))
        world_matrix = multiply(
            create_from_eulers(create(self.rotate_x / 180 * math.pi, 0, -self.rotate_y / 180 * math.pi),
                               dtype='float32'), world_matrix)
        # world_matrix = multiply(create_from_x_rotation(self.rotate_x / 180 * math.pi, dtype='float32'), world_matrix)
        wml = glGetUniformLocation(self.shader_program, 'world_matrix')
        glUniformMatrix4fv(wml, 1, GL_FALSE, world_matrix)

        glViewport(self.x, self.y, self.w, self.h)

        glEnable(GL_SCISSOR_TEST)
        glScissor(self.x, self.y, self.w, self.h)

        glEnable(GL_DEPTH_TEST)

        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.drawCommand()

        glDisable(GL_SCISSOR_TEST)

        self.unbindCommand()

    @pyqtSlot(OBJ)
    def handle_new_obj(self, obj):
        def init_task():
            # init program
            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)

            buffers = glGenBuffers(3)
            vvbo = buffers[0]
            ivbo = buffers[1]
            nvbo = buffers[2]

            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ivbo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, numpy.array(obj.indexes, dtype='int32'), GL_STATIC_DRAW)

            self.shader_program = get_shader_render_program('vertex.glsl', 'fragment.glsl')
            glUseProgram(self.shader_program)

            # vertice attribute
            glBindBuffer(GL_ARRAY_BUFFER, vvbo)
            glBufferData(GL_ARRAY_BUFFER, len(obj.vertices) * 12,
                         numpy.array([v for point in obj.vertices for v in point], dtype='float32'),
                         usage=GL_STATIC_DRAW)
            vl = glGetAttribLocation(self.shader_program, 'vertice')
            glEnableVertexAttribArray(vl)
            glVertexAttribPointer(vl, 3, GL_FLOAT, False, 0, None)

            # normal attribute
            glBindBuffer(GL_ARRAY_BUFFER, nvbo)
            glBufferData(GL_ARRAY_BUFFER, len(obj.normals) * 12,
                         numpy.array([v for point in obj.normals for v in point], dtype='float32'),
                         usage=GL_STATIC_DRAW)
            nl = glGetAttribLocation(self.shader_program, 'normal')
            glEnableVertexAttribArray(nl)
            glVertexAttribPointer(nl, 3, GL_FLOAT, False, 0, None)

            glUseProgram(0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

            glBindVertexArray(0)
            glDeleteBuffers(3, buffers)

            self.shader_program = get_shader_render_program('vertex.glsl', 'fragment.glsl')

            def bind():
                glBindVertexArray(vao)
                glUseProgram(self.shader_program)

            def unbind():
                glUseProgram(0)
                glBindVertexArray(0)

            # set index
            def draw():
                glDrawElements(GL_TRIANGLES, len(obj.indexes), GL_UNSIGNED_INT, None)

            self.bindCommand = bind
            self.drawCommand = draw
            self.unbindCommand = unbind

        self.initCommand = init_task
        self.updateScene.emit()

    @pyqtSlot(int, int)
    def change_rotate(self, x, y):
        self.rotate_y += x
        self.rotate_x += y
        self.updateScene.emit()

    @pyqtSlot(BSplineBody)
    def draw_b_spline_body(self, b_spline_body):
        if b_spline_body:
            def draw_b_spline_body():
                pass

            self.draw_b_spline_body_commond = draw_b_spline_body()

