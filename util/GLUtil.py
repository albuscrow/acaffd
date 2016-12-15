from OpenGL.GL import *
import numpy as np
import config as conf


def bind_ssbo(vbo, binding_point, data, size, dtype, usage):
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, vbo)
    if data:
        if dtype:
            glBufferData(GL_SHADER_STORAGE_BUFFER, int(size),
                         np.array(data, dtype=dtype),
                         usage=usage)
        else:
            glBufferData(GL_SHADER_STORAGE_BUFFER, int(size),
                         data,
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
    glBindBuffer(GL_UNIFORM_BUFFER, 0)


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


tag_repeat = {}

class tp:
    def __init__(self, tag, repeat):
        self.tag = tag
        self.repeat_times = repeat
        self.total_time = 0
        self.current = self.repeat_times

    def reset(self):
        self.total_time = 0
        self.current = self.repeat_times

    def add_time(self, time):
        self.total_time += time
        self.current -= 1
        if self.current == 0:
            # print(self.tag, ": ", self.total_time / self.repeat_times, 'ms')
            self.reset()


def gl_timing(op, tag, repeat=1):
    if tag not in tag_repeat:
        tag_repeat[tag] = tp(tag, repeat)

    t = tag_repeat[tag]

    query_id = glGenQueries(1)
    glFinish()
    glBeginQuery(GL_TIME_ELAPSED, query_id)
    op()
    glFinish()
    glEndQuery(GL_TIME_ELAPSED)
    stop_timer_available = 0
    while stop_timer_available == 0:
        stop_timer_available = glGetQueryObjectiv(query_id, GL_QUERY_RESULT_AVAILABLE)

    run_time = glGetQueryObjectiv(query_id, GL_QUERY_RESULT) / 1000000
    t.add_time(run_time)

    return run_time
