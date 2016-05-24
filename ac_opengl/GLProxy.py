from code import interact

from mvc_control.AuxController import AuxController
from mvc_control.PreviousComputeControllerCPU import PreviousComputeControllerCPU
from mvc_control.PreviousComputeControllerGPU import PreviousComputeControllerGPU
from mvc_control.DeformAndDrawController import DeformAndDrawController
from mvc_model.GLObject import ACVBO
from mvc_model.model import OBJ
from OpenGL.GL import *
from Constant import *
import sys

from mvc_model.plain_class import ACRect


class GLProxy:
    def __init__(self, controller=None):
        self._controller = controller
        self._aux_controller = None  # type: AuxController
        self._deform_and_renderer_controller = None  # type: DeformAndDrawController
        self._debug_buffer = None  # type: ACVBO
        self._model = None  # type: OBJ
        self._previous_compute_controller_CYM = None
        self._previous_compute_controller_AC = None

        if len(sys.argv) > 1 and sys.argv[1] == 'cpu':
            self._algorithm = ALGORITHM_CYM
        else:
            self._algorithm = ALGORITHM_AC

    def change_model(self, model: OBJ):
        self._model = model
        if self._aux_controller is None:
            self._aux_controller = AuxController(model.get_length_xyz())  # type: AuxController
        else:
            self._aux_controller.change_size(model.get_length_xyz())

        if self.previous_compute_controller is None:
            self._previous_compute_controller_AC = \
                PreviousComputeControllerGPU(model)
            self._previous_compute_controller_CYM = \
                PreviousComputeControllerCPU(model, self._aux_controller.b_spline_body,
                                             self._previous_compute_controller_AC)
            if self._algorithm == ALGORITHM_AC:
                self._previous_compute_controller_CYM.need_upload_control_points = False
        else:
            self.previous_compute_controller.change_model(model)
            self.previous_compute_controller.b_spline_body = self._aux_controller.b_spline_body

    def draw(self, model_view_matrix, perspective_matrix):
        number, need_deform = self.previous_compute_controller.gl_compute(
            self._aux_controller.gl_sync_buffer_for_previous_computer)
        glFinish()
        self._deform_and_renderer_controller.set_number_and_need_deform(number, need_deform)
        self._deform_and_renderer_controller.gl_renderer(model_view_matrix, perspective_matrix,
                                                         self._aux_controller.gl_sync_buffer_for_deformation)
        # for i in self._debug_buffer.get_value(ctypes.c_float, (10, 4)):
        #     print(i)
        self._aux_controller.gl_draw(model_view_matrix, perspective_matrix)

    def gl_init_global(self):
        glClearColor(1, 1, 1, 1)
        self._aux_controller.gl_init()

        self._debug_buffer = ACVBO(GL_SHADER_STORAGE_BUFFER, 14, None, GL_DYNAMIC_READ)  # type: ACVBO
        self._debug_buffer.capacity = 4096
        self._debug_buffer.gl_sync()

        # init previous compute shader
        self._previous_compute_controller_AC.gl_init()
        self._previous_compute_controller_CYM.gl_init()

        self.previous_compute_controller.gl_compute(self._aux_controller.gl_sync_buffer_for_previous_computer)
        glFinish()

        # alloc memory in gpu for tessellated vertex
        self._deform_and_renderer_controller = DeformAndDrawController(
            self._model.has_texture,
            self.previous_compute_controller,
            self._model,
            self._aux_controller,
            self._controller)
        self._deform_and_renderer_controller.gl_init()

    def set_select_region(self, x1, y1, x2, y2):
        if self._aux_controller.is_normal_control_point_mode:
            region = ACRect(x1, y1, x2 - x1, y2 - y1)
            self._aux_controller.pick_control_point(region)

    def set_select_point(self, start_point, direction):
        self._aux_controller.select_point_gpu(start_point, direction,
                                              self.previous_compute_controller.splited_triangle_number *
                                              self._deform_and_renderer_controller.tessellated_triangle_number_pre_splited_triangle)

    def move_control_points(self, x, y, z):
        self._aux_controller.move_selected_control_points([x, y, z])
        self._deform_and_renderer_controller.need_deform = True

    def rotate_control_points(self, m):
        self._aux_controller.rotate_selected_control_points(m)
        self._deform_and_renderer_controller.need_deform = True

    def change_tessellation_level(self, level):
        self._deform_and_renderer_controller.set_tessellation_factor(level)  # type: DeformAndDrawController
        self._deform_and_renderer_controller.need_deform = True
        self.aux_controller.b_spline_body.modify_range_flag = True

    def change_control_point_number(self, u, v, w):
        self._aux_controller.change_control_point_number(u, v, w)
        self.previous_compute_controller.need_compute = True
        self._deform_and_renderer_controller.need_deform = True

    def change_control_point_order(self, order):
        self._aux_controller.change_control_point_order(order)
        self.previous_compute_controller.need_compute = True
        self._deform_and_renderer_controller.need_deform = True

    def change_split_factor(self, factor):
        if self._algorithm == ALGORITHM_AC:
            self.previous_compute_controller.split_factor = factor
            self.change_tessellation_level(
                self.previous_compute_controller.split_factor / self._deform_and_renderer_controller.final_tessellation_level)
            self.aux_controller.b_spline_body.modify_range_flag = True

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
        self._aux_controller.clear_dst_direct_control_point()

    def move_direct_control_point(self, direction):
        self._aux_controller.move_direct_control_point(direction)
        self._deform_and_renderer_controller.need_deform = True

    def move_direct_control_point_delta(self, direction):
        self._aux_controller.move_direct_control_point_delta(direction)
        self._deform_and_renderer_controller.need_deform = True

    def direct_control_point_selected(self):
        return self._aux_controller.is_direct_control_point_selected()

    def set_show_real(self, is_show):
        self._deform_and_renderer_controller.set_show_real(is_show)

    def set_show_original(self, is_show):
        self._deform_and_renderer_controller.set_show_original(is_show)

    def set_need_comparison(self):
        self._deform_and_renderer_controller.set_need_comparison()

    @property
    def algorithm(self):
        return self._algorithm

    @algorithm.setter
    def algorithm(self, algorithm):
        self._algorithm = algorithm
        self.previous_compute_controller.need_compute = True
        self.previous_compute_controller.gl_async_update_buffer_about_output()
        self.aux_controller.b_spline_body.modify_range_flag = True

    @property
    def previous_compute_controller(self):
        if self._algorithm == ALGORITHM_AC:
            return self._previous_compute_controller_AC
        else:
            return self._previous_compute_controller_CYM

    def control_points(self):
        return self._aux_controller.get_normal_control_point_data()

    def set_control_points(self, control_points):
        self._aux_controller.set_control_points(control_points)
        self._deform_and_renderer_controller.need_deform = True

    def get_parameter_str(self):
        return '%s_%.2f_%d' % (self.aux_controller.get_control_point_str(),
                               self._previous_compute_controller_AC.split_factor,
                               self._deform_and_renderer_controller.tessellation_level)

    def set_use_pn_normal(self, use):
        self._deform_and_renderer_controller.use_pn_normal_for_renderer = use

    def clear_director_control_points(self):
        self.aux_controller.clear_all_direct_control_point()
