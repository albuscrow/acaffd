import threading

import numpy

from mvc_model.GLObject import ACVBO
from mvc_model.aux import BSplineBody
from pyrr.matrix44 import *
from OpenGL.GLU import *
from util.GLUtil import *
from Constant import *
from ac_opengl.shader.ShaderWrapper import PrevComputeProgramWrap, DeformComputeProgramWrap, DrawProgramWrap


class GLProxy:
    def __init__(self, model):
        self._tessellation_factor = 3
        self._tessellated_point_number_pre_splited_triangle = (self._tessellation_factor + 1) * (
            self._tessellation_factor + 2) / 2
        self._tessellated_triangle_number_pre_splited_triangle = self._tessellation_factor * self._tessellation_factor

        self.model = model
        self.b_spline_body = BSplineBody(*self.model.get_length_xyz())

        self.model_vao = None
        self.splited_triangle_number = 0
        self.previous_compute_shader = None
        self.deform_compute_shader = None
        self.model_renderer_shader = None
        self.need_deform = False

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

        self.vertex_vbo = None  # type: ACVBO
        self.normal_vbo = None  # type: ACVBO
        self.index_vbo = None  # type: ACVBO

        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None

        self.task = []
        self.lock = threading.Lock()

        self.original_vertex_ssbo = None
        self.original_normal_ssbo = None
        self.original_index_ssbo = None
        self.adjacency_info_ssbo = None
        self.share_adjacency_pn_triangle_ssbo = None
        self.splited_triangle_ssbo = None
        self.splited_triangle_counter_acbo = None
        self.control_point_for_sample_ubo = None

    def draw(self, model_view_matrix, perspective_matrix):
        if not self.is_inited:
            self.gl_init_global()

        with self.lock:
            for t in self.task:
                t()
            self.task.clear()

        self.deform_and_draw_model(model_view_matrix, perspective_matrix)
        self.draw_b_spline(model_view_matrix, perspective_matrix)

    def gl_init_global(self):
        # init code for openGL
        # create ssbo
        # 原始顶点数据,也是顶点在b样条体中的参数;要满足这一条件必须使控制顶点和节点向量满足一定条件。
        # original_vertex_ssbo original_normal_ssbo original_index_ssbo
        # 原始面片邻接关系, 共享的原始面片pn triangle
        # adjacency_ssbo share_adjacency_pn_triangle_ssbo
        # 经过分割以后的数据。
        # splited_triangle_ssbo
        # B spline body 的信息。
        # b_spline_body_ubo
        self.original_vertex_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 0, None, GL_STATIC_DRAW)
        self.original_normal_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 1, self.model.normal, GL_STATIC_DRAW)
        self.original_index_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 2, None, GL_STATIC_DRAW)
        self.adjacency_info_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 3, None, GL_STATIC_DRAW)
        self.share_adjacency_pn_triangle_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 4, None, GL_STATIC_DRAW)
        self.splited_triangle_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 5, None, GL_STATIC_DRAW)
        self.b_spline_body_ubo = ACVBO(GL_UNIFORM_BUFFER, 0, None, GL_STATIC_DRAW)

        # 分割后三角形的计数器
        self.splited_triangle_counter_acbo = ACVBO(GL_ATOMIC_COUNTER_BUFFER, 0, None, GL_DYNAMIC_DRAW)

        # 变形要用到的buffer
        # 加速采样后的控制顶点
        self.control_point_for_sample_ubo = ACVBO(GL_UNIFORM_BUFFER, 1, None, GL_DYNAMIC_DRAW)

        # 经过tessellate后最终用于绘制的数据。
        # vertice_vbo
        # normal_vbo
        # index_vbo
        self.vertex_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 6, None, GL_DYNAMIC_DRAW)
        self.normal_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 7, None, GL_DYNAMIC_DRAW)
        self.index_vbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 8, None, GL_DYNAMIC_DRAW)
        self.model_vao = glGenVertexArrays(1)
        glBindVertexArray(self.model_vao)
        # set vertice attribute
        self.vertex_vbo.as_array_buffer(0, 4, GL_FLOAT)
        # set normal attribute
        self.normal_vbo.as_array_buffer(1, 4, GL_FLOAT)
        # specific index buffer
        self.index_vbo.as_element_array_buffer()
        # unbind program
        glBindVertexArray(0)
        # self.bind_model_buffer(self.index_vbo, self.normal_vbo, self.vertex_vbo)

        # init previous compute shader
        self.previous_compute_shader = PrevComputeProgramWrap('previous_compute_shader_oo.glsl')

        self.gl_init_for_model()

        self.model_renderer_shader = DrawProgramWrap('vertex.glsl', 'fragment.glsl')

        self.deform_compute_shader = DeformComputeProgramWrap('deform_compute_shader_oo.glsl',
                                                              self.splited_triangle_number, self.b_spline_body)
        self.need_deform = True

        # buffer for b_spline
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

        self.is_inited = True

    def gl_init_for_model(self) -> None:
        # alloc memory in gpu for splited vertex
        self.original_vertex_ssbo.async_update(self.model.vertex)
        self.original_vertex_ssbo.gl_sync()
        # copy original vertex to gpu, and bind original_vertex_vbo to bind point 0
        self.original_normal_ssbo.async_update(self.model.normal)
        self.original_normal_ssbo.gl_sync()
        # copy original normal to gpu, and bind original_normal_vbo to bind point 1
        self.original_index_ssbo.async_update(self.model.index)
        self.original_index_ssbo.gl_sync()
        # copy original index to gpu, and bind original_index_vbo to bind point 2
        self.adjacency_info_ssbo.async_update(self.model.adjacency)
        self.adjacency_info_ssbo.gl_sync()
        # copy adjacency table to gpu, and bind adjacency_vbo to bind point 3
        self.share_adjacency_pn_triangle_ssbo.capacity = self.model.original_triangle_number * PER_TRIANGLE_PN_NORMAL_TRIANGLE_SIZE
        self.share_adjacency_pn_triangle_ssbo.gl_sync()
        # 用于储存原始三角面片的PN-triangle
        self.splited_triangle_ssbo.capacity = self.model.original_triangle_number * MAX_SPLITED_TRIANGLE_PRE_ORIGINAL_TRIANGLE * SPLITED_TRIANGLE_SIZE
        self.splited_triangle_ssbo.gl_sync()
        # b_spline_body相关信息
        self.gl_init_for_b_spline()

        # 预计算（分割三角形） 初始化下列buffer的时候需要用到分割后的三角形，所以要先分割
        self.prev_computer()

        # alloc memory in gpu for tessellated vertex
        self.vertex_vbo.capacity = self.splited_triangle_number * self._tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
        self.vertex_vbo.gl_sync()
        # alloc memory in gpu for tessellated normal
        self.normal_vbo.capacity = self.splited_triangle_number * self._tessellated_point_number_pre_splited_triangle * VERTEX_SIZE
        self.normal_vbo.gl_sync()
        # alloc memory in gpu for tessellated index
        self.index_vbo.capacity = self.splited_triangle_number \
                                  * self._tessellated_triangle_number_pre_splited_triangle * PER_TRIANGLE_INDEX_SIZE
        self.index_vbo.gl_sync()

    def gl_init_for_b_spline(self):
        # init b_spline_body_ubo copy BSpline body info to gpu
        self.b_spline_body_ubo.async_update(self.b_spline_body.get_info())
        self.b_spline_body_ubo.gl_sync()
        # init control_point_for_sample_ubo
        self.control_point_for_sample_ubo.async_update(self.b_spline_body.get_control_point_for_sample())
        self.control_point_for_sample_ubo.gl_sync()

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
            self.control_point_for_sample_ubo.async_update(self.b_spline_body.get_control_point_for_sample())
            self.control_point_for_sample_ubo.gl_sync()
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
        # glDrawElements(GL_TRIANGLES, int(self.splited_triangle_number * 1 * 3), GL_UNSIGNED_INT, None)
        glUseProgram(0)
        glBindVertexArray(0)

    def init_renderer_model_buffer(self):
        # 加速采样后的控制顶点
        # self.control_point_for_sample_ubo

        # 经过tessellate后最终用于绘制的数据。
        # vertice_vbo
        # normal_vbo
        # index_vbo

        glBindVertexArray(self.model_vao)

        self.deform_compute_shader = DeformComputeProgramWrap('deform_compute_shader_oo.glsl',
                                                              self.splited_triangle_number, self.b_spline_body)
        # self.bind_model_buffer(self.index_vbo, self.normal_vbo, self.vertex_vbo)
        # copy control point info to gpu
        self.control_point_for_sample_ubo.async_update(self.b_spline_body.get_control_point_for_sample())
        self.control_point_for_sample_ubo.gl_sync()
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
                  self._tessellated_point_number_pre_splited_triangle * VERTEX_SIZE,
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
        # 更新b样条体相关信息
        bspline_body_info = self.b_spline_body.get_info()
        self.b_spline_body_ubo.async_update(bspline_body_info)
        self.b_spline_body_ubo.gl_sync()

    def prev_computer(self):
        # 用于同步
        # init atom buffer for count splited triangle number
        self.splited_triangle_counter_acbo.async_update(np.array([0], dtype=np.uint32))
        self.splited_triangle_counter_acbo.gl_sync()

        # prev computer
        glUseProgram(self.previous_compute_shader.get_program())
        glDispatchCompute(int(self.model.original_triangle_number / 512 + 1), 1, 1)
        self.splited_triangle_number = self.splited_triangle_counter_acbo.get_value(ctypes.c_uint32)[0]

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
