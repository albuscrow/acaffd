from mvc_model.model import OBJ, ModelFileFormatType
from math import *
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from OpenGL.GL import *
from pyrr.matrix44 import *
from pyrr.euler import *

from ac_opengl.GLProxy import GLProxy
from mvc_model.plain_class import ACRect
import numpy as np

__author__ = 'ac'


class Controller(QObject):
    updateScene = pyqtSignal()

    def __init__(self):
        super().__init__()
        # todo test code
        self._gl_proxy = None  # type: GLProxy
        self.load_file("")

        # default show b spline control points
        self.show_aux(True)

        # for renderer
        # window size for glSetViewPort
        self._window_size = ACRect()  # type: ACRect

        # for rotate
        self._rotate_x = 0  # type: int
        self._rotate_y = 0  # type: int

        # m v p matrix
        self._perspective_matrix = None  # type: np.array
        self._model_matrix = create_from_translation(np.array([0, 0, -8]), dtype='float32')  # type: np.array
        self._model_view_matrix = self._model_matrix  # type: np.array

        self.inited = False  # type: bool

    @pyqtSlot(float, float, float)
    def move_control_points(self, x, y, z):
        self._gl_proxy.move_control_points(x, y, z)
        self.updateScene.emit()

    @pyqtSlot(int)
    def change_tessellation_level(self, level):
        self._gl_proxy.change_tessellation_level(level)
        self.updateScene.emit()

    @pyqtSlot(str)
    def load_file(self, file_path):
        # todo
        file_path = "res/3d_model/Mobile.obj"
        # file_path = "res/3d_model/767.obj"
        # file_path = "res/3d_model/ttest.obj"
        # file_path = "res/3d_model/cube.obj"
        # file_path = "res/3d_model/test2.obj"
        # file_path = "res/3d_model/bishop.obj"
        # file_path = "res/3d_model/test_same_normal.obj"
        # file_path = "res/3d_model/star.obj"
        # file_path = "res/3d_model/legoDog.obj"
        # file_path = "res/3d_model/test_2_triangle.obj"
        # file_path = "res/3d_model/Mobile.obj"
        # file_path = "res/3d_model/biship_cym_area_average_normal.obj"
        # file_path = "res/3d_model/test_2_triangle.obj"
        # file_path = "res/3d_model/biship_cym_area_average_normal.obj"
        # file_path = "res/3d_model/biship_cym_direct_average_normal.obj"
        # file_path = "res/3d_model/vase_cym.obj"
        # file_path = "res/3d_model/sphere.obj"
        # file_path = "res/3d_model/wheel.obj"
        if file_path.startswith('file://'):
            file_path = file_path[len('file://'):]
        raw_obj = OBJ(file_path, ModelFileFormatType.obj)
        self._gl_proxy = GLProxy(raw_obj)

    @pyqtSlot(int, int)
    def rotate(self, x, y):
        # record rotate_y and rotate_x
        self._rotate_y += x
        self._rotate_x += y
        # update _mode_view_matrix
        self._model_view_matrix = multiply(create_from_eulers(create(-self._rotate_x / 180 * pi, 0,
                                                                     -self._rotate_y / 180 * pi), dtype='float32'),
                                           self._model_matrix)
        self.updateScene.emit()

    @pyqtSlot(bool)
    def show_aux(self, is_show: bool):
        self._gl_proxy._show_control_point = is_show

    @pyqtSlot(int, int, int, int)
    def select(self, x1: int, y1: int, x2: int, y2: int):
        x1 = min(x1, x2)
        x2 = max(x1, x2)
        y1 = min(y1, y2)
        y2 = max(y1, y2)
        self._gl_proxy.set_select_region(x1, self.window_size.h - y2, x2, self.window_size.h - y1)
        self.updateScene.emit()

    @pyqtSlot(int, int, int)
    def change_control_point_number(self, u: int, v: int, w: int):
        self._gl_proxy.change_control_point_number(u, v, w)
        self.updateScene.emit()

    @pyqtSlot(int)
    def zoom(self, delta):
        pass

    @property
    def window_size(self):
        return self._window_size

    def gl_on_view_port_change(self, *xywh):
        if self.window_size != xywh:
            self.window_size.update(xywh)
            aspect = self.window_size.aspect
            self._perspective_matrix = create_perspective_projection_matrix_from_bounds(-aspect, aspect, -1,
                                                                                        1, 4, 100,
                                                                                        dtype='float32')

    def gl_init(self) -> None:
        glClearColor(1, 1, 1, 1)
        self._gl_proxy.gl_init_global()

    def gl_on_frame_draw(self) -> None:
        glEnable(GL_SCISSOR_TEST)
        glScissor(*self.window_size.xywh)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # todo 这句理论上应该在gl_on_view_port_change调用，但是会有问题
        glViewport(*self.window_size.xywh)

        if self._gl_proxy:
            self._gl_proxy.draw(self._model_view_matrix, self._perspective_matrix)

        glDisable(GL_SCISSOR_TEST)

    @pyqtSlot()
    def paint(self):
        if not self.inited:
            self.gl_init()
            self.inited = True
        self.gl_on_frame_draw()
