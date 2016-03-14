from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtQuick import QQuickItem

from mvc_control.Renderer import Renderer
from mvc_control.controller import Controller

__author__ = 'ac'


class FFDScene(QQuickItem):
    def __init__(self, parent):
        super().__init__(parent)
        self.renderer = Renderer()
        self._controller = Controller()  # type: Controller
        # noinspection PyUnresolvedReferences
        self.windowChanged.connect(self.handle_window_changed, type=Qt.DirectConnection)  # type: pyqtSignal

    @property
    def controller(self) -> Controller:
        return self._controller

    @controller.setter
    def controller(self, _controller: Controller) -> None:
        self._controller = _controller

    @pyqtSlot()
    def sync(self):
        r = self.window().devicePixelRatio()
        p = self.parentItem()
        self.renderer.set_view_port(p.x() * r, p.y() * r, p.width() * r, p.height() * r)

    @pyqtSlot(object)
    def handle_window_changed(self, window):
        if window:
            window.beforeSynchronizing.connect(self.sync, type=Qt.DirectConnection)
            window.afterRendering.connect(self.renderer.paint, type=Qt.DirectConnection)
            window.setClearBeforeRendering(False)
            self.renderer.updateScene.connect(window.update)
            # self.renderer.resetOpenGLStatus.connect(window.resetOpenGLStatus)
