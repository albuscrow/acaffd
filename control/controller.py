import logging
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
from model.model import OBJ, ModelFileFormatType

__author__ = 'ac'


class Controller(QObject):
    read_obj_success = pyqtSignal(OBJ)
    change_rotate = pyqtSignal(int, int)
    show_aux_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

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

    def connect_with_renderer(self, renderer):
        self.read_obj_success.connect(renderer.handle_new_obj)
        self.change_rotate.connect(renderer.change_rotate)
        self.show_aux_signal.connect(renderer.show_aux)
