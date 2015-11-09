import math
import numpy
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from util.util import static_var
from model.aux import BSplineBody
from model.model import OBJ
from shader.ShaderUtil import get_shader_render_program_qobj, get_shader_render_program
from OpenGL.GL import *
from pyrr.matrix44 import *
from pyrr.euler import *
from OpenGL.GLUT import *
from queue import Queue


class Renderer(QObject):
    updateScene = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.gl_task = Queue()
        self.renderer_model_task = None
        self.renderer_aux_task = None

        self.rotate_x = 0
        self.rotate_y = 0

        self.perspective_matrix = None

        self.translation_matrix = create_from_translation(numpy.array([0, 0, -5]), dtype='float32')

        self.model_view_matrix = multiply(create_from_eulers(create(-self.rotate_x / 180 * math.pi, 0,
                                                                    -self.rotate_y / 180 * math.pi), dtype='float32'),
                                          self.translation_matrix)

    def set_view_port(self, x, y, w, h):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

        self.perspective_matrix = create_perspective_projection_matrix(50, self.w / self.h, 2, 100,
                                                                       dtype='float32')

    @pyqtSlot()
    def paint(self):
        if not self.gl_task.empty():
            task = self.gl_task.get()
            task()
            self.gl_task.task_done()

        glViewport(self.x, self.y, self.w, self.h)
        glEnable(GL_SCISSOR_TEST)
        glScissor(self.x, self.y, self.w, self.h)
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.renderer_model_task:
            self.renderer_model_task()

        if self.renderer_aux_task and self.renderer_aux_task.is_show:
            self.renderer_aux_task()

        glDisable(GL_SCISSOR_TEST)

    @pyqtSlot(OBJ)
    def handle_new_obj(self, obj):
        @static_var(shader=None, vao=None, index=None, rotate_x=0, rotate_y=0)
        def renderer_model_task():
            # init program
            if not renderer_model_task.shader:
                renderer_model_task.vao = glGenVertexArrays(1)
                glBindVertexArray(renderer_model_task.vao)

                buffers = glGenBuffers(3)
                vvbo = buffers[0]
                ivbo = buffers[1]
                nvbo = buffers[2]

                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ivbo)
                glBufferData(GL_ELEMENT_ARRAY_BUFFER, numpy.array(obj.indexes, dtype='int32'), GL_STATIC_DRAW)

                renderer_model_task.shader = get_shader_render_program('vertex.glsl', 'fragment.glsl')
                glUseProgram(renderer_model_task.shader)

                # vertice attribute
                glBindBuffer(GL_ARRAY_BUFFER, vvbo)
                glBufferData(GL_ARRAY_BUFFER, len(obj.vertices) * 12,
                             numpy.array(obj.vertices, dtype='float32'),
                             usage=GL_STATIC_DRAW)
                vl = glGetAttribLocation(renderer_model_task.shader, 'vertice')
                glEnableVertexAttribArray(vl)
                glVertexAttribPointer(vl, 3, GL_FLOAT, False, 0, None)

                # normal attribute
                glBindBuffer(GL_ARRAY_BUFFER, nvbo)
                glBufferData(GL_ARRAY_BUFFER, len(obj.normals) * 12,
                             numpy.array(obj.normals, dtype='float32'),
                             usage=GL_STATIC_DRAW)
                nl = glGetAttribLocation(renderer_model_task.shader, 'normal')
                glEnableVertexAttribArray(nl)
                glVertexAttribPointer(nl, 3, GL_FLOAT, False, 0, None)

                glUseProgram(0)
                glBindBuffer(GL_ARRAY_BUFFER, 0)

                glBindVertexArray(0)
                glDeleteBuffers(3, buffers)

            glBindVertexArray(renderer_model_task.vao)
            glUseProgram(renderer_model_task.shader)

            # common bind
            mmatrix = multiply(self.model_view_matrix, self.perspective_matrix)

            ml = glGetUniformLocation(renderer_model_task.shader, 'mmatrix')
            glUniformMatrix4fv(ml, 1, GL_FALSE, mmatrix)

            glEnable(GL_DEPTH_TEST)

            glDrawElements(GL_TRIANGLES, len(obj.indexes), GL_UNSIGNED_INT, None)

            glUseProgram(0)
            glBindVertexArray(0)

        self.renderer_model_task = renderer_model_task
        self.updateScene.emit()

    @pyqtSlot(int, int)
    def change_rotate(self, x, y):
        self.rotate_y += x
        self.rotate_x += y

        self.model_view_matrix = multiply(create_from_eulers(create(-self.rotate_x / 180 * math.pi, 0,
                                                                    -self.rotate_y / 180 * math.pi), dtype='float32'),
                                          self.translation_matrix)
        self.updateScene.emit()

    @pyqtSlot(BSplineBody)
    def show_aux(self, is_show):
        if not self.renderer_aux_task:
            @static_var(is_show=is_show, b_spline_body=None, shader=None, vao=None)
            def draw_aux():
                if not draw_aux.b_spline_body:
                    draw_aux.b_spline_body = BSplineBody()
                    draw_aux.vao = glGenVertexArrays(1)
                    glBindVertexArray(draw_aux.vao)
                    vvbo = glGenBuffers(1)
                    glBindBuffer(GL_ARRAY_BUFFER, vvbo)
                    vertices = draw_aux.b_spline_body.point
                    glBufferData(GL_ARRAY_BUFFER, len(vertices) * 12, numpy.array(vertices, dtype='float32'), usage=GL_STATIC_DRAW)

                    draw_aux.shader = get_shader_render_program('aux.v.glsl', 'aux.f.glsl')
                    glUseProgram(draw_aux.shader)
                    vl = glGetAttribLocation(draw_aux.shader, 'vertice')
                    glEnableVertexAttribArray(vl)
                    glVertexAttribPointer(vl, 3, GL_FLOAT, False, 0, None)

                    glUseProgram(0)
                    glBindBuffer(GL_ARRAY_BUFFER, 0)
                    glBindVertexArray(0)
                    glDeleteBuffers(1, [vvbo])

                glBindVertexArray(draw_aux.vao)
                glUseProgram(draw_aux.shader)

                # common bind
                mmatrix = multiply(self.model_view_matrix, self.perspective_matrix)

                ml = glGetUniformLocation(draw_aux.shader, 'mmatrix')
                glUniformMatrix4fv(ml, 1, GL_FALSE, mmatrix)

                glEnable(GL_DEPTH_TEST)
                glEnable(GL_PROGRAM_POINT_SIZE)

                glDrawArrays(GL_POINTS, 0, 125)

                glUseProgram(0)
                glBindVertexArray(0)

            self.renderer_aux_task = draw_aux

        self.renderer_aux_task.is_show = is_show
