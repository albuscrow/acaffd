import logging
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
from model.RawOBJModel import OBJ, ModelFileFormatType
from model.BSplineBody import BSplineBody

__author__ = 'ac'


class Controller(QObject):
    read_obj_success = pyqtSignal(OBJ)
    change_rotate = pyqtSignal(int, int)
    set_rotate = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.b_spline_body = BSplineBody()

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
        self.draw_b_spline_body.emit(self.b_spline_body)

    @pyqtSlot(int, int)
    def move(self, x, y):
        self.change_rotate.emit(x, y)

    @pyqtSlot(int, int)
    def release_mouse(self, x, y):
        self.set_rotate()

    def connect_with_renderer(self, renderer):
        self.read_obj_success.connect(renderer.handle_new_obj)
        self.change_rotate.connect(renderer.change_rotate)
        self.draw_b_spline_body.connect(renderer.draw_b_spline_body)
