import logging
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
from model.model import OBJ, ModelFileFormatType
import shader.ShaderUtil as su

__author__ = 'ac'


class Controller(QObject):
    read_obj_success = pyqtSignal(OBJ)
    change_rotate = pyqtSignal(int, int)
    show_aux_signal = pyqtSignal(bool)
    send_select = pyqtSignal(int, int, int, int)
    move_control_points = pyqtSignal(float, float, float)

    def __init__(self):
        super().__init__()
        self.tessellationLevel = 2
        su.shader_parameter.init_tessllation_level(self.tessellationLevel)

    @pyqtSlot(int)
    def change_tessellation_level(self):
        su.shader_parameter.init_tessllation_level(self.tessellationLevel)

    @pyqtSlot(str)
    def load_file(self, file_url):
        """
        :param file_url:
        :type file_url: str
        :return:
        """
        if file_url.startswith('file://'):
            file_url = file_url[len('file://'):]
        raw_obj = OBJ(file_url, ModelFileFormatType.obj)
        self.read_obj_success.emit(raw_obj)
        self.show_aux_signal.emit(True)

    @pyqtSlot(int, int)
    def move(self, x, y):
        self.change_rotate.emit(x, y)

    @pyqtSlot(int, int)
    def release_mouse(self, x, y):
        self.set_rotate()

    @pyqtSlot(bool)
    def show_aux(self, is_show):
        self.show_aux_signal.emit(is_show)

    @pyqtSlot(int, int, int, int)
    def select(self, x, y, x2, y2):
        if x > x2:
            minx = x2
            maxx = x
        else:
            minx = x
            maxx = x2

        if y > y2:
            miny = y2
            maxy = y
        else:
            miny = y
            maxy = y2
        self.send_select.emit(minx, miny, maxx, maxy)

    def connect_with_renderer(self, renderer):
        self.read_obj_success.connect(renderer.handle_new_obj)
        self.change_rotate.connect(renderer.change_rotate)
        self.show_aux_signal.connect(renderer.show_aux)
        self.send_select.connect(renderer.select)
        self.move_control_points.connect(renderer.move_control_points)
        # todo test code
        # raw_obj = OBJ("data/767.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/ttest.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/test2.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/bishop.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/test_same_normal.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/star.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/legoDog.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/test_2_triangle.obj", ModelFileFormatType.obj)
        raw_obj = OBJ("data/Mobile.obj", ModelFileFormatType.obj)
        self.read_obj_success.emit(raw_obj)
        self.show_aux_signal.emit(True)
