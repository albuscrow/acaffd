from OpenGL.GL import *
import numpy as np


def bindSSBO(vbo, bind_point, data, size, dtype, usage):
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, vbo)
    if data:
        glBufferData(GL_SHADER_STORAGE_BUFFER, int(size),
                     np.array(data, dtype=dtype),
                     usage=usage)
    else:
        glBufferData(GL_SHADER_STORAGE_BUFFER, int(size),
                     None,
                     usage=usage)
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, bind_point, vbo)
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)
