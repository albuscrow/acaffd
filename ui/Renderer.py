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
from util.GLUtil import bindSSBO


class Renderer(QObject):
    updateScene = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.need_update_control_point = False
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

        self.translation_matrix = create_from_translation(numpy.array([0, 0, -4.7]), dtype='float32')

        self.model_view_matrix = multiply(create_from_eulers(create(-self.rotate_x / 180 * math.pi, 0,
                                                                    -self.rotate_y / 180 * math.pi), dtype='float32'),
                                          self.translation_matrix)
        self.model = None
        self.b_spline_body = None
        self.need_deform = False

    def set_view_port(self, x, y, w, h):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

        aspect = self.w / self.h
        self.perspective_matrix = create_perspective_projection_matrix_from_bounds(-aspect, aspect, -1,
                                                                                   1, 4, 100,
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

        if self.renderer_aux_task and self.renderer_aux_task.is_show:
            self.renderer_aux_task()

        if self.renderer_model_task:
            self.renderer_model_task()

        glDisable(GL_SCISSOR_TEST)

    @pyqtSlot(OBJ)
    def handle_new_obj(self, obj):
        self.model = obj

        @static_var(shader=None, vao=None, deform_compute_shader=None, triangle_number=None)
        def renderer_model_task():
            global vertex_vbo, normal_vbo, index_vbo
            if not renderer_model_task.shader:
                # init program
                renderer_model_task.vao = glGenVertexArrays(1)
                glBindVertexArray(renderer_model_task.vao)

                # 原始顶点数据,也是顶点在b样条体中的参数;要满足这一条件必须使控制顶点和节点向量满足一定条件。
                # original_vertex_vbo
                # original_normal_vbo
                # original_index_vbo

                # 经过分割以后的数据。
                # splited_vertex_vbo
                # splited_normal_vbo
                # splited_index_vbo

                # 经过tessellate后最终用于绘制的数据。
                # vertice_vbo
                # normal_vbo
                # index_vbo

                # create vbo
                buffers = glGenBuffers(14)
                original_vertex_vbo, original_normal_vbo, original_index_vbo, adjacency_vbo, \
                atomic_buffer, bspline_body_buffer, \
                splited_vertex_vbo, splited_normal_vbo, splited_index_vbo, splited_bspline_info_vbo, \
                vertex_vbo, normal_vbo, index_vbo, debug_vbo = buffers

                # copy original vertex to gpu, and bind original_vertex_vbo to bind point 0
                bindSSBO(original_vertex_vbo, 0, obj.vertex, len(obj.vertex) * 16, 'float32', GL_STATIC_DRAW)

                # copy original normal to gpu, and bind original_normal_vbo to bind point 1
                bindSSBO(original_normal_vbo, 1, obj.normal, len(obj.normal) * 16, 'float32', GL_STATIC_DRAW)

                # copy original index to gpu, and bind original_index_vbo to bind point 2
                bindSSBO(original_index_vbo, 2, obj.index, len(obj.index) * 4, 'uint32', GL_STATIC_DRAW)
                print(len(obj.index) * 4)

                # copy adjacency table to gpu, and bind adjacency_vbo to bind point 2
                bindSSBO(adjacency_vbo, 11, obj.adjacency, len(obj.adjacency) * 12, 'int32', GL_STATIC_DRAW)
                print(len(obj.adjacency) * 12)

                bindSSBO(debug_vbo, 12, None, 16 * 10, 'float32', GL_DYNAMIC_DRAW)

                # self.print_vbo(original_vertex_vbo, (3, 4))
                # self.print_vbo(original_normal_vbo, (3, 4))
                # self.print_vbo(original_index_vbo, (1, 3), data_type=ctypes.c_uint32)

                # copy BSpline body info to gpu
                glBindBuffer(GL_UNIFORM_BUFFER, bspline_body_buffer)
                data = self.b_spline_body.get_info()
                glBufferData(GL_UNIFORM_BUFFER, len(data) * 4, data, usage=GL_STATIC_DRAW)
                glBindBufferBase(GL_UNIFORM_BUFFER, 0, bspline_body_buffer)

                # init atom buffer for count splited triangle number
                glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, atomic_buffer)
                glBufferData(GL_ATOMIC_COUNTER_BUFFER, 8, numpy.array([0, 0], dtype='uint32'),
                             usage=GL_DYNAMIC_DRAW)
                glBindBufferBase(GL_ATOMIC_COUNTER_BUFFER, 0, atomic_buffer)
                glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, 0)

                # alloc memory in gpu for splited vertex, and
                bindSSBO(splited_vertex_vbo, 3, None, len(obj.vertex) * 16 * 50, 'float32', GL_DYNAMIC_DRAW)

                # alloc memory in gpu for splited normal
                bindSSBO(splited_normal_vbo, 4, None, len(obj.normal) * 16 * 50, 'float32', GL_DYNAMIC_DRAW)

                # alloc memory in gpu for splited index
                bindSSBO(splited_index_vbo, 5, None, len(obj.index) * 4 * 50, 'uint32', GL_DYNAMIC_DRAW)

                # alloc memory in gpu for bspline info
                bindSSBO(splited_bspline_info_vbo, 10, None, len(obj.vertex) * 48 * 50, 'uint32', GL_DYNAMIC_DRAW)

                # run previous compute shader
                previous_compute_shader = get_compute_shader_program('previous_compute_shader.glsl')
                glUseProgram(previous_compute_shader)

                # self.print_vbo(debug_vbo, (10, 4))
                glDispatchCompute(int(len(obj.index) / 3 / 512 + 1), 1, 1)

                # self.print_vbo(splited_vertex_vbo, (8, 4))
                # self.print_vbo(splited_normal_vbo, (4, 4))
                # self.print_vbo(splited_index_vbo, (10, 3), data_type=ctypes.c_uint32)
                # self.print_vbo(splited_bspline_info_vbo, (4 * 3, 4))
                self.print_vbo(debug_vbo, (10, 4))

                # get number of splited triangle
                renderer_model_task.triangle_number, point_number = self.get_splited_triangle_number(atomic_buffer)

                # alloc memory in gpu for tessellated vertex
                bindSSBO(vertex_vbo, 6, None, point_number * 16, 'float32', GL_DYNAMIC_DRAW)

                # alloc memory in gpu for tessellated normal
                bindSSBO(normal_vbo, 7, None, point_number * 16, 'float32', GL_DYNAMIC_DRAW)

                # alloc memory in gpu for tessellated index
                bindSSBO(index_vbo, 8, None, renderer_model_task.triangle_number * 12, 'uint32', GL_DYNAMIC_DRAW)

                # init compute shader before every frame
                renderer_model_task.deform_compute_shader = get_compute_shader_program('deform_compute_shader.glsl')
                glProgramUniform1f(renderer_model_task.deform_compute_shader, 0, renderer_model_task.triangle_number)
                glUseProgram(renderer_model_task.deform_compute_shader)
                glUniform3fv(1, len(self.b_spline_body.ctrlPoints), numpy.array(self.b_spline_body.ctrlPoints, dtype='float32'))
                glDispatchCompute(int(renderer_model_task.triangle_number / 512 + 1), 1, 1)

                # self.print_vbo(vertex_vbo, (4, 4))
                # self.print_vbo(normal_vbo, (4, 4))
                # self.print_vbo(index_vbo, (2, 3), data_type=ctypes.c_uint32)

                # check compute result
                # self.print_vbo(normal_vbo, len(obj.normal) / 4)

                # run renderer shader
                # gen renderer program
                renderer_model_task.shader = get_renderer_shader_program('vertex.glsl', 'fragment.glsl')
                glUseProgram(renderer_model_task.shader)

                # set vertice attribute
                glBindBuffer(GL_ARRAY_BUFFER, vertex_vbo)
                vertex_location = 0
                glEnableVertexAttribArray(vertex_location)
                glVertexAttribPointer(vertex_location, 4, GL_FLOAT, False, 0, None)

                # set normal attribute
                glBindBuffer(GL_ARRAY_BUFFER, normal_vbo)
                normal_location = 1
                glEnableVertexAttribArray(normal_location)
                glVertexAttribPointer(normal_location, 4, GL_FLOAT, False, 0, None)
                glBindBuffer(GL_ARRAY_BUFFER, 0)

                # specific index buffer
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, index_vbo)

                # unbind program
                glUseProgram(0)

                glBindVertexArray(0)
                # glDeleteBuffers(9, buffers)

            # sample and tessellate
            glBindVertexArray(renderer_model_task.vao)

            # if control points is change, run deform compute shader
            if self.need_deform:
                glUseProgram(renderer_model_task.deform_compute_shader)
                glUniform3fv(1, len(self.b_spline_body.ctrlPoints), numpy.array(self.b_spline_body.ctrlPoints, dtype='float32'))
                glDispatchCompute(int(renderer_model_task.triangle_number / 512 + 1), 1, 1)
                self.need_deform = False

            glUseProgram(renderer_model_task.shader)

            # common bind
            wvp_matrix = multiply(self.model_view_matrix, self.perspective_matrix)

            ml = glGetUniformLocation(renderer_model_task.shader, 'wvp_matrix')
            glUniformMatrix4fv(ml, 1, GL_FALSE, wvp_matrix)

            glEnable(GL_DEPTH_TEST)

            glDrawElements(GL_TRIANGLES, renderer_model_task.triangle_number * 3, GL_UNSIGNED_INT, None)
            # glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_INT, None)

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

    @staticmethod
    def get_splited_triangle_number(atomic_buffer):
        glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, atomic_buffer)
        pointer_to_buffer = glMapBuffer(GL_ATOMIC_COUNTER_BUFFER, GL_READ_ONLY)
        vbo_pointer = ctypes.cast(pointer_to_buffer, ctypes.POINTER(ctypes.c_uint32))
        vbo_array = numpy.ctypeslib.as_array(vbo_pointer, (2,))
        glUnmapBuffer(GL_ATOMIC_COUNTER_BUFFER)
        return vbo_array

    @staticmethod
    def print_vbo(vbo_name, shape, data_type=ctypes.c_float):
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, vbo_name)
        pointer_to_buffer = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
        vbo_pointer = ctypes.cast(pointer_to_buffer, ctypes.POINTER(data_type))
        # Turn that pointer into a numpy array that spans
        # the whole block.(buffer size is the size of your buffer)
        vbo_array = numpy.ctypeslib.as_array(vbo_pointer, shape)
        #
        for data in vbo_array:
            print(data)
        glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

    @pyqtSlot(BSplineBody)
    def show_aux(self, is_show):
        if not self.renderer_aux_task:
            @static_var(is_show=is_show, shader=None, vao=None, is_select=False, hvbo=None, vvbo=None,
                        x1=0, y1=0, x2=0, y2=0, need_select=False)
            def draw_aux():
                if not self.b_spline_body:
                    self.b_spline_body = BSplineBody(*self.model.get_length_xyz())
                    draw_aux.vao = glGenVertexArrays(1)
                    glBindVertexArray(draw_aux.vao)
                    vbos = glGenBuffers(2)

                    draw_aux.shader = get_renderer_shader_program('aux.v.glsl', 'aux.f.glsl')
                    glUseProgram(draw_aux.shader)
                    draw_aux.vvbo = vbos[0]
                    glBindBuffer(GL_ARRAY_BUFFER, draw_aux.vvbo)
                    vertices = self.b_spline_body.ctrlPoints
                    glBufferData(GL_ARRAY_BUFFER, len(vertices) * 12, numpy.array(vertices, dtype='float32'),
                                 usage=GL_STATIC_DRAW)
                    vl = glGetAttribLocation(draw_aux.shader, 'vertice')
                    glEnableVertexAttribArray(vl)
                    glVertexAttribPointer(vl, 3, GL_FLOAT, False, 0, None)

                    draw_aux.hvbo = vbos[1]
                    glBindBuffer(GL_ARRAY_BUFFER, draw_aux.hvbo)
                    hits = self.b_spline_body.is_hit
                    glBufferData(GL_ARRAY_BUFFER, len(hits) * 4, numpy.array(hits, dtype='float32'),
                                 usage=GL_DYNAMIC_DRAW)
                    hl = glGetAttribLocation(draw_aux.shader, 'isHit')
                    glEnableVertexAttribArray(hl)
                    glVertexAttribPointer(hl, 1, GL_FLOAT, False, 0, None)

                    glUseProgram(0)
                    glBindBuffer(GL_ARRAY_BUFFER, 0)
                    glBindVertexArray(0)

                if not draw_aux.is_show:
                    return

                glBindVertexArray(draw_aux.vao)
                glUseProgram(draw_aux.shader)

                if draw_aux.need_select:
                    self.b_spline_body.reset_is_hit()
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
                            self.b_spline_body.is_hit[select_name] = True

                    glBindBuffer(GL_ARRAY_BUFFER, draw_aux.hvbo)
                    glBufferSubData(GL_ARRAY_BUFFER, 0, len(self.b_spline_body.is_hit) * 4,
                                    numpy.array(self.b_spline_body.is_hit, dtype='float32'))
                    draw_aux.need_select = False

                if self.need_update_control_point:
                    glBindBuffer(GL_ARRAY_BUFFER, draw_aux.vvbo)
                    vertices = self.b_spline_body.ctrlPoints
                    glBufferData(GL_ARRAY_BUFFER, len(vertices) * 12, numpy.array(vertices, dtype='float32'),
                                 usage=GL_STATIC_DRAW)
                    glBindBuffer(GL_ARRAY_BUFFER, 0)
                    self.need_update_control_point = False;

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

    @pyqtSlot(float, float, float)
    def move_control_points(self, x, y, z):
        self.b_spline_body.move(x, y, z)
        self.need_update_control_point = True
        self.need_deform = True
