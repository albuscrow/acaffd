import _ctypes
import numpy as np
from OpenGL.GL import *


class ACVBO:
    def __init__(self, target: int, binding_point: int, data: np.array, usage_hint: int):
        self._buffer_name = glGenBuffers(1)  # type: int
        self._binding_point = binding_point  # type: int
        self._target = target
        self._data = data  # type: np.array
        if self._data is not None:
            self._capacity = self._data.size * self._data.itemsize  # type: int
        else:
            self._capacity = -1  # type: int
        self._dirty = True  # type: bool
        self._usage_hint = usage_hint
        if target == GL_ARRAY_BUFFER:
            self._is_bind = True
        else:
            self._is_bind = False

    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, capacity: int):
        self._capacity = int(capacity)

    def async_update(self, data):
        if data is None:
            raise Exception("input data can not be None")
        self._data = data
        self._capacity = self._data.size * self._data.itemsize  # type: int
        self._dirty = True

    def gl_sync(self):
        if not self._is_bind:
            glBindBufferBase(self._target, self._binding_point, self._buffer_name)
            self._is_bind = True
        if self._dirty:
            glBindBuffer(self._target, self._buffer_name)
            glBufferData(self._target, len(self), self._data, self._usage_hint)
            glBindBuffer(self._target, 0)
            self._dirty = False

    def get_value(self, buffer_type):
        glBindBuffer(self._target, self._buffer_name)
        pointer_to_buffer = glMapBuffer(self._target, GL_READ_ONLY)
        vbo_pointer = ctypes.cast(pointer_to_buffer, ctypes.POINTER(buffer_type))
        vbo_array = np.ctypeslib.as_array(vbo_pointer, (1, ))
        glUnmapBuffer(self._target)
        return vbo_array

    def get_value2(self, buffer_type):
        glBindBuffer(self._target, self._buffer_name)
        pointer_to_buffer = glMapBuffer(self._target, GL_READ_ONLY)
        vbo_pointer = ctypes.cast(pointer_to_buffer, ctypes.POINTER(buffer_type))
        vbo_array = np.ctypeslib.as_array(vbo_pointer, (100, 4))
        glUnmapBuffer(self._target)
        return vbo_array

    def __len__(self) -> int:
        if self._capacity <= 0:
            raise Exception("capacity error")
        return self._capacity

    def as_array_buffer(self, location, size, type):
        glBindBuffer(GL_ARRAY_BUFFER, self._buffer_name)
        glEnableVertexAttribArray(location)
        glVertexAttribPointer(location, size, type, False, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def as_element_array_buffer(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._buffer_name)