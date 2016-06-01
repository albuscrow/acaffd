import logging
import threading

from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QUrl
from PyQt5.QtQml import qmlRegisterType
from PyQt5.QtWidgets import QApplication
from mvc_control.controller import Controller
import sys, signal
from mvc_view.FFDScene import FFDScene
from util.util import filter_for_speed

__author__ = 'ac'

# logging.basicConfig(level=logging.DEBUG)
app = QApplication(sys.argv)

signal.signal(signal.SIGINT, signal.SIG_DFL)


qmlRegisterType(FFDScene, 'FFD', 1, 0, "FFDScene")
# controller = Controller()

engine = QQmlApplicationEngine()
engine.load(QUrl(filter_for_speed(file_name='res/ui/main.qml')))
scene = engine.rootObjects()[0].findChild(FFDScene, 'scene')

controller = scene.controller  # type: Controller
engine.rootContext().setContextProperty('controller', controller)

# print('main thread:', threading.current_thread().ident)
# app.exec()
sys.exit(app.exec())
