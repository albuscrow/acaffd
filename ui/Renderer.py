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
from util.GLUtil import bind_ssbo
from Constant import *
from shader.ShaderUtil import shader_parameter
from shader.ShaderWrapper import ModelShader


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
        self.model_shader = None
        self.renderer_aux_task = None

        self.rotate_x = 0
        self.rotate_y = 0

        self.perspective_matrix = None

        self.translation_matrix = create_from_translation(numpy.array([0, 0, -8]), dtype='float32')

        # self.model_view_matrix = multiply(create_from_eulers(create(-self.rotate_x / 180 * math.pi, 0,
        #                                                             -self.rotate_y / 180 * math.pi), dtype='float32'),
        #                                   self.translation_matrix)
        self.model_view_matrix = self.translation_matrix

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

        # if self.renderer_aux_task and self.renderer_aux_task.is_show:
        #     self.renderer_aux_task()

        if self.model_shader:
            self.model_shader.draw(self.model_view_matrix, self.perspective_matrix)
            self.updateScene.emit()

        glDisable(GL_SCISSOR_TEST)

    @pyqtSlot(OBJ)
    def handle_new_obj(self, obj):
        self.model = obj
        self.b_spline_body = BSplineBody(*self.model.get_length_xyz())
        self.model_shader = ModelShader(obj)

    @pyqtSlot(OBJ)
    def handle_new_obj2(self, obj):
        self.model = obj

        @static_var(shader=None, vao=None, deform_compute_shader=None, triangle_number=None)
        def renderer_model_task():
            global vertex_vbo, normal_vbo, index_vbo
            if not renderer_model_task.shader:
                # init program
                renderer_model_task.vao = glGenVertexArrays(1)
                glBindVertexArray(renderer_model_task.vao)

                # 原始顶点数据,也是顶点在b样条体中的参数;要满足这一条件必须使控制顶点和节点向量满足一定条件。
                # original_vertex_vbo original_normal_vbo original_index_vbo

                # 原始面片邻接关系, 共享的原始面片pn triangle
                # adjacency_vbo share_adjacency_pn_triangle_vbo

                # 用于同步
                # atomic_buffer

                # b样条体相关信息
                # bspline_body_ubo

                # 经过分割以后的数据。
                # splited_triangle_vbo

                # 加速采样后的控制顶点
                # self.control_point_for_sample_ubo

                # 经过tessellate后最终用于绘制的数据。
                # vertice_vbo
                # normal_vbo
                # index_vbo

                # create vbo
                buffers = glGenBuffers(13)
                original_vertex_vbo, original_normal_vbo, original_index_vbo, \
                adjacency_vbo, share_adjacency_pn_triangle_vbo, \
                atomic_ubo, \
                bspline_body_ubo, \
                splited_triangle_vbo, \
                self.control_point_for_sample_ubo, \
                vertex_vbo, normal_vbo, index_vbo, debug_vbo = buffers

                # copy original vertex to gpu, and bind original_vertex_vbo to bind point 0
                bind_ssbo(original_vertex_vbo, 0, obj.vertex, obj.original_vertex_number * VERTEX_SIZE, np.float32,
                          GL_STATIC_DRAW)

                # copy original normal to gpu, and bind original_normal_vbo to bind point 1
                bind_ssbo(original_normal_vbo, 1, obj.normal, obj.original_normal_number * NORMAL_SIZE, np.float32,
                          GL_STATIC_DRAW)

                # copy original index to gpu, and bind original_index_vbo to bind point 2
                bind_ssbo(original_index_vbo, 2, obj.index, obj.original_triangle_number * PER_TRIANGLE_INDEX_SIZE,
                          np.uint32, GL_STATIC_DRAW)

                # copy adjacency table to gpu, and bind adjacency_vbo to bind point 2
                bind_ssbo(adjacency_vbo, 3, obj.adjacency,
                          obj.original_triangle_number * PER_TRIANGLE_ADJACENCY_INDEX_SIZE, np.int32, GL_STATIC_DRAW)

                bind_ssbo(share_adjacency_pn_triangle_vbo, 4, None,
                          obj.original_triangle_number * PER_TRIANGLE_PN_NORMAL_TRIANGLE_SIZE, np.float32,
                          GL_DYNAMIC_DRAW)

                bind_ssbo(debug_vbo, 14, None, (2 * 9 * 6 + 1) * 16, 'float32', GL_DYNAMIC_DRAW)

                # copy BSpline body info to gpu
                bspline_body_info = self.b_spline_body.get_info()
                self.bindUBO(0, bspline_body_ubo, bspline_body_info,
                             bspline_body_info.size * bspline_body_info.itemsize)

                # init atom buffer for count splited triangle number
                self.init_atomic(atomic_ubo)

                # alloc memory in gpu for splited vertex, and
                bind_ssbo(splited_triangle_vbo, 5, None,
                          obj.original_triangle_number * MAX_SPLITED_TRIANGLE_PRE_ORIGINAL_TRIANGLE * SPLITED_TRIANGLE_SIZE,
                          np.float32, GL_DYNAMIC_DRAW)

                # run previous compute shader
                previous_compute_shader = get_compute_shader_program('previous_compute_shader_oo.glsl')
                glUseProgram(previous_compute_shader)

                glDispatchCompute(int(obj.original_triangle_number / 512 + 1), 1, 1)
                # self.print_vbo(debug_vbo, (2 * 9 * 6 + 1, 4))
                # self.print_vbo(share_adjacency_pn_triangle_vbo, (obj.original_triangle_number * PER_TRIANGLE_PN_NORMAL_TRIANGLE_SIZE / 16, 4))

                # get number of splited triangle
                renderer_model_task.triangle_number, = self.get_splited_triangle_number(atomic_ubo)

                # alloc memory in gpu for tessellated vertex
                bind_ssbo(vertex_vbo, 6, None,
                          renderer_model_task.triangle_number *
                          shader_parameter.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE,
                          np.float32, GL_DYNAMIC_DRAW)

                # alloc memory in gpu for tessellated normal
                bind_ssbo(normal_vbo, 7, None,
                          renderer_model_task.triangle_number *
                          shader_parameter.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE,
                          np.float32, GL_DYNAMIC_DRAW)

                # alloc memory in gpu for tessellated index
                bind_ssbo(index_vbo, 8, None,
                          renderer_model_task.triangle_number *
                          shader_parameter.tessellated_triangle_number_pre_splited_triangle * PER_TRIANGLE_INDEX_SIZE,
                          np.uint32, GL_DYNAMIC_DRAW)

                # copy control point info to gpu
                new_control_points = self.b_spline_body.get_control_point_for_sample()
                self.bindUBO(1, self.control_point_for_sample_ubo, new_control_points,
                             new_control_points.size * new_control_points.itemsize)

                # init compute shader before every frame
                renderer_model_task.deform_compute_shader = get_compute_shader_program('deform_compute_shader_oo.glsl')
                glProgramUniform1f(renderer_model_task.deform_compute_shader, 0, renderer_model_task.triangle_number)

                glUseProgram(renderer_model_task.deform_compute_shader)
                glDispatchCompute(int(renderer_model_task.triangle_number / 512 + 1), 1, 1)

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

                new_control_points = self.b_spline_body.get_control_point_for_sample()

                self.bindUBO(1, self.control_point_for_sample_ubo, new_control_points,
                             new_control_points.size * new_control_points.itemsize)

                # glBindBuffer(GL_UNIFORM_BUFFER, self.control_point_for_sample_ubo)
                # new_control_points = self.b_spline_body.get_control_point_for_sample()
                # glBufferSubData(GL_UNIFORM_BUFFER, 0, new_control_points.size * new_control_points.itemsize,
                #                 new_control_points)
                # glBufferData(GL_UNIFORM_BUFFER, new_control_points.size * new_control_points.itemsize,
                #              new_control_points,
                #              usage=GL_STATIC_DRAW)
                glDispatchCompute(int(renderer_model_task.triangle_number / 512 + 1), 1, 1)
                self.need_deform = False

            glUseProgram(renderer_model_task.shader)

            # common bind
            wvp_matrix = multiply(self.model_view_matrix, self.perspective_matrix)

            ml = glGetUniformLocation(renderer_model_task.shader, 'wvp_matrix')
            glUniformMatrix4fv(ml, 1, GL_FALSE, wvp_matrix)

            ml = glGetUniformLocation(renderer_model_task.shader, 'wv_matrix')
            glUniformMatrix4fv(ml, 1, GL_FALSE, self.model_view_matrix)

            glEnable(GL_DEPTH_TEST)
            glDrawElements(GL_TRIANGLES, int(
                    renderer_model_task.triangle_number * shader_parameter.tessellated_triangle_number_pre_splited_triangle * 3),
                           GL_UNSIGNED_INT, None)
            # glDrawElements(GL_TRIANGLES, int(renderer_model_task.triangle_number * 1 * 3), GL_UNSIGNED_INT, None)

            glUseProgram(0)
            glBindVertexArray(0)

        self.renderer_model_task = renderer_model_task
        self.updateScene.emit()

    @staticmethod
    def init_atomic(atomic_buffer):
        glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, atomic_buffer)
        glBufferData(GL_ATOMIC_COUNTER_BUFFER, 4, numpy.array([0], dtype='uint32'),
                     usage=GL_DYNAMIC_DRAW)
        glBindBufferBase(GL_ATOMIC_COUNTER_BUFFER, 0, atomic_buffer)
        glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, 0)

    @staticmethod
    def bindUBO(binding_point, bspline_body_buffer, data, size):
        glBindBuffer(GL_UNIFORM_BUFFER, bspline_body_buffer)
        glBufferData(GL_UNIFORM_BUFFER, size, data, usage=GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, binding_point, bspline_body_buffer)

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
        vbo_array = numpy.ctypeslib.as_array(vbo_pointer, (1,))
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
        return vbo_array

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
                    glBufferData(GL_ARRAY_BUFFER, vertices.size * vertices.itemsize, vertices,
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

                    ml = glGetUniformLocation(draw_aux.shader, 'wvp_matrix')
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
                    glBufferData(GL_ARRAY_BUFFER, vertices.size * vertices.itemsize, vertices,
                                 usage=GL_STATIC_DRAW)
                    glBindBuffer(GL_ARRAY_BUFFER, 0)
                    self.need_update_control_point = False

                # common bind
                mmatrix = multiply(self.model_view_matrix, self.perspective_matrix)

                ml = glGetUniformLocation(draw_aux.shader, 'wvp_matrix')
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
        # if self.renderer_aux_task.is_show:
        #     self.renderer_aux_task.x1 = x
        #     self.renderer_aux_task.y1 = self.h - y2
        #     self.renderer_aux_task.x2 = x2
        #     self.renderer_aux_task.y2 = self.h - y
        #     self.renderer_aux_task.need_select = True
        self.model_shader.select(x, self.h - y2, x2, self.h - y)
        self.updateScene.emit()

    @pyqtSlot(float, float, float)
    def move_control_points(self, x, y, z):
        self.model_shader.move_control_points(x, y, z)
        self.updateScene.emit()
