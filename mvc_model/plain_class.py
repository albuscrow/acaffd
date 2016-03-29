class ACRect:
    def __init__(self, *p: tuple):
        if len(p) == 0:
            self._x = 0  # type: int
            self._y = 0  # type: int
            self._w = 0  # type: int
            self._h = 0  # type: int
        elif len(p) == 4:
            self._x = p[0]  # type: int
            self._y = p[1]  # type: int
            self._w = p[2]  # type: int
            self._h = p[3]  # type: int
        else:
            raise Exception("wrong parameter number")

    def update(self, window_parameter: tuple):
        self._x, self._y, self._w, self._h = [int(x) for x in window_parameter]

    @property
    def aspect(self) -> float:
        return self._w / self._h

    @property
    def xywh(self) -> tuple:
        return self._x, self._y, self._w, self._h

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def x1(self):
        return self._x

    @property
    def y1(self):
        return self._y

    @property
    def x2(self):
        return self._x + self._w

    @property
    def y2(self):
        return self._y + self._h

    @property
    def w(self):
        return self._w

    @property
    def h(self):
        return self._h

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x \
                   and self.y == other.y \
                   and self.w == other.w \
                   and self.h == other.h
        elif isinstance(other, tuple):
            return len(other) == 4 \
                   and self.x == other[0] \
                   and self.y == other[1] \
                   and self.w == other[2] \
                   and self.h == other[3]
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str([self.x, self.y, self._w, self._h])
