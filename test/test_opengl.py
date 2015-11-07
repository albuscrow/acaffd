import OpenGL.GL as gl
import OpenGL.GLUT as glut
import sys
from threading import Thread
from time import sleep


def display():
    glut.glutSwapBuffers()


def reshape(width, height):
    gl.glViewport(0, 0, width, height)


def keyboard(key, x, y):
    print(key)
    if key == '\033':
        sys.exit()


glut.glutInit()
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
glut.glutCreateWindow('hello world!')
glut.glutReshapeWindow(512, 512)
glut.glutReshapeFunc(reshape)
glut.glutDisplayFunc(display)
glut.glutKeyboardFunc(keyboard)
print('opengl version: ' + str(gl.glGetString(gl.GL_VERSION)))
thread = Thread(target=lambda: print("opengl version: " + str(gl.glGetString(gl.GL_VERSION))))
thread.start()
thread.join()

glut.glutMainLoop()
