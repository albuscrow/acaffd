import threading

import numpy

from mvc_control.BSplineBodyController import BSplineBodyController
from mvc_control.PreviousComputeController import PreviousComputeController
from mvc_model.GLObject import ACVBO
from pyrr.matrix44 import *

from mvc_model.plain_class import ACRect
from util.GLUtil import *
from Constant import *
from ac_opengl.shader.ShaderWrapper import DeformComputeProgramWrap, DrawProgramWrap


class GLProxy:
    def __init__(self, model):
        self._tessellation_factor = 3
        self._tessellated_point_number_pre_splited_triangle = (self._tessellation_factor + 1) * (
            self._tessellation_factor + 2) / 2
        self._tessellated_triangle_number_pre_splited_triangle = self._tessellation_factor * self._tessellation_factor

        self.model = model
        self._embed_body_controller = BSplineBodyController(self.model.get_length_xyz())  # type: BSplineBodyController

        self.model_vao = None
        self.splited_triangle_number = 0
        self.previous_compute_controller = PreviousComputeController(self.model)  # type: PreviousComputeController
        self.deform_compute_shader = None
        self.model_renderer_shader = None
        self.need_deform = False

        # self.b_spline_body_ubo = None
        self.control_point_vertex_vbo = None
        self.control_point_color_vbo = None
        self.is_inited = False
        self.need_update_control_point = False
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

        self.control_point_for_sample_ubo = None

    def draw(self, model_view_matrix, perspective_matrix):
        if not self.is_inited:
            self.gl_init_global()

        with self.lock:
            for t in self.task:
                t()
            self.task.clear()

        self.deform_and_draw_model(model_view_matrix, perspective_matrix)
        self._embed_body_controller.gl_draw(model_view_matrix, perspective_matrix)

    def gl_init_global(self):
        self._embed_body_controller.gl_init()
        self._embed_body_controller.gl_sync_buffer_for_previous_computer()
        # init code for openGL
        # create ssbo
        # 原始面片邻接关系, 共享的原始面片pn triangle
        # adjacency_ssbo share_adjacency_pn_triangle_ssbo
        # 经过分割以后的数据。
        # splited_triangle_ssbo
        # B spline body 的信息。
        # b_spline_body_ubo

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

        # init previous compute shader
        self.previous_compute_controller.gl_init()
        self.splited_triangle_number = self.previous_compute_controller.split_model()

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

        self.model_renderer_shader = DrawProgramWrap('vertex.glsl', 'fragment.glsl')

        self.deform_compute_shader = DeformComputeProgramWrap('deform_compute_shader_oo.glsl',
                                                              self.splited_triangle_number, self._embed_body_controller.get_cage_size())
        self.need_deform = True

        self.is_inited = True

    def deform_and_draw_model(self, model_view_matrix, perspective_matrix):
        glBindVertexArray(self.model_vao)
        # if control points is change, run deform compute shader
        if self.need_deform:
            if self.tessellation_factor_is_change:
                self.bind_model_buffer(self.index_vbo, self.normal_vbo, self.vertex_vbo)
            glUseProgram(self.deform_compute_shader.get_program())
            self._embed_body_controller.gl_sync_buffer_for_deformation()
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
            self.deform_compute_shader._tessellated_triangle_number_pre_splited_triangle * 3),
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
                                                              self.splited_triangle_number,
                                                              self._embed_body_controller.get_cage_size())
        # init compute shader before every frame
        glUseProgram(self.deform_compute_shader.get_program())
        # self.deform_compute_shader.test()
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

    def set_select_region(self, x1, y1, x2, y2):
        region = ACRect(x1, y1, x2 - x1, y2 - y1)
        self._embed_body_controller.pick_control_point(region)

    def move_control_points(self, x, y, z):
        self._embed_body_controller.move_selected_control_points([x, y, z])
        self.need_deform = True

    def change_tessellation_level(self, level):
        self.deform_compute_shader.tessellation_factor = level
        self.need_deform = True
        self.tessellation_factor_is_change = True

    def change_control_point(self, u, v, w):
        self._embed_body_controller.change_control_point_number(u, v, w)
        with self.lock:
            self.task.append(self.init_renderer_model_buffer)


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
