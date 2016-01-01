import threading

import numpy
from model.aux import BSplineBody
from pyrr.matrix44 import *
from OpenGL.GLU import *
from util.GLUtil import *
from Constant import *
from shader.ShaderWrapper import PrevComputeProgramWrap, DeformComputeProgramWrap, DrawProgramWrap

class GLProxy:
    def __init__(self, model):
        self.model = model
        self.b_spline_body = BSplineBody(*self.model.get_length_xyz())

        self.model_vao = None
        self.splited_triangle_number = 0
        self.previous_compute_shader = None
        self.deform_compute_shader = None
        self.model_renderer_shader = None
        self.need_deform = False
        self.counter = None
        self.control_point_for_sample_ubo = None

        self.b_spline_body_vao = None
        self.b_spline_body_renderer_shader = None
        self.b_spline_body_ubo = None
        self.control_point_vertex_vbo = None
        self.control_point_color_vbo = None
        self.is_inited = False
        self.need_update_control_point = False
        self.need_select = False
        self.tessellation_factor_is_change = False
        self._show_control_point = True

        self.vertex_vbo = None
        self.normal_vbo = None
        self.index_vbo = None

        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None

        self.task = []
        self.lock = threading.Lock()

    def draw(self, model_view_matrix, perspective_matrix):
        if not self.is_inited:
            self.init_gl()

        with self.lock:
            for t in self.task:
                t()
            self.task.clear()

        self.deform_and_draw_model(model_view_matrix, perspective_matrix)
        self.draw_b_spline(model_view_matrix, perspective_matrix)

    def init_gl(self):
        # init code for openGL

        # create vbo
        self.load_model_to_gpu_and_init_some_fix_buffer_in_gpu()
        # copy BSpline body info to gpu
        self.load_b_spline_body_to_gpu()
        # prev compute and get number of splited triangle
        self.prev_computer()
        self.init_renderer_model_buffer()

        self.init_renderer_b_spline_buffer()

        self.is_inited = True

    def init_renderer_b_spline_buffer(self):
        if self.b_spline_body_vao is None:
            self.b_spline_body_vao = glGenVertexArrays(1)
            glBindVertexArray(self.b_spline_body_vao)

            self.b_spline_body_renderer_shader = DrawProgramWrap('aux.v.glsl', 'aux.f.glsl')
            glUseProgram(self.b_spline_body_renderer_shader.get_program())

            vbos = glGenBuffers(2)
            self.control_point_vertex_vbo = vbos[0]
            glBindBuffer(GL_ARRAY_BUFFER, self.control_point_vertex_vbo)
            vertices = self.b_spline_body.ctrlPoints
            glBufferData(GL_ARRAY_BUFFER, vertices.size * vertices.itemsize, vertices,
                        usage=GL_STATIC_DRAW)
            vl = glGetAttribLocation(self.b_spline_body_renderer_shader.get_program(), 'vertice')
            glEnableVertexAttribArray(vl)
            glVertexAttribPointer(vl, 3, GL_FLOAT, False, 0, None)

            self.control_point_color_vbo = vbos[1]
            glBindBuffer(GL_ARRAY_BUFFER, self.control_point_color_vbo)
            hits = self.b_spline_body.is_hit
            glBufferData(GL_ARRAY_BUFFER, len(hits) * 4, numpy.array(hits, dtype='float32'),
                         usage=GL_DYNAMIC_DRAW)
            hl = glGetAttribLocation(self.b_spline_body_renderer_shader.get_program(), 'isHit')
            glEnableVertexAttribArray(hl)
            glVertexAttribPointer(hl, 1, GL_FLOAT, False, 0, None)
            glUseProgram(0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)
        else:
            glBindVertexArray(self.b_spline_body_vao)

            glBindBuffer(GL_ARRAY_BUFFER, self.control_point_vertex_vbo)
            vertices = self.b_spline_body.ctrlPoints
            glBufferData(GL_ARRAY_BUFFER, vertices.size * vertices.itemsize, vertices,
                         usage=GL_STATIC_DRAW)

            glBindBuffer(GL_ARRAY_BUFFER, self.control_point_color_vbo)
            hits = self.b_spline_body.is_hit
            glBufferData(GL_ARRAY_BUFFER, len(hits) * 4, numpy.array(hits, dtype='float32'),
                         usage=GL_DYNAMIC_DRAW)

            glBindVertexArray(0)

    def draw_b_spline(self, model_view_matrix, perspective_matrix):
        if not self._show_control_point:
            return
        glBindVertexArray(self.b_spline_body_vao)
        glUseProgram(self.b_spline_body_renderer_shader.get_program())
        if self.need_select:
            self.select_control_point(model_view_matrix, perspective_matrix)
        if self.need_update_control_point:
            glBindBuffer(GL_ARRAY_BUFFER, self.control_point_vertex_vbo)
            vertices = self.b_spline_body.ctrlPoints
            glBufferData(GL_ARRAY_BUFFER, vertices.size * vertices.itemsize, vertices,
                         usage=GL_STATIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            self.need_update_control_point = False

        # common bind
        mmatrix = multiply(model_view_matrix, perspective_matrix)
        ml = glGetUniformLocation(self.b_spline_body_renderer_shader.get_program(), 'wvp_matrix')
        glUniformMatrix4fv(ml, 1, GL_FALSE, mmatrix)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_PROGRAM_POINT_SIZE)
        glDrawArrays(GL_POINTS, 0, self.b_spline_body.get_control_point_number())
        glUseProgram(0)
        glBindVertexArray(0)

    def select_control_point(self, model_view_matrix, perspective_matrix):
        self.b_spline_body.reset_is_hit()
        glSelectBuffer(1024)
        glRenderMode(GL_SELECT)
        glInitNames()
        glPushName(0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        w = self.x2 - self.x1
        h = self.y2 - self.y1
        if w < 10:
            w = 10
        if h < 10:
            h = 10
        gluPickMatrix((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2,
                      w, h,
                      glGetDoublev(GL_VIEWPORT))
        pick_matrix = glGetDoublev(GL_PROJECTION_MATRIX)
        mmatrix = multiply(model_view_matrix, multiply(perspective_matrix, pick_matrix))
        ml = glGetUniformLocation(self.b_spline_body_renderer_shader.get_program(), 'wvp_matrix')
        glUniformMatrix4fv(ml, 1, GL_FALSE, mmatrix)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_PROGRAM_POINT_SIZE)
        for i in range(self.b_spline_body.get_control_point_number()):
            glLoadName(i)
            glDrawArrays(GL_POINTS, i, 1)
        hit_info = glRenderMode(GL_RENDER)
        for r in hit_info:
            for select_name in r.names:
                self.b_spline_body.is_hit[select_name] = True
        glBindBuffer(GL_ARRAY_BUFFER, self.control_point_color_vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, len(self.b_spline_body.is_hit) * 4,
                        numpy.array(self.b_spline_body.is_hit, dtype='float32'))
        self.need_select = False

    def deform_and_draw_model(self, model_view_matrix, perspective_matrix):
        glBindVertexArray(self.model_vao)
        # if control points is change, run deform compute shader
        if self.need_deform:
            if self.tessellation_factor_is_change:
                self.bind_model_buffer(self.index_vbo, self.normal_vbo, self.vertex_vbo)
            glUseProgram(self.deform_compute_shader.get_program())
            new_control_points = self.b_spline_body.get_control_point_for_sample()
            bind_ubo(self.control_point_for_sample_ubo, 1, new_control_points,
                     new_control_points.size * new_control_points.itemsize)
            glDispatchCompute(int(self.splited_triangle_number / 512 + 1), 1, 1)
            self.need_deform = False
        glUseProgram(self.model_renderer_shader.get_program())
        # common bind
        wvp_matrix = multiply(model_view_matrix, perspective_matrix)
        ml = glGetUniformLocation(self.model_renderer_shader.get_program(), 'wvp_matrix')
        glUniformMatrix4fv(ml, 1, GL_FALSE, wvp_matrix)
        ml = glGetUniformLocation(self.model_renderer_shader.get_program(), 'wv_matrix')
        glUniformMatrix4fv(ml, 1, GL_FALSE, model_view_matrix)
        glEnable(GL_DEPTH_TEST)
        glDrawElements(GL_TRIANGLES, int(
                self.splited_triangle_number *
                self.deform_compute_shader.tessellated_triangle_number_pre_splited_triangle * 3),
                       GL_UNSIGNED_INT, None)
        # glDrawElements(GL_TRIANGLES, int(renderer_model_task.triangle_number * 1 * 3), GL_UNSIGNED_INT, None)
        glUseProgram(0)
        glBindVertexArray(0)

    def init_renderer_model_buffer(self):
        # 加速采样后的控制顶点
        # self.control_point_for_sample_ubo

        # 经过tessellate后最终用于绘制的数据。
        # vertice_vbo
        # normal_vbo
        # index_vbo

        if self.model_vao is None:
            self.model_vao = glGenVertexArrays(1)
            glBindVertexArray(self.model_vao)
            buffers = glGenBuffers(4)
            self.control_point_for_sample_ubo, self.vertex_vbo, self.normal_vbo, self.index_vbo = buffers

        else:
            glBindVertexArray(self.model_vao)

        self.deform_compute_shader = DeformComputeProgramWrap('deform_compute_shader_oo.glsl',
                                                              self.splited_triangle_number, self.b_spline_body)
        self.bind_model_buffer(self.index_vbo, self.normal_vbo, self.vertex_vbo)
        # copy control point info to gpu
        new_control_points = self.b_spline_body.get_control_point_for_sample()
        bind_ubo(self.control_point_for_sample_ubo, 1, new_control_points,
                 new_control_points.size * new_control_points.itemsize)
        # init compute shader before every frame
        glUseProgram(self.deform_compute_shader.get_program())
        glDispatchCompute(int(self.splited_triangle_number / 512 + 1), 1, 1)
        # check compute result
        # self.print_vbo(normal_vbo, len(obj.normal) / 4)
        # run renderer shader
        # gen renderer program
        if self.model_renderer_shader is None:
            self.model_renderer_shader = DrawProgramWrap('vertex.glsl', 'fragment.glsl')
            glUseProgram(self.model_renderer_shader.get_program())
            # set vertice attribute
            glBindBuffer(GL_ARRAY_BUFFER, self.vertex_vbo)
            vertex_location = 0
            glEnableVertexAttribArray(vertex_location)
            glVertexAttribPointer(vertex_location, 4, GL_FLOAT, False, 0, None)
            # set normal attribute
            glBindBuffer(GL_ARRAY_BUFFER, self.normal_vbo)
            normal_location = 1
            glEnableVertexAttribArray(normal_location)
            glVertexAttribPointer(normal_location, 4, GL_FLOAT, False, 0, None)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            # specific index buffer
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_vbo)
            # unbind program
            glUseProgram(0)
        glBindVertexArray(0)

    def bind_model_buffer(self, index_vbo, normal_vbo, vertex_vbo):
        # alloc memory in gpu for tessellated vertex
        bind_ssbo(vertex_vbo, 6, None,
                  self.splited_triangle_number *
                  self.deform_compute_shader.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE,
                  np.float32, GL_DYNAMIC_DRAW)
        # alloc memory in gpu for tessellated normal
        bind_ssbo(normal_vbo, 7, None,
                  self.splited_triangle_number *
                  self.deform_compute_shader.tessellated_point_number_pre_splited_triangle * VERTEX_SIZE,
                  np.float32, GL_DYNAMIC_DRAW)
        # alloc memory in gpu for tessellated index
        bind_ssbo(index_vbo, 8, None,
                  self.splited_triangle_number *
                  self.deform_compute_shader.tessellated_triangle_number_pre_splited_triangle * PER_TRIANGLE_INDEX_SIZE,
                  np.uint32, GL_DYNAMIC_DRAW)

    def load_b_spline_body_to_gpu(self):
        # b样条体相关信息
        if not self.b_spline_body_ubo:
            self.b_spline_body_ubo = glGenBuffers(1)
        bspline_body_info = self.b_spline_body.get_info()
        bind_ubo(self.b_spline_body_ubo, 0, bspline_body_info,
                 bspline_body_info.size * bspline_body_info.itemsize)

    def load_model_to_gpu_and_init_some_fix_buffer_in_gpu(self):
        buffers = glGenBuffers(6)

        # 原始顶点数据,也是顶点在b样条体中的参数;要满足这一条件必须使控制顶点和节点向量满足一定条件。
        # original_vertex_vbo original_normal_vbo original_index_vbo
        # 原始面片邻接关系, 共享的原始面片pn triangle
        # adjacency_vbo share_adjacency_pn_triangle_vbo
        # 经过分割以后的数据。
        # splited_triangle_vbo
        original_vertex_vbo, original_normal_vbo, original_index_vbo, adjacency_vbo, share_adjacency_pn_triangle_vbo, \
        splited_triangle_vbo = buffers

        # copy original vertex to gpu, and bind original_vertex_vbo to bind point 0
        bind_ssbo(original_vertex_vbo, 0, self.model.vertex, self.model.original_vertex_number * VERTEX_SIZE,
                  np.float32,
                  GL_STATIC_DRAW)
        # copy original normal to gpu, and bind original_normal_vbo to bind point 1
        bind_ssbo(original_normal_vbo, 1, self.model.normal, self.model.original_normal_number * NORMAL_SIZE,
                  np.float32,
                  GL_STATIC_DRAW)
        # copy original index to gpu, and bind original_index_vbo to bind point 2
        bind_ssbo(original_index_vbo, 2, self.model.index,
                  self.model.original_triangle_number * PER_TRIANGLE_INDEX_SIZE,
                  np.uint32, GL_STATIC_DRAW)
        # copy adjacency table to gpu, and bind adjacency_vbo to bind point 2
        bind_ssbo(adjacency_vbo, 3, self.model.adjacency,
                  self.model.original_triangle_number * PER_TRIANGLE_ADJACENCY_INDEX_SIZE, np.int32, GL_STATIC_DRAW)
        # 用于储存原始三角面片的PN-triangle
        bind_ssbo(share_adjacency_pn_triangle_vbo, 4, None,
                  self.model.original_triangle_number * PER_TRIANGLE_PN_NORMAL_TRIANGLE_SIZE, np.float32,
                  GL_DYNAMIC_DRAW)

        # alloc memory in gpu for splited vertex, and
        bind_ssbo(splited_triangle_vbo, 5, None,
                  self.model.original_triangle_number * MAX_SPLITED_TRIANGLE_PRE_ORIGINAL_TRIANGLE *
                  SPLITED_TRIANGLE_SIZE,
                  np.float32, GL_DYNAMIC_DRAW)

    def prev_computer(self):
        # 用于同步
        # self.prev_computer.counter
        if self.counter is None:
            self.counter = glGenBuffers(1)

        # init atom buffer for count splited triangle number
        set_atomic_value(self.counter, 0)

        # run previous compute shader
        if self.previous_compute_shader is None:
            self.previous_compute_shader = PrevComputeProgramWrap('previous_compute_shader_oo.glsl')
        glUseProgram(self.previous_compute_shader.get_program())
        # prev computer
        glDispatchCompute(int(self.model.original_triangle_number / 512 + 1), 1, 1)
        self.splited_triangle_number = get_atomic_value(self.counter)

    def set_select_region(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.need_select = True

    def move_control_points(self, x, y, z):
        self.b_spline_body.move(x, y, z)
        self.need_update_control_point = True
        self.need_deform = True

    def change_tessellation_level(self, level):
        self.deform_compute_shader.tessellation_factor = level
        self.need_deform = True
        self.tessellation_factor_is_change = True

    def change_control_point(self, u, v, w):
        self.b_spline_body.change_control_point(u, v, w)

        with self.lock:
            self.task.append(self.load_b_spline_body_to_gpu)
            self.task.append(self.prev_computer)
            self.task.append(self.init_renderer_model_buffer)
            self.task.append(self.init_renderer_b_spline_buffer)


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