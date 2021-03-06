from functools import reduce

from mvc_model.model import OBJ
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from OpenGL.GL import *
from pyrr.matrix44 import *

from ac_opengl.GLProxy import GLProxy
from mvc_model.plain_class import ACRect
import numpy as np
from os.path import isfile, exists
from Constant import ALGORITHM_AC, ALGORITHM_CYM
import os
import matplotlib.pyplot as plt
import util.util
import util.figure_util as figutil

__author__ = 'ac'


class Controller(QObject):
    update_scene = pyqtSignal(name='update_scene')
    show_figure = pyqtSignal(name='show_figure')

    def __init__(self):
        super().__init__()
        self._context = None
        self._gl_proxy = GLProxy(self)  # type: GLProxy

        # todo test code
        self._loaded_file_path = None  # type: str
        self.load_file(get_test_file_name())

        # default show b spline control points
        self.set_control_point_visibility(False)

        # for renderer
        # window size for glSetViewPort
        self._window_size = ACRect()  # type: ACRect

        # for zoom
        self._scale = np.array([1, 1, 1], dtype='f4')

        # m v p matrix
        self._perspective_matrix = None  # type: np.array
        self._translate = [0, 0, -8]  # type: np.array
        self._model_view_matrix = create_from_translation(np.array(self._translate), dtype='float32')  # type: np.array
        self._rotate_matrix = create_identity(dtype='f4')

        # rotate matrix for cube
        # self._rotate_matrix = np.array(
        #     [[0.44967501, -0.06625679, -0.89087461, 0.],
        #      [-0.84477917, 0.29277544, -0.4481853, 0.],
        #      [0.29048993, 0.95400547, 0.07567401, 0.],
        #      [0., 0., 0., 1.]])

        # model_view_matrix for ship
        self._model_view_matrix = np.array([[1.75159, 0.288119, -0.677501, 0.0],
                                            [-0.278612, 1.87784, 0.0782773, 0.0],
                                            [0.681467, 0.0271856, 1.7734, 0.0],
                                            [0.19, 0.43, -8.0, 1.0]])

        self._inited = False  # type: bool

        self.factors = None
        self.area_result = []
        self.quality_result = []
        self.diff_result = []
        self.time_result = []
        self.cage_length = 0
        self.cym_position_error = 0
        self.splited_number = []
        self.cpu_split_number = 0

        self.gl_task = None
        self.show_figure.connect(self.show_diff_result)

    def add_quality(self, q):
        self.quality_result.append(q)

    def add_time(self, t):
        self.time_result.append(t)

    def add_area(self, a):
        self.area_result.append(a)

    def add_diff_result(self, r):
        self.diff_result.append(r)

    def add_splited_number(self, n):
        self.splited_number.append(n)

    def show_diff_result(self):
        path = self.get_save_path()
        np.save(path + '/split_data', self.diff_result)
        l = list(self.factors)

        triangle_number = self.splited_number
        r_number = [1 / x for x in triangle_number]
        triangle_area = self.area_result
        triangle_quality = self.quality_result

        #获取l临界命值，使三角形质量较优
        print(l)
        print(triangle_number)
        print(triangle_quality)
        tmp = list(zip(l, triangle_number, triangle_quality))
        tmp.sort(key=lambda t: t[1], reverse=True)
        print(tmp)


        split_time, deformation_time = self.time_result[0::2], self.time_result[1::2]
        total_time = [x + y for x, y in zip(split_time, deformation_time)]

        # self.diff_result 里面的元素(位置(平均，最大，标准差),法向(平均，最大，标准差))
        position_average_error = [x[0][0] for x in self.diff_result]
        normal_average_error = [x[1][0] for x in self.diff_result]

        # l error
        # fp = '/home/ac/thesis/zju_thesis/figures/clip/l-error0.png'
        # figutil.draw_figure([(l, position_average_error, '', None)],
        #                     u'l取值', u'几何误差',
        #                     save_file_name=fp, show=True, sort_x=False,
        #                     font_size=20, dpi=60)

        # area error
        # fp = '/home/ac/thesis/zju_thesis/figures/clip/l-error1.png'
        # figutil.draw_figure([(triangle_area, position_average_error, '', None)],
        #                     u'子三角形平均面积', u'几何误差',
        #                     save_file_name=fp, show=True, sort_x=True,
        #                     font_size=20, dpi=60)

        # l-quality
        # fp = '/home/ac/thesis/zju_thesis/figures/clip/l-quality0.png'
        # figutil.draw_figure([(l, triangle_quality, '', None)],
        #                     u'l取值', u'平均三角形质量',
        #                     save_file_name=fp, show=True, sort_x=False,
        #                     font_size=20, dpi=60)

        # number-quality
        # fp = '/home/ac/thesis/zju_thesis/figures/clip/l-quality1.png'
        # figutil.draw_figure([(triangle_number, triangle_quality, '', None)],
        #                     u'三角形数量', u'平均三角形质量',
        #                     save_file_name=fp, show=True, sort_x=True,
        #                     font_size=20, dpi=60)

        # number-quality

        # number-time
        # fp = '/home/ac/thesis/zju_thesis/figures/clip/l-time1.png'
        # figutil.draw_figure([(triangle_number, split_time, '', '分割时间'), (triangle_number, deformation_time, '', '变形时间')],
        #                     u'子三角形数量', u'时间（ms）',
        #                     save_file_name=fp, show=False, sort_x=True,
        #                     font_size=20, dpi=60, legend_loc='upper left')

        # l-time
        # fp = '/home/ac/thesis/zju_thesis/figures/clip/l-time0.png'
        # figutil.draw_figure([(l, split_time, '', '分割时间'), (l, deformation_time, '', '变形时间')],
        #                     u'l取值', u'时间（ms）',
        #                     save_file_name=fp, show=False, font_size=20, dpi=60)

        # figutil.draw_figure([(l, split_time, '', '分割时间'), (l, split_time, '', '分割时间')], u'l取值', u'时间')

        # self.draw_figure(self.area_result, position_average_error, u'子三角形平均面积', u'顶点平均几何误差')
        # figutil.draw_zoom(plt.gcf(), [0, 0.47, 0, 0.06], [0.1, 0.25], 1.1)

    @pyqtSlot()
    def clear_director_control_points(self):
        self._gl_proxy.clear_director_control_points()

    @pyqtSlot(float, float, float)
    def move_control_points(self, x, y, z):
        if self._gl_proxy.normal_control_mode:
            self._gl_proxy.move_control_points(x, y, z)
        else:
            direct_delta = np.array([x / 10, y / 10, z / 10], dtype='f4')
            self._gl_proxy.move_direct_control_point_delta(direct_delta)

        self.update_scene.emit()

    @pyqtSlot(float, float, float)
    def rotate_control_points(self, x, y, z):
        if self._gl_proxy.normal_control_mode:
            if x != 0:
                if x > 0:
                    m = create_from_x_rotation(0.1)
                else:
                    m = create_from_x_rotation(-0.1)
            elif y != 0:
                if y > 0:
                    m = create_from_y_rotation(0.1)
                else:
                    m = create_from_y_rotation(-0.1)
            else:
                if z > 0:
                    m = create_from_z_rotation(0.1)
                else:
                    m = create_from_z_rotation(-0.1)
            self._gl_proxy.rotate_control_points(m)
            self.update_scene.emit()

    @pyqtSlot(int)
    def change_tessellation_level(self, level):
        self._gl_proxy.change_tessellation_level(level)
        self.update_scene.emit()

    @pyqtSlot(float)
    def change_split_factor(self, level):
        self._gl_proxy.change_split_factor(level)
        # self.updateScene.emit()

    @staticmethod
    def check_file_path(file_path):
        if file_path.startswith('file://'):
            file_path = file_path[len('file://'):]
        if not isfile(file_path):
            print('check_file_path:', '文件名错误!')
            return None
        else:
            return file_path

    @pyqtSlot(str)
    def load_file(self, file_path):
        self._loaded_file_path = self.check_file_path(file_path)
        if self._loaded_file_path is None:
            return
        raw_obj = OBJ(file_path=self._loaded_file_path)
        self._gl_proxy.change_model(raw_obj)

    @pyqtSlot()
    def save_ctrl_points(self):
        path = self.get_save_path()
        files = os.listdir(path)
        file_name_prefix = self._loaded_file_path[
                           self._loaded_file_path.rfind('/') + 1:self._loaded_file_path.rfind('.')]
        no = 0
        for f in files:
            if f.startswith(file_name_prefix):
                no += 1
        file_name = '%s/%s_control_points%d' \
                    % (path,
                       file_name_prefix,
                       no)
        points = self._gl_proxy.control_points()
        np.save(file_name, points)

    def get_save_path(self):
        path = self._loaded_file_path[:self._loaded_file_path.rfind('.')] + '_' + self._gl_proxy.get_parameter_str()
        if not exists(path):
            os.mkdir(path)
        return path

    @pyqtSlot(str)
    def load_control_points(self, file_path):
        file_path = self.check_file_path(file_path)
        if file_path is None:
            return
        load = np.load(file_path)
        self._gl_proxy.set_control_points(load)
        self.update_scene.emit()

    @pyqtSlot(int, int)
    def rotate(self, x, y):
        if x == y == 0:
            return
        # update _mode_view_matrix
        self._rotate_matrix = multiply(self._rotate_matrix, util.util.create_rotate(2, y, x, 0))
        scale_matrix = create_from_scale(self._scale, dtype='f4')
        self._model_view_matrix = multiply(self._rotate_matrix,
                                           np.dot(scale_matrix, create_from_translation(self._translate, dtype='f4')))
        self.print_matrix(self._model_view_matrix)
        self.update_scene.emit()

    @pyqtSlot(int, int)
    def move(self, x, y):
        # record rotate_y and rotate_x
        xyz = [x / 100, - y / 100, 0]
        self._translate = [x + y for x, y in zip(self._translate, xyz)]
        # update _mode_view_matrix
        scale_matrix = create_from_scale(self._scale, dtype='f4')
        self._model_view_matrix = multiply(self._rotate_matrix,
                                           np.dot(scale_matrix, create_from_translation(self._translate, dtype='f4')))

        self.print_matrix(self._model_view_matrix)
        self.update_scene.emit()

    @pyqtSlot(bool)
    def set_control_point_visibility(self, is_show: bool):
        self._gl_proxy.set_control_point_visibility(is_show)

    @pyqtSlot(bool)
    def set_show_real(self, is_show: bool):
        self._gl_proxy.set_show_real(is_show)

    @pyqtSlot(bool)
    def set_show_original(self, is_show: bool):
        self._gl_proxy.set_show_original(is_show)

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

    @pyqtSlot(bool)
    def set_use_pn_normal(self, use: bool):
        self._gl_proxy.set_use_pn_normal(use)

    def set_cpu_splited_number(self, n):
        self.cpu_split_number = n

    @pyqtSlot()
    def begin_test_split_factor(self):
        self.diff_result.clear()
        self.splited_number.clear()
        self.area_result.clear()
        self.quality_result.clear()
        self.time_result.clear()
        step = self._gl_proxy.aux_controller.get_bspline_body_size()
        self.cage_length = reduce(lambda p, x: p + x ** 2, step, 0) ** 0.5
        self.factors = np.arange(0.115, 2 * (3 ** 0.5), 0.02, dtype='f4')
        indices = 0
        original_split_factor = self._gl_proxy.previous_compute_controller.split_factor

        def gl_task1():
            nonlocal indices
            print('from begin_test_split_factor indices:', indices)
            if indices < len(self.factors):
                self.change_split_factor(self.factors[indices])
                self.set_need_comparison()
                indices += 1
                self.update_scene.emit()
            else:
                self.change_split_factor(original_split_factor)
                self.show_figure.emit()
                self.gl_task = None

        self.gl_task = gl_task1
        self.update_scene.emit()

    def set_need_comparison(self):
        self._gl_proxy.set_need_comparison()

    @pyqtSlot()
    def begin_diff_comparison(self):
        self.diff_result.clear()

        def gl_task0():
            is_ac = True
            if self._gl_proxy.algorithm != ALGORITHM_AC:
                self._gl_proxy.algorithm = ALGORITHM_AC
                is_ac = False
            self._gl_proxy.set_need_comparison()

            def gl_task1():
                self._gl_proxy.algorithm = ALGORITHM_CYM
                self._gl_proxy.set_need_comparison()

                def gl_task2():
                    if is_ac:
                        self._gl_proxy.algorithm = ALGORITHM_AC
                    self.gl_task = None
                    for ac, cym, label in zip(*self.diff_result, ['位置', '法向']):
                        print(label + '比对: 平均/最大/标准差')
                        print('ac %e / %e / %e' % (ac[0], ac[1], ac[2]))
                        print('cym %e / %e / %e' % (cym[0], cym[1], cym[2]))
                    self.cym_position_error = self.diff_result[1][0][0]

                self.gl_task = gl_task2
                self.update_scene.emit()

            self.gl_task = gl_task1
            self.update_scene.emit()

        self.gl_task = gl_task0
        self.update_scene.emit()

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
                self._gl_proxy.move_direct_control_point(np.array(direction, dtype='f4').reshape(4, )[:3] / 300)
            else:
                start_point = np.mat([0, 0, 0, 1], dtype='f4') * i
                end_point_z = -4
                end_point_y = y2 / self.window_size.h * 2 - 1
                end_point_x = x2 / self.window_size.h * 2 - self.window_size.aspect
                end_point = np.mat([end_point_x, end_point_y, end_point_z, 1], dtype='f4') * i
                self._gl_proxy.set_select_point(start_point, end_point - start_point)
        self.update_scene.emit()

    @pyqtSlot()
    def cancel_direct_control_point(self):
        self._gl_proxy.clear_direct_control_point()
        self.update_scene.emit()

    @pyqtSlot(int, int, int)
    def change_control_point_number(self, u: int, v: int, w: int):
        self._gl_proxy.change_control_point_number(u, v, w)
        self.update_scene.emit()

    @pyqtSlot(int)
    def change_control_point_order(self, order: int):
        self._gl_proxy.change_control_point_order(order)
        self.update_scene.emit()

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
        self._model_view_matrix = np.dot(self._rotate_matrix,
                                         np.dot(scale_matrix, create_from_translation(self._translate, dtype='f4')))

        self.print_matrix(self._model_view_matrix)
        # normal
        # self._model_view_matrix = np.array(
        #     [[-1.64843, -1.10888, 0.230428, 0.0],
        #      [1.01591, -1.26784, 1.16642, 0.0],
        #      [-0.500636, 1.07843, 1.60822, 0.0],
        #      [0.0, 0.0, -8.0, 1.0]])

        # deformation
        # self._model_view_matrix = np.array(
        #     [[-1.33853, -0.952707, -0.436706, 0.0],
        #      [0.663226, -1.31852, 0.84363, 0.0],
        #      [-0.81148, 0.49387, 1.40984, 0.0],
        #      [0.27, 0.02, -8.0, 1.0]])

        self.update_scene.emit()

    @staticmethod
    def print_matrix(matrix):
        print('[', end='')
        for j in range(4):
            print('[', end='')
            for i in range(4):
                if i == 3:
                    print(matrix[j, i], end='')
                else:
                    print(matrix[j, i], end=', ')
            if j == 3:
                print(']', end='')
            else:
                print('],')
        print(']')
        print()

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
        glViewport(*self.window_size.xywh)

        if self._gl_proxy:
            if self.gl_task:
                self.gl_task()
            self._gl_proxy.draw(self._model_view_matrix, self._perspective_matrix)

        glDisable(GL_SCISSOR_TEST)

    @pyqtSlot()
    def paint(self):
        if not self._inited:
            self.gl_init()
            self._inited = True
        self.gl_on_frame_draw()

    @pyqtSlot()
    def save_image(self):
        self._gl_proxy.save_image()

    @pyqtSlot(bool)
    def set_use_texture(self, b):
        self._gl_proxy.use_texture(b)

    @pyqtSlot()
    def export_obj(self):
        self._gl_proxy.export_obj()


