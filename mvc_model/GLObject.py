import numpy as np
from OpenGL.GL import *


class ACSSBO:
    def __init__(self, binding_point: int, data: np.array, usage_hint: int):
        self._buffer_name = glGenBuffers(1)  # type: int
        self._binding_point = binding_point  # type: int
        self._data = data  # type: np.array
        if self._data is not None:
            self._capacity = self._data.size * self._data.itemsize  # type: int
        else:
            self._capacity = -1  # type: int
        self._dirty = True  # type: bool
        self._usage_hint = usage_hint
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, self._binding_point, self._buffer_name)

    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, capacity: int):
        self._capacity = int(capacity)

    def async_update(self, data):
        self._data = data
        self._dirty = True

    def gl_sync(self):
        if self._dirty:
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self._buffer_name)
            glBufferData(GL_SHADER_STORAGE_BUFFER, len(self), self._data, self._usage_hint)
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)
            self._dirty = False

    def __len__(self) -> int:
        if self._capacity <= 0:
            raise Exception("capacity error")
        return self._capacity
