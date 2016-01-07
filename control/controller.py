import logging
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
from model.model import OBJ, ModelFileFormatType

__author__ = 'ac'


class Controller(QObject):
    def __init__(self):
        super().__init__()
        self.renderer = None

    @pyqtSlot(float, float, float)
    def move_control_points(self, x, y, z):
        self.renderer.move_control_points(x, y, z)

    @pyqtSlot(int)
    def change_tessellation_level(self, level):
        self.renderer.change_tessellation_level(level)


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
        self.renderer.handle_new_obj(raw_obj)
        self.renderer.show_aux(True)

    @pyqtSlot(int, int)
    def move(self, x, y):
        self.renderer.change_rotate(x, y)

    @pyqtSlot(int, int)
    def release_mouse(self, x, y):
        self.set_rotate()

    @pyqtSlot(bool)
    def show_aux(self, is_show):
        self.renderer.show_aux(is_show)

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
        self.renderer.select(minx, miny, maxx, maxy)

    @pyqtSlot(int, int, int)
    def change_control_point_number(self, u, v, w):
        self.renderer.change_control_point(u, v, w)

    @pyqtSlot(int)
    def zoom(self, delta):
        # self.renderer.change_control_point(u, v, w)
        pass

    def connect_with_renderer(self, renderer):
        self.renderer = renderer

        # todo test code
        # raw_obj = OBJ("data/767.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/ttest.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/test2.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/bishop.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/test_same_normal.obj", ModelFileFormatType.obj)
        raw_obj = OBJ("data/star.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/legoDog.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/test_2_triangle.obj", ModelFileFormatType.obj)
        # raw_obj = OBJ("data/Mobile.obj", ModelFileFormatType.obj)
        self.renderer.handle_new_obj(raw_obj)
        self.renderer.show_aux(True)
