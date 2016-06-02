import numpy as np

from mvc_control.PreviousComputeControllerGPU import PreviousComputeControllerGPU
from mvc_model.aux import BSplineBody
from mvc_model.model import OBJ
from OpenGL.GL import *
import config as conf


class PreviousComputeControllerCPU:
    def __init__(self, model: OBJ, b_spline_body: BSplineBody, ac: PreviousComputeControllerGPU, controller):
        self._model = model  # type: OBJ

        self._need_recompute = True  # type: bool

        self._splited_triangle_number = -1  # type: int

        # declare buffer
        self._splited_triangle_ssbo = ac.splited_triangle_ssbo
        self._share_adjacency_pn_triangle_normal_ssbo = ac.share_adjacency_pn_triangle_normal_ssbo
        if not conf.IS_FAST_MODE:
            self._share_adjacency_pn_triangle_position_ssbo = ac.share_adjacency_pn_triangle_position_ssbo
        self.original_vertex_ssbo = ac.original_vertex_ssbo
        self.original_normal_ssbo = ac.original_normal_ssbo
        self.original_tex_coord_ssbo = ac.original_tex_coord_ssbo
        self.original_index_ssbo = ac.original_index_ssbo

        self._b_spline_body = b_spline_body
        self._need_upload_control_points = True
        self._controller = controller

    @property
    def need_upload_control_points(self):
        return self._need_upload_control_points

    @need_upload_control_points.setter
    def need_upload_control_points(self, b):
        self._need_upload_control_points = b

    def change_model(self, model):
        self._model = model
        self._need_recompute = True  # type: bool
        self.need_upload_control_points = True

    def gl_init(self):
        pass

    def gl_compute(self, op) -> int:
        if not self._need_recompute:
            return self._splited_triangle_number, False
        self._splited_triangle_number = self.compute_cpu()
        glFinish()
        self._need_recompute = False
        print('gl_compute:', 'cpu splited triangle number: %d' % self._splited_triangle_number)
        self._controller.set_cpu_splited_number(self._splited_triangle_number)
        return self._splited_triangle_number, True

    @property
    def need_compute(self):
        return self._need_recompute

    @need_compute.setter
    def need_compute(self, b):
        self._need_recompute = b

    @property
    def group_size(self):
        return [int(self._model._original_triangle_number / 512 + 1), 1, 1]

    @property
    def splited_triangle_number(self):
        return self._splited_triangle_number

    @property
    def b_spline_body(self):
        return self._b_spline_body

    @b_spline_body.setter
    def b_spline_body(self, b_spline_body):
        self._b_spline_body = b_spline_body

    def compute_cpu(self) -> int:
        number, splited_triangle_data, pn_triangle_position_control_point, pn_triangle_normal_control_point \
            = self._model.split(self._b_spline_body)  # type: np.array
        self._splited_triangle_ssbo.async_update(splited_triangle_data)
        self._splited_triangle_ssbo.gl_sync()

        if self._need_upload_control_points:
            if not conf.IS_FAST_MODE:
                if self._model.from_bezier:
                    self._share_adjacency_pn_triangle_position_ssbo.async_update(self._model.bezier_control_points)
                else:
                    self._share_adjacency_pn_triangle_position_ssbo.async_update(pn_triangle_position_control_point)
                self._share_adjacency_pn_triangle_position_ssbo.gl_sync()
            self._share_adjacency_pn_triangle_normal_ssbo.async_update(pn_triangle_normal_control_point.reshape(-1, 4))
            self._share_adjacency_pn_triangle_normal_ssbo.gl_sync()
            self._need_upload_control_points = False


        return number

    def gl_async_update_buffer_about_output(self):
        pass
