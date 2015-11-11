import math
import numpy
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from util.util import static_var
from model.aux import BSplineBody
from model.model import OBJ
from shader.ShaderUtil import get_compute_shader_program, get_renderer_shader_program
from OpenGL.GL import *
from pyrr.matrix44 import *
from pyrr.euler import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
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

        aspect = self.w / self.h
        self.perspective_matrix = create_perspective_projection_matrix_from_bounds(-aspect, aspect, -1, 1, 2, 100,
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
                nvbo = buffers[1]
                ivbo = buffers[2]

                # copy vertices to gpu
                glBindBuffer(GL_SHADER_STORAGE_BUFFER, vvbo)
                glBufferData(GL_SHADER_STORAGE_BUFFER, len(obj.vertices) * 12,
                             numpy.array(obj.vertices, dtype='float32'),
                             usage=GL_DYNAMIC_DRAW)
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, vvbo)

                # # copy normal to gpu
                glBindBuffer(GL_SHADER_STORAGE_BUFFER, nvbo)
                glBufferData(GL_SHADER_STORAGE_BUFFER, len(obj.normals) * 12,
                             numpy.array(obj.normals, dtype='float32'),
                             usage=GL_STATIC_DRAW)
                glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

                # # copy index to gpu
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ivbo)
                glBufferData(GL_ELEMENT_ARRAY_BUFFER, numpy.array(obj.indexes, dtype='int32'), GL_STATIC_DRAW)
                # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

                # run computer shader
                compute_shader = get_compute_shader_program('sample_bspline.glsl')
                glUseProgram(compute_shader)
                glDispatchCompute(int(len(obj.vertices) * 3 / 512 + 1), 1, 1)
                glUseProgram(0)

                # run renderer shader
                # gen renderer program
                renderer_model_task.shader = get_renderer_shader_program('vertex.glsl', 'fragment.glsl')
                glUseProgram(renderer_model_task.shader)

                # set vertice attribute
                glBindBuffer(GL_ARRAY_BUFFER, vvbo)
                # glBufferData(GL_ARRAY_BUFFER, len(obj.vertices) * 12,
                #              numpy.array(obj.vertices, dtype='float32'),
                #              usage=GL_DYNAMIC_DRAW)
                vl = glGetAttribLocation(renderer_model_task.shader, 'vertice')
                glEnableVertexAttribArray(vl)
                glVertexAttribPointer(vl, 3, GL_FLOAT, False, 0, None)

                # set normal attribute
                glBindBuffer(GL_ARRAY_BUFFER, nvbo)
                # glBufferData(GL_ARRAY_BUFFER, len(obj.normals) * 12,
                #              numpy.array(obj.normals, dtype='float32'),
                #              usage=GL_STATIC_DRAW)
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
            @static_var(is_show=is_show, b_spline_body=None, shader=None, vao=None, is_select=False, hvbo=None,
                        x1=0, y1=0, x2=0, y2=0, need_select=False)
            def draw_aux():
                if not draw_aux.b_spline_body:
                    draw_aux.b_spline_body = BSplineBody()
                    draw_aux.vao = glGenVertexArrays(1)
                    glBindVertexArray(draw_aux.vao)
                    vbos = glGenBuffers(2)

                    draw_aux.shader = get_renderer_shader_program('aux.v.glsl', 'aux.f.glsl')
                    glUseProgram(draw_aux.shader)
                    vvbo = vbos[0]
                    glBindBuffer(GL_ARRAY_BUFFER, vvbo)
                    vertices = draw_aux.b_spline_body.point
                    glBufferData(GL_ARRAY_BUFFER, len(vertices) * 12, numpy.array(vertices, dtype='float32'),
                                 usage=GL_STATIC_DRAW)
                    vl = glGetAttribLocation(draw_aux.shader, 'vertice')
                    glEnableVertexAttribArray(vl)
                    glVertexAttribPointer(vl, 3, GL_FLOAT, False, 0, None)

                    draw_aux.hvbo = vbos[1]
                    glBindBuffer(GL_ARRAY_BUFFER, draw_aux.hvbo)
                    hits = draw_aux.b_spline_body.is_hit
                    glBufferData(GL_ARRAY_BUFFER, len(hits) * 4, numpy.array(hits, dtype='float32'),
                                 usage=GL_DYNAMIC_DRAW)
                    hl = glGetAttribLocation(draw_aux.shader, 'isHit')
                    glEnableVertexAttribArray(hl)
                    glVertexAttribPointer(hl, 1, GL_FLOAT, False, 0, None)

                    glUseProgram(0)
                    glBindBuffer(GL_ARRAY_BUFFER, 0)
                    glBindVertexArray(0)
                    glDeleteBuffers(1, [vvbo])

                if not draw_aux.is_show:
                    return

                glBindVertexArray(draw_aux.vao)
                glUseProgram(draw_aux.shader)

                if draw_aux.need_select:
                    draw_aux.b_spline_body.reset_is_hit()
                    glSelectBuffer(1024)
                    glRenderMode(GL_SELECT)

                    glInitNames()
                    glPushName(0)

                    glMatrixMode(GL_PROJECTION)
                    glLoadIdentity()
                    w = draw_aux.x2 - draw_aux.x1
                    h = draw_aux.y2 - draw_aux.y1
                    if w < 10:
                        w = 10
                    if h < 10:
                        h = 10
                    gluPickMatrix((draw_aux.x1 + draw_aux.x2) / 2, (draw_aux.y1 + draw_aux.y2) / 2,
                                  w, h,
                                  glGetDoublev(GL_VIEWPORT))

                    pick_matrix = glGetDoublev(GL_PROJECTION_MATRIX)

                    mmatrix = multiply(self.model_view_matrix, multiply(self.perspective_matrix, pick_matrix))

                    ml = glGetUniformLocation(draw_aux.shader, 'mmatrix')
                    glUniformMatrix4fv(ml, 1, GL_FALSE, mmatrix)

                    glEnable(GL_DEPTH_TEST)
                    glEnable(GL_PROGRAM_POINT_SIZE)

                    for i in range(125):
                        glLoadName(i)
                        glDrawArrays(GL_POINTS, i, 1)
                    hit_info = glRenderMode(GL_RENDER)

                    for r in hit_info:
                        for select_name in r.names:
                            draw_aux.b_spline_body.is_hit[select_name] = 1

                    glBindBuffer(GL_ARRAY_BUFFER, draw_aux.hvbo)
                    glBufferSubData(GL_ARRAY_BUFFER, 0, len(draw_aux.b_spline_body.is_hit) * 4,
                                    numpy.array(draw_aux.b_spline_body.is_hit, dtype='float32'))
                    draw_aux.need_select = False

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

    @pyqtSlot(int, int, int, int)
    def select(self, x, y, x2, y2):
        if self.renderer_aux_task.is_show:
            self.renderer_aux_task.x1 = x
            self.renderer_aux_task.y1 = self.h - y2
            self.renderer_aux_task.x2 = x2
            self.renderer_aux_task.y2 = self.h - y
            self.renderer_aux_task.need_select = True
        self.updateScene.emit()
