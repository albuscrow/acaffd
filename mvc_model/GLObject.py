import _ctypes
import numpy as np
from OpenGL.GL import *


class ACVBO:
    def __init__(self, target: int, binding_point: int, data: np.array, usage_hint: int):
        self._buffer_name = -1  # type: int
        self._binding_point = binding_point  # type: int
        self._target = target
        self._data = data  # type: np.array
        if self._data is not None:
            self._capacity = self._data.size * self._data.itemsize  # type: int
        else:
            self._capacity = -1  # type: int
        self._dirty = True  # type: bool
        self._usage_hint = usage_hint
        if target == GL_ARRAY_BUFFER or target == GL_ELEMENT_ARRAY_BUFFER:
            self._is_bind = True
        else:
            self._is_bind = False

    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, capacity: int):
        if self._capacity == capacity:
            return
        self._capacity = int(capacity)
        self._data = None
        self._dirty = True

    def async_update(self, data: np.array):
        if data is None:
            raise Exception("input data can not be None")
        self._data = data
        self._capacity = self._data.size * self._data.itemsize  # type: int
        self._dirty = True

    @property
    def buffer_name(self):
        if self._buffer_name == -1:
            self._buffer_name = glGenBuffers(1)
        return self._buffer_name

    def gl_sync(self):
        if len(self) == 0:
            return

        if not self._is_bind:
            glBindBufferBase(self._target, self._binding_point, self.buffer_name)
            self._is_bind = True

        if self._dirty:
            glBindBuffer(self._target, self.buffer_name)
            glBufferData(self._target, len(self), self._data, self._usage_hint)
            glBindBuffer(self._target, 0)
            self._dirty = False

    def get_value(self, buffer_type, shape: tuple = (1,)) -> np.array:
        glBindBuffer(self._target, self.buffer_name)
        pointer_to_buffer = glMapBuffer(self._target, GL_READ_ONLY)
        vbo_pointer = ctypes.cast(pointer_to_buffer, ctypes.POINTER(buffer_type))
        vbo_array = np.ctypeslib.as_array(vbo_pointer, shape)
        glUnmapBuffer(self._target)
        return vbo_array

    def __len__(self) -> int:
        if self._capacity < 0:
            raise Exception("capacity error:", self._capacity)
        return self._capacity

    def as_array_buffer(self, location, size, data_type: int):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_name)
        glEnableVertexAttribArray(location)
        glVertexAttribPointer(location, size, data_type, False, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def as_element_array_buffer(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffer_name)

        if self._target == GL_ELEMENT_ARRAY_BUFFER:
            print("bind ok")

    def __del__(self):
        if self._buffer_name != -1:
            print('delete vbo')
            glDeleteBuffers(1, self._buffer_name)
