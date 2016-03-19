from Constant import *
from mvc_model.model import OBJ
from mvc_model.GLObject import ACVBO
from OpenGL.GL import *


class PreviousComputeController:
    def __init__(self, model: OBJ):
        self._model = model  # type: OBJ

        self._need_recompute = True  # type: bool

        self._splited_triangle_number = -1  # type: int

        # declare buffer
        self._splited_triangle_ssbo = ACVBO(GL_SHADER_STORAGE_BUFFER, 5, None, GL_STATIC_DRAW)

    def change_model(self, model):
        self._model = model
        self._splited_triangle_ssbo.capacity = self._model.original_triangle_number \
                                               * MAX_SPLITED_TRIANGLE_PRE_ORIGINAL_TRIANGLE \
                                               * SPLITED_TRIANGLE_SIZE
        self._need_recompute = True  # type: bool

    def gl_init(self):
        # async update vbo
        self._splited_triangle_ssbo.capacity = self._model.original_triangle_number \
                                               * MAX_SPLITED_TRIANGLE_PRE_ORIGINAL_TRIANGLE \
                                               * SPLITED_TRIANGLE_SIZE

    def gl_sync(self):
        self._splited_triangle_ssbo.gl_sync()

    def gl_compute(self, operator) -> int:
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
        return -1
