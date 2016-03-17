import threading

from mvc_control.BSplineBodyController import BSplineBodyController
from mvc_control.PreviousComputeController import PreviousComputeController
from mvc_control.DeformAndDrawController import DeformAndDrawController
from mvc_model.model import OBJ
from OpenGL.GL import *

from mvc_model.plain_class import ACRect


class GLProxy:
    def __init__(self, model: OBJ):
        self._embed_body_controller = BSplineBodyController(model.get_length_xyz())  # type: BSplineBodyController
        self._previous_compute_controller = PreviousComputeController(model)  # type: PreviousComputeController
        self._deform_and_renderer_controller = None  # type: DeformAndDrawController

    def draw(self, model_view_matrix, perspective_matrix):
        self._previous_compute_controller.gl_compute(self._embed_body_controller.gl_sync_buffer_for_previous_computer)
        self._deform_and_renderer_controller.gl_renderer(model_view_matrix, perspective_matrix,
                                                         self._embed_body_controller.gl_sync_buffer_for_deformation)
        self._embed_body_controller.gl_draw(model_view_matrix, perspective_matrix)

    def gl_init_global(self):
        glClearColor(1, 1, 1, 1)
        self._embed_body_controller.gl_init()

        # init previous compute shader
        self._previous_compute_controller.gl_init()
        self._previous_compute_controller.gl_compute(self._embed_body_controller.gl_sync_buffer_for_previous_computer)

        # alloc memory in gpu for tessellated vertex
        self._deform_and_renderer_controller = DeformAndDrawController(
            self._previous_compute_controller.splited_triangle_number,
            self._embed_body_controller.get_cage_size())
        self._deform_and_renderer_controller.gl_init()

    def set_select_region(self, x1, y1, x2, y2):
        region = ACRect(x1, y1, x2 - x1, y2 - y1)
        self._embed_body_controller.pick_control_point(region)

    def move_control_points(self, x, y, z):
        self._embed_body_controller.move_selected_control_points([x, y, z])
        self._deform_and_renderer_controller.need_deform = True

    def change_tessellation_level(self, level):
        self._deform_and_renderer_controller.set_tessellation_factor(level)  # type: DeformAndDrawController
        self._deform_and_renderer_controller.need_deform = True

    def change_control_point_number(self, u, v, w):
        self._embed_body_controller.change_control_point_number(u, v, w)
        self._deform_and_renderer_controller.cage_size = self._embed_body_controller.get_cage_size()
        self._previous_compute_controller.need_compute = True
