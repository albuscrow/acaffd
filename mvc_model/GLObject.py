import numpy as np
from OpenGL.GL import *


class ACSSBO:
    def __init__(self, binding_point: int, data: np.array, usage_hint: int):
        self._buffer_name = glGenBuffers(1)  # type: int
        self._binding_point = binding_point  # type: int
        self._data = data  # type: np.array
        self._dirty = True  # type: bool
        self._usage_hint = usage_hint
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, self._binding_point, self._buffer_name)

    def async_update(self, data):
        self._data = data
        self._dirty = True

    def sync(self):
        if self._dirty:
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self._buffer_name)
            glBufferData(GL_SHADER_STORAGE_BUFFER, len(self), self._data, self._usage_hint)
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)
            self._dirty = False

    def __len__(self):
        print("len", len(self._data) * self._data.itemsize)
        return self._data.size * self._data.itemsize


class ACSSBOOutput(ACSSBO):
    def __init__(self, binding_point: int, capacity: int):
        super().__init__(binding_point, None)
        self._capacity = capacity

    def __len__(self):
        return self._capacity
