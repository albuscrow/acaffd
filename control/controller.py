import logging
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
from model.RawOBJModel import OBJ, ModelFileFormatType

__author__ = 'ac'


class Controller(QObject):
    read_obj_success = pyqtSignal(OBJ)

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

    def connect_with_renderer(self, renderer):
        self.read_obj_success.connect(renderer.handle_new_obj)
