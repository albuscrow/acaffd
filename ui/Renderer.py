import math
import numpy
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from OpenGL.GL import *
from pyrr.matrix44 import *
from pyrr.euler import *
from queue import Queue
from shader.GLProxy import GLProxy


class Renderer(QObject):
    updateScene = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.need_update_control_point = False
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.gl_task = Queue()
        self.model = None
        self.renderer_aux_task = None

        self.rotate_x = 0
        self.rotate_y = 0

        self.perspective_matrix = None

        self.translation_matrix = create_from_translation(numpy.array([0, 0, -8]), dtype='float32')

        self.model_view_matrix = self.translation_matrix

        self.model = None
        self.b_spline_body = None
        self.need_deform = False

    def set_view_port(self, x, y, w, h):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

        aspect = self.w / self.h
        self.perspective_matrix = create_perspective_projection_matrix_from_bounds(-aspect, aspect, -1,
                                                                                   1, 4, 100,
                                                                                   dtype='float32')

    @pyqtSlot()
    def paint(self):
        if not self.gl_task.empty():
            task = self.gl_task.get()
            task()
            self.gl_task.task_done()

        glViewport(self.x, self.y, self.w, self.h)
        glEnable(GL_SCISSOR_TEST)
        glScissor(self.x, self.y, self.w, self.h)
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.model:
            self.model.draw(self.model_view_matrix, self.perspective_matrix)

        glDisable(GL_SCISSOR_TEST)

    def handle_new_obj(self, obj):
        self.model = obj
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
        self.model.set_select_region(x, self.h - y2, x2, self.h - y)
        self.updateScene.emit()

    def move_control_points(self, x, y, z):
        self.model.move_control_points(x, y, z)
        self.updateScene.emit()

    def change_tessellation_level(self, level):
        self.model.change_tessellation_level(level)
        self.updateScene.emit()

