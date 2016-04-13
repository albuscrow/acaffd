import logging
import threading

from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QUrl
from PyQt5.QtQml import qmlRegisterType
from PyQt5.QtWidgets import QApplication
from mvc_control.controller import Controller
import sys
from mvc_view.FFDScene import FFDScene

__author__ = 'ac'
# logging.basicConfig(level=logging.DEBUG)
app = QApplication(sys.argv)

qmlRegisterType(FFDScene, 'FFD', 1, 0, "FFDScene")
# controller = Controller()

engine = QQmlApplicationEngine()
engine.load(QUrl('res/ui/main.qml'))
scene = engine.rootObjects()[0].findChild(FFDScene, 'scene')

controller = scene.controller  # type: Controller
engine.rootContext().setContextProperty('controller', controller)

# print('main thread:', threading.current_thread().ident)
app.exec()
