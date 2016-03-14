import math
import numpy
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from OpenGL.GL import *
from pyrr.matrix44 import *
from pyrr.euler import *

from ac_opengl.GLProxy import GLProxy
from mvc_model.plain_class import ACRect


class Renderer(QObject):
    pass
