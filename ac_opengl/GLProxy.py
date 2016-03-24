from mvc_control.BSplineBodyController import BSplineBodyController
from mvc_control.PreviousComputeControllerCPU import PreviousComputeControllerCPU
from mvc_control.PreviousComputeControllerGPU import PreviousComputeControllerGPU
from mvc_control.DeformAndDrawController import DeformAndDrawController
from mvc_model.model import OBJ
from OpenGL.GL import *
import sys

from mvc_model.plain_class import ACRect

if len(sys.argv) > 1 and sys.argv[1] == 'cpu':
    PreviousComputeController = PreviousComputeControllerCPU
else:
    PreviousComputeController = PreviousComputeControllerGPU


class GLProxy:
    def __init__(self):
        self._embed_body_controller = None  # type: BSplineBodyController
        self._previous_compute_controller = None  # type: PreviousComputeController
        self._deform_and_renderer_controller = None  # type: DeformAndDrawController

    def change_model(self, model: OBJ):
        if self._embed_body_controller is None:
            self._embed_body_controller = BSplineBodyController(model.get_length_xyz())  # type: BSplineBodyController
        else:
            self._embed_body_controller.change_size(model.get_length_xyz())

        if self._previous_compute_controller is None:
            if PreviousComputeController == PreviousComputeControllerCPU:
                self._previous_compute_controller = PreviousComputeController(model,
                                                                              self._embed_body_controller.b_spline_body)  # type: PreviousComputeController
            else:
                self._previous_compute_controller = PreviousComputeController(model)  # type: PreviousComputeController

        else:
            self._previous_compute_controller.change_model(model)

        if self._deform_and_renderer_controller is not None:
            self._deform_and_renderer_controller.cage_size = self._embed_body_controller.get_cage_size()

    def draw(self, model_view_matrix, perspective_matrix):
        if isinstance(self._previous_compute_controller, PreviousComputeControllerGPU):
            self._deform_and_renderer_controller.splited_triangle_number \
                = self._previous_compute_controller \
                .gl_compute(self._embed_body_controller.gl_sync_buffer_for_previous_computer)
        else:
            self._deform_and_renderer_controller.splited_triangle_number \
                = self._previous_compute_controller \
                .gl_compute()

        self._deform_and_renderer_controller.gl_renderer(model_view_matrix, perspective_matrix,
                                                         self._embed_body_controller.gl_sync_buffer_for_deformation)
        self._embed_body_controller.gl_draw(model_view_matrix, perspective_matrix)

    def gl_init_global(self):
        glClearColor(1, 1, 1, 1)
        self._embed_body_controller.gl_init()

        # init previous compute shader
        self._previous_compute_controller.gl_init()
        if isinstance(self._previous_compute_controller, PreviousComputeControllerGPU):
            self._previous_compute_controller.gl_compute(self._embed_body_controller.gl_sync_buffer_for_previous_computer)
        else:
            self._previous_compute_controller.gl_compute()

        # alloc memory in gpu for tessellated vertex
        self._deform_and_renderer_controller = DeformAndDrawController(
            self._previous_compute_controller.splited_triangle_number,
            self._embed_body_controller.get_cage_size())
        self._deform_and_renderer_controller.gl_init()

    def set_select_region(self, x1, y1, x2, y2):
        if self._embed_body_controller.visibility:
            region = ACRect(x1, y1, x2 - x1, y2 - y1)
            self._embed_body_controller.pick_control_point(region)

    def move_control_points(self, x, y, z):
        if self._embed_body_controller.visibility:
            self._embed_body_controller.move_selected_control_points([x, y, z])
            self._deform_and_renderer_controller.need_deform = True

    def change_tessellation_level(self, level):
        self._deform_and_renderer_controller.set_tessellation_factor(level)  # type: DeformAndDrawController
        self._deform_and_renderer_controller.need_deform = True

    def change_control_point_number(self, u, v, w):
        self._embed_body_controller.change_control_point_number(u, v, w)
        self._deform_and_renderer_controller.cage_size = self._embed_body_controller.get_cage_size()
        self._previous_compute_controller.need_compute = True
        self._deform_and_renderer_controller.need_deform = True

    def change_split_factor(self, factor):
        if isinstance(self._previous_compute_controller, PreviousComputeControllerGPU):
            self._previous_compute_controller.split_factor = factor

    def set_control_point_visibility(self, v):
        self._embed_body_controller.visibility = v

    def set_splited_edge_visibility(self, v):
        self._deform_and_renderer_controller.set_splited_edge_visibility(v)

    def set_show_triangle_quality(self, is_show):
        self._deform_and_renderer_controller.set_show_triangle_quality(is_show)
