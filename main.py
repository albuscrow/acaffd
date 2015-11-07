import logging
import signal

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QUrl
from PyQt5.QtQml import qmlRegisterType, QQmlComponent, QQmlEngine, QQmlListProperty
import sys
from ui.FFDScene import FFDScene
from control.controller import Controller

__author__ = 'ac'
logging.basicConfig(level=logging.DEBUG)

app = QGuiApplication(sys.argv)

qmlRegisterType(FFDScene, 'FFD', 1, 0, "FFDScene")
controller = Controller()

engine = QQmlApplicationEngine()
engine.rootContext().setContextProperty('controller', controller)
engine.load(QUrl('qml/main.qml'))

scene = engine.rootObjects()[0].findChild(FFDScene, 'scene')
controller.connect_with_renderer(scene.renderer)

app.exec()