def get_test_file_name():
    # todo
    # file_path = "res/3d_model/ttest.obj"
    # file_path = "res/3d_model/cube.obj"
    # file_path = "res/3d_model/test2.obj"
    # file_path = "res/3d_model/bishop.obj"
    # file_path = "res/3d_model/test_same_normal.obj"
    # file_path = "res/3d_model/legoDog.obj"
    # file_path = "res/3d_model/test_2_triangle.obj"
    # file_path = "res/3d_model/test_2_triangle_plain.obj"
    # file_path = "res/3d_model/test_2_triangle.obj"
    ## file_path = "res/3d_model/biship_cym_direct_average_normal.obj"
    # file_path = "res/3d_model/vase_cym.obj"
    # file_path = "res/3d_model/wheel.obj"
    # file_path = "res/3d_model/snail.obj"
    # file_path = "res/3d_model/t.bpt"

    # file_path = "res/3d_model/Mobile.obj"
    # file_path = "res/3d_model/biship_cym_area_average_normal.obj"
    # file_path = "res/3d_model/cube2.obj"
    # file_path = "res/3d_model/sphere.bj"
    # file_path = "res/3d_model/rabbit_cym.obj"
    # file_path = "res/3d_model/star.obj"

    # for renderer effect
    # file_path = 'res/3d_model/rabbit_real/rabbit.obj'
    file_path = 'res/3d_model/ship/ship2.obj'
    return file_path
