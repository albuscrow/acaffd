import math
import numpy
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from OpenGL.GL import *
from pyrr.matrix44 import *
from pyrr.euler import *

from ac_opengl.GLProxy import GLProxy
from mvc_model.plain_class import ACRect


class Renderer(QObject):
    updateScene = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.need_update_control_point = False
        self._window_size = ACRect()  # type: ACRect

        self.rotate_x = 0
        self.rotate_y = 0

        self.perspective_matrix = None

        self.translation_matrix = create_from_translation(numpy.array([0, 0, -8]), dtype='float32')

        self.model_view_matrix = self.translation_matrix

        self.model = None
        self.b_spline_body = None
        self.need_deform = False

        self.inited = False  # type: bool

    @property
    def window_size(self):
        return self._window_size

    def gl_on_view_port_change(self, *xywh):
        if self.window_size != xywh:
            self.window_size.update(xywh)
            aspect = self.window_size.aspect
            self.perspective_matrix = create_perspective_projection_matrix_from_bounds(-aspect, aspect, -1,
                                                                                       1, 4, 100,
                                                                                       dtype='float32')

    def gl_init(self) -> None:
        glClearColor(1, 1, 1, 1)

    def gl_on_frame_draw(self) -> None:
        glEnable(GL_SCISSOR_TEST)
        glScissor(*self.window_size.xywh)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # todo 这句理论上应该在gl_on_view_port_change调用，但是会有问题
        glViewport(*self.window_size.xywh)

        if self.model:
            self.model.draw(self.model_view_matrix, self.perspective_matrix)

        glDisable(GL_SCISSOR_TEST)

    @pyqtSlot()
    def paint(self):
        if not self.inited:
            self.gl_init()
            self.inited = True
        self.gl_on_frame_draw()

    def handle_new_obj(self, obj):
        self.model = GLProxy(obj)

    def change_rotate(self, x, y):
        self.rotate_y += x
        self.rotate_x += y

        self.model_view_matrix = multiply(create_from_eulers(create(-self.rotate_x / 180 * math.pi, 0,
                                                                    -self.rotate_y / 180 * math.pi), dtype='float32'),
                                          self.translation_matrix)
        self.updateScene.emit()

    def show_aux(self, is_show):
        self.model._show_control_point = is_show

    def select(self, x, y, x2, y2):
        self.model.set_select_region(x, self.window_size.h - y2, x2, self.window_size.h - y)
        self.updateScene.emit()

    def move_control_points(self, x, y, z):
        self.model.move_control_points(x, y, z)
        self.updateScene.emit()

    def change_tessellation_level(self, level):
        self.model.change_tessellation_level(level)
        self.updateScene.emit()

    def change_control_point(self, u, v, w):
        self.model.change_control_point(u, v, w)
        self.updateScene.emit()
