import numpy as np
from mvc_model.aux import BSplineBody
from mvc_model.model import OBJ
from mvc_model.GLObject import ACVBO
from OpenGL.GL import *


class PreviousComputeControllerCPU:
    def __init__(self, model: OBJ, b_spline_body: BSplineBody):
        self._model = model  # type: OBJ

        self._need_recompute = True  # type: bool

        self._splited_triangle_number = -1  # type: int

        # declare buffer
        self._splited_triangle_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 5, None, GL_STATIC_DRAW)

        self._b_spline_body = b_spline_body

    def change_model(self, model):
        self._model = model
        self._need_recompute = True  # type: bool

    def gl_init(self):
        pass

    def gl_compute(self, operator) -> int:
        operator()
        if not self._need_recompute:
            return self._splited_triangle_number
        self._splited_triangle_number = self.compute_cpu()
        self._need_recompute = False
        return self._splited_triangle_number

    @property
    def need_compute(self):
        return self._need_recompute

    @need_compute.setter
    def need_compute(self, b):
        self._need_recompute = b

    @property
    def group_size(self):
        return [int(self._model.original_triangle_number / 512 + 1), 1, 1]

    @property
    def splited_triangle_number(self):
        return self._splited_triangle_number

    def compute_cpu(self) -> int:
        number, data = self._model.split(self._b_spline_body)  # type: np.array
        self._splited_triangle_ssbo.async_update(data)
        self._splited_triangle_ssbo.gl_sync()
        return number
