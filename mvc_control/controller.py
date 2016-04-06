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
        self._gl_proxy = GLProxy()  # type: GLProxy

        # todo test code
        self.load_file(get_test_file_name())

        # default show b spline control points
        self.set_control_point_visibility(False)

        # for renderer
        # window size for glSetViewPort
        self._window_size = ACRect()  # type: ACRect

        # for rotate
        self._rotate_x = 0  # type: int
        self._rotate_y = 0  # type: int

        # for zoom
        self._scale = np.array([1, 1, 1], dtype='f4')

        # m v p matrix
        self._perspective_matrix = None  # type: np.array
        self._translate = [0, 0, -8]  # type: np.array
        self._model_view_matrix = create_from_translation(np.array(self._translate), dtype='float32')  # type: np.array

        self._inited = False  # type: bool

    @pyqtSlot(float, float, float)
    def move_control_points(self, x, y, z):
        self._gl_proxy.move_control_points(x, y, z)
        self.updateScene.emit()

    @pyqtSlot(int)
    def change_tessellation_level(self, level):
        self._gl_proxy.change_tessellation_level(level)
        self.updateScene.emit()

    @pyqtSlot(float)
    def change_split_factor(self, level):
        self._gl_proxy.change_split_factor(level)
        self.updateScene.emit()

    @pyqtSlot(str)
    def load_file(self, file_path):
        if file_path.startswith('file://'):
            file_path = file_path[len('file://'):]
        raw_obj = OBJ(file_path, ModelFileFormatType.obj)
        self._gl_proxy.change_model(raw_obj)

    @pyqtSlot(int, int)
    def rotate(self, x, y):
        # record rotate_y and rotate_x
        self._rotate_y += x
        self._rotate_x += y
        # update _mode_view_matrix
        scale_matrix = create_from_scale(self._scale, dtype='f4')
        self._model_view_matrix = multiply(create_from_eulers(create(-self._rotate_x / 180 * pi, 0,
                                                                     -self._rotate_y / 180 * pi), dtype='f4'),
                                           np.dot(scale_matrix, create_from_translation(self._translate, dtype='f4')))
        self.updateScene.emit()

    @pyqtSlot(int, int)
    def move(self, x, y):
        # record rotate_y and rotate_x
        xyz = [x / 100, - y / 100, 0]
        self._translate = [x + y for x, y in zip(self._translate, xyz)]
        # update _mode_view_matrix
        scale_matrix = create_from_scale(self._scale, dtype='f4')
        self._model_view_matrix = multiply(create_from_eulers(create(-self._rotate_x / 180 * pi, 0,
                                                                     -self._rotate_y / 180 * pi), dtype='f4'),
                                           np.dot(scale_matrix, create_from_translation(self._translate, dtype='f4')))
        self.updateScene.emit()

    @pyqtSlot(int, int)
    def rotate(self, x, y):
        # record rotate_y and rotate_x
        self._rotate_y += x
        self._rotate_x += y
        # update _mode_view_matrix
        scale_matrix = create_from_scale(self._scale, dtype='f4')
        self._model_view_matrix = multiply(create_from_eulers(create(-self._rotate_x / 180 * pi, 0,
                                                                     -self._rotate_y / 180 * pi), dtype='f4'),
                                           np.dot(scale_matrix, create_from_translation(self._translate, dtype='f4')))
        self.updateScene.emit()

    @pyqtSlot(bool)
    def set_control_point_visibility(self, is_show: bool):
        self._gl_proxy.set_control_point_visibility(is_show)

    @pyqtSlot(bool)
    def set_show_real(self, is_show: bool):
        self._gl_proxy.set_show_real(is_show)

    @pyqtSlot(bool)
    def set_splited_edge_visibility(self, is_show: bool):
        self._gl_proxy.set_splited_edge_visibility(is_show)

    @pyqtSlot(bool)
    def set_show_triangle_quality_flag(self, is_show: bool):
        self._gl_proxy.set_show_triangle_quality(is_show)

    @pyqtSlot(bool)
    def set_show_normal_diff_flag(self, is_show: bool):
        self._gl_proxy.set_show_normal_diff(is_show)

    @pyqtSlot(bool)
    def set_adjust_control_point(self, is_adjust: bool):
        self._gl_proxy.set_adjust_control_point(is_adjust)

    @pyqtSlot(bool)
    def set_show_position_diff_flag(self, is_show: bool):
        self._gl_proxy.set_show_position_diff(is_show)

    @pyqtSlot(bool)
    def set_show_control_point(self, is_show: bool):
        self._gl_proxy.set_show_control_point(is_show)

    @pyqtSlot(bool)
    def set_show_normal(self, is_show: bool):
        self._gl_proxy.set_show_normal(is_show)

    @pyqtSlot()
    def set_need_comparison(self):
        self._gl_proxy.set_need_comparison()

    @pyqtSlot(int, int, int, int)
    def left_move(self, x1: int, y1: int, x2: int, y2: int):
        y1 = self.window_size.h - y1
        y2 = self.window_size.h - y2
        if self._gl_proxy.normal_control_mode:
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            self._gl_proxy.set_select_region(x1, y1, x2, y2)
        else:
            i = np.mat(self._model_view_matrix).I
            if self._gl_proxy.direct_control_point_selected():
                direction = np.mat([x2 - x1, y2 - y1, 0, 0], dtype='f4') * i
                self._gl_proxy.move_direct_control_point(np.array(direction, dtype='f4').reshape(4,)[:3])

                # start_point = np.mat([0, 0, 0, 1], dtype='f4') * i
                # end_point_z = -4
                # end_point_y = y2 / self.window_size.h * 2 - 1
                # end_point_x = x2 / self.window_size.h * 2 - self.window_size.aspect
                # end_point = np.mat([end_point_x, end_point_y, end_point_z, 1], dtype='f4') * i
                # self._gl_proxy.set_select_point(start_point, end_point - start_point)
            else:
                start_point = np.mat([0, 0, 0, 1], dtype='f4') * i
                end_point_z = -4
                end_point_y = y2 / self.window_size.h * 2 - 1
                end_point_x = x2 / self.window_size.h * 2 - self.window_size.aspect
                end_point = np.mat([end_point_x, end_point_y, end_point_z, 1], dtype='f4') * i
                self._gl_proxy.set_select_point(start_point, end_point - start_point)

        self.updateScene.emit()

    @pyqtSlot()
    def cancel_direct_control_point(self):
        self._gl_proxy.clear_direct_control_point()
        self.updateScene.emit()

    @pyqtSlot(int, int, int)
    def change_control_point_number(self, u: int, v: int, w: int):
        self._gl_proxy.change_control_point_number(u, v, w)
        self.updateScene.emit()

    @pyqtSlot(int)
    def change_algorithm(self, algorithm):
        self._gl_proxy.algorithm = algorithm

    @pyqtSlot(int)
    def zoom(self, delta):
        delta /= 10
        self._scale += delta
        if self._scale[0] == 0:
            self._scale += delta
        scale_matrix = create_from_scale(self._scale, dtype='f4')
        self._model_view_matrix = np.dot(create_from_eulers(create(-self._rotate_x / 180 * pi, 0,
                                                                   -self._rotate_y / 180 * pi), dtype='float32'),
                                         np.dot(scale_matrix, create_from_translation(self._translate, dtype='f4')))
        self.updateScene.emit()

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
        if not self._inited:
            self.gl_init()
            self._inited = True
        self.gl_on_frame_draw()


def get_test_file_name():
    # todo
    # file_path = "res/3d_model/Mobile.obj"
    # file_path = "res/3d_model/767.obj"
    # file_path = "res/3d_model/ttest.obj"
    file_path = "res/3d_model/cube.obj"
    # file_path = "res/3d_model/test2.obj"
    # file_path = "res/3d_model/bishop.obj"
    # file_path = "res/3d_model/test_same_normal.obj"
    # file_path = "res/3d_model/star.obj"
    # file_path = "res/3d_model/legoDog.obj"
    # file_path = "res/3d_model/test_2_triangle.obj"
    # file_path = "res/3d_model/test_2_triangle_plain.obj"
    # file_path = "res/3d_model/Mobile.obj"
    # file_path = "res/3d_model/test_2_triangle.obj"
    # file_path = "res/3d_model/biship_cym_area_average_normal.obj"
    # file_path = "res/3d_model/biship_cym_direct_average_normal.obj"
    # file_path = "res/3d_model/vase_cym.obj"
    # file_path = "res/3d_model/sphere.obj"
    # file_path = "res/3d_model/wheel.obj"
    # file_path = "res/3d_model/snail.obj"
    return file_path
