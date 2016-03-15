import logging
import signal

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QUrl
from PyQt5.QtQml import qmlRegisterType, QQmlComponent, QQmlEngine, QQmlListProperty
import sys
from mvc_view.FFDScene import FFDScene
from OpenGL.GL import *
import numpy as np

__author__ = 'ac'
# logging.basicConfig(level=logging.DEBUG)
app = QGuiApplication(sys.argv)

qmlRegisterType(FFDScene, 'FFD', 1, 0, "FFDScene")
# controller = Controller()

engine = QQmlApplicationEngine()
engine.load(QUrl('res/ui/main.qml'))
scene = engine.rootObjects()[0].findChild(FFDScene, 'scene')

controller = scene.controller
engine.rootContext().setContextProperty('controller', controller)

app.exec()
