from code import interact

from mvc_control.AuxController import AuxController
from mvc_control.PreviousComputeControllerCPU import PreviousComputeControllerCPU
from mvc_control.PreviousComputeControllerGPU import PreviousComputeControllerGPU
from mvc_control.DeformAndDrawController import DeformAndDrawController
from mvc_model.GLObject import ACVBO
from mvc_model.model import OBJ
from OpenGL.GL import *
import numpy as np
import sys

from mvc_model.plain_class import ACRect

if len(sys.argv) > 1 and sys.argv[1] == 'cpu':
    PreviousComputeController = PreviousComputeControllerCPU
else:
    PreviousComputeController = PreviousComputeControllerGPU


class GLProxy:
    def __init__(self):
        self._aux_controller = None  # type: AuxController
        self._previous_compute_controller = None  # type: PreviousComputeController
        self._deform_and_renderer_controller = None  # type: DeformAndDrawController
        self._debug_buffer = None  # type: ACVBO
        self._model = None  # type: OBJ

    def change_model(self, model: OBJ):
        self._model = model
        if self._aux_controller is None:
            self._aux_controller = AuxController(model.get_length_xyz())  # type: AuxController
        else:
            self._aux_controller.change_size(model.get_length_xyz())

        if self._previous_compute_controller is None:
            if PreviousComputeController == PreviousComputeControllerCPU:
                self._previous_compute_controller = PreviousComputeController(model,
                                                                              self._aux_controller.b_spline_body)  # type: PreviousComputeController
            else:
                self._previous_compute_controller = PreviousComputeController(model)  # type: PreviousComputeController
        else:
            self._previous_compute_controller.change_model(model)
            self._previous_compute_controller.b_spline_body = self._aux_controller.b_spline_body

        if self._deform_and_renderer_controller is not None:
            self._deform_and_renderer_controller.cage_size = self._aux_controller.get_cage_size()

    def draw(self, model_view_matrix, perspective_matrix):
        number, need_deform = self._previous_compute_controller.gl_compute()
        self._deform_and_renderer_controller.set_number_and_need_deform(number, need_deform)
        self._deform_and_renderer_controller.gl_renderer(model_view_matrix, perspective_matrix,
                                                         self._aux_controller.gl_sync_buffer_for_deformation)
        self._aux_controller.gl_draw(model_view_matrix, perspective_matrix)

    def gl_init_global(self):
        glClearColor(1, 1, 1, 1)
        self._aux_controller.gl_init()

        self._debug_buffer = ACVBO(GL_SHADER_STORAGE_BUFFER, 14, None, GL_DYNAMIC_DRAW)  # type: ACVBO
        self._debug_buffer.capacity = 2048
        self._debug_buffer.gl_sync()

        # init previous compute shader
        self._previous_compute_controller.gl_init()

        self._previous_compute_controller.gl_compute()

        # alloc memory in gpu for tessellated vertex
        self._deform_and_renderer_controller = DeformAndDrawController(
            self._aux_controller.get_cage_size())
        self._deform_and_renderer_controller.gl_init()

    def set_select_region(self, x1, y1, x2, y2):
        if self._aux_controller.is_normal_control_point_mode:
            region = ACRect(x1, y1, x2 - x1, y2 - y1)
            self._aux_controller.pick_control_point(region)

    def set_select_point(self, start_point, direction):
        self._aux_controller.select_point_gpu(start_point, direction,
                                              self._previous_compute_controller.splited_triangle_number *
                                              self._deform_and_renderer_controller.tessellated_triangle_number_pre_splited_triangle)

    def move_control_points(self, x, y, z):
        self._aux_controller.move_selected_control_points([x, y, z])
        self._deform_and_renderer_controller.need_deform = True

    def change_tessellation_level(self, level):
        self._deform_and_renderer_controller.set_tessellation_factor(level)  # type: DeformAndDrawController
        self._deform_and_renderer_controller.need_deform = True

    def change_control_point_number(self, u, v, w):
        self._aux_controller.change_control_point_number(u, v, w)
        self._deform_and_renderer_controller.cage_size = self._aux_controller.get_cage_size()
        self._previous_compute_controller.need_compute = True
        self._deform_and_renderer_controller.need_deform = True

    def change_split_factor(self, factor):
        if isinstance(self._previous_compute_controller, PreviousComputeControllerGPU):
            self._previous_compute_controller.split_factor = factor

    def set_control_point_visibility(self, v):
        self._aux_controller.is_normal_control_point_mode = v

    def set_splited_edge_visibility(self, v):
        self._deform_and_renderer_controller.set_splited_edge_visibility(v)

    def set_show_triangle_quality(self, is_show):
        self._deform_and_renderer_controller.set_show_triangle_quality(is_show)

    def set_show_normal_diff(self, is_show):
        self._deform_and_renderer_controller.set_show_normal_diff(is_show)

    def set_show_position_diff(self, is_show):
        self._deform_and_renderer_controller.set_show_position_diff(is_show)

    def set_adjust_control_point(self, is_adjust):
        self._deform_and_renderer_controller.set_adjust_control_point(is_adjust)

    def set_show_control_point(self, is_show):
        self._deform_and_renderer_controller.show_control_point = is_show

    def set_show_normal(self, is_show):
        self._deform_and_renderer_controller.show_normal = is_show

    @property
    def aux_controller(self):
        return self._aux_controller

    @property
    def normal_control_mode(self):
        return self._aux_controller.normal_control_mode

    def clear_direct_control_point(self):
        self._aux_controller.clear_direct_control_point()

    def move_direct_control_point(self, direction):
        self._aux_controller.move_direct_control_point(direction)
        self._deform_and_renderer_controller.need_deform = True

    def direct_control_point_selected(self):
        return self._aux_controller.is_direct_control_point_selected()

    def set_show_real(self, is_show):
        self._deform_and_renderer_controller.set_show_real(is_show)
