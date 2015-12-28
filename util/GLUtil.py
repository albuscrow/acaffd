from OpenGL.GL import *
import numpy as np


def bind_ssbo(vbo, binding_point, data, size, dtype, usage):
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, vbo)
    if data:
        glBufferData(GL_SHADER_STORAGE_BUFFER, int(size),
                     np.array(data, dtype=dtype),
                     usage=usage)
    else:
        glBufferData(GL_SHADER_STORAGE_BUFFER, int(size),
                     None,
                     usage=usage)
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, binding_point, vbo)
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)


def bind_ubo(bspline_body_buffer, binding_point, data, size):
    glBindBuffer(GL_UNIFORM_BUFFER, bspline_body_buffer)
    glBufferData(GL_UNIFORM_BUFFER, size, data, usage=GL_STATIC_DRAW)
    glBindBufferBase(GL_UNIFORM_BUFFER, binding_point, bspline_body_buffer)


def set_atomic_value(atomic_buffer, binding_point, data=None, size=4):
    if data is None:
        data = [0]
    glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, atomic_buffer)
    glBufferData(GL_ATOMIC_COUNTER_BUFFER, size, np.array(data, dtype='uint32'),
                 usage=GL_DYNAMIC_DRAW)
    glBindBufferBase(GL_ATOMIC_COUNTER_BUFFER, binding_point, atomic_buffer)
    glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, 0)


def get_atomic_value(atomic_buffer):
    glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, atomic_buffer)
    pointer_to_buffer = glMapBuffer(GL_ATOMIC_COUNTER_BUFFER, GL_READ_ONLY)
    vbo_pointer = ctypes.cast(pointer_to_buffer, ctypes.POINTER(ctypes.c_uint32))
    vbo_array = np.ctypeslib.as_array(vbo_pointer, (1,))
    glUnmapBuffer(GL_ATOMIC_COUNTER_BUFFER)
    return vbo_array[0]
