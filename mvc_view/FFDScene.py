from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtQuick import QQuickItem, QQuickWindow

from mvc_control.controller import Controller

__author__ = 'ac'


class FFDScene(QQuickItem):
    def __init__(self, parent):
        super().__init__(parent)
        self._controller = Controller()  # type: Controller
        # noinspection PyUnresolvedReferences
        self.windowChanged.connect(self.handle_window_changed, type=Qt.DirectConnection)

    @property
    def controller(self) -> Controller:
        return self._controller

    @controller.setter
    def controller(self, _controller: Controller) -> None:
        self._controller = _controller

    @pyqtSlot()
    def sync(self):
        r = self.window().devicePixelRatio()
        p = self.parentItem()  # type: QQuickItem
        # self.controller.gl_on_view_port_change(p.x() * r, p.y() * r, 1024, 1024)
        self.controller.gl_on_view_port_change(p.x() * r, p.y() * r, p.width() * r, p.height() * r)

    def handle_window_changed(self, window):
        if window:
            window.beforeSynchronizing.connect(self.sync, type=Qt.DirectConnection)
            window.afterRendering.connect(self.controller.paint, type=Qt.DirectConnection)
            window.setClearBeforeRendering(False)
            self.controller.update_scene.connect(window.update)
            # self.renderer.resetOpenGLStatus.connect(window.resetOpenGLStatus)
