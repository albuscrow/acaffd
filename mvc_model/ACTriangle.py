from itertools import product

import numpy as np
from functools import reduce

from Constant import ZERO
from mvc_model.aux import BSplineBody
from util.util import normalize


class ACTriangle:
    DATA_TYPE = [('samplePoint', [('parameter', '4f4'),
                                  ('sample_point_original_normal', '4f4'),
                                  ('knot_left_index', '4u4')], 37),
                 ('normal_adj', '4f4', 3),
                 ('adjacency_normal', '4f4', 6),
                 ('original_normal', '4f4', 3),
                 ('original_position', '4f4', 3),
                 ('need_adj', '8i4'),
                 ]

    SAMPLE_PATTERN = np.array([
        [1.000000, 0.000000, 0.000000],

        [0.833333, 0.166667, 0.000000],
        [0.833333, 0.000000, 0.166667],

        [0.666667, 0.333333, 0.000000],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.000000, 0.333333],

        [0.500000, 0.500000, 0.000000],
        [0.500000, 0.333333, 0.166667],
        [0.500000, 0.166667, 0.333333],
        [0.500000, 0.000000, 0.500000],

        [0.333333, 0.666667, 0.000000],
        [0.333333, 0.500000, 0.166667],
        [0.333333, 0.333333, 0.333333],
        [0.333333, 0.166667, 0.500000],
        [0.333333, 0.000000, 0.666667],

        [0.166667, 0.833333, 0.000000],
        [0.166667, 0.666667, 0.166667],
        [0.166667, 0.500000, 0.333333],
        [0.166667, 0.333333, 0.500000],
        [0.166667, 0.166667, 0.666667],
        [0.166667, 0.000000, 0.833333],

        [0.000000, 1.000000, 0.000000],
        [0.000000, 0.833333, 0.166667],
        [0.000000, 0.666667, 0.333333],
        [0.000000, 0.500000, 0.500000],
        [0.000000, 0.333333, 0.666667],
        [0.000000, 0.166667, 0.833333],
        [0.000000, 0.000000, 1.000000],

        [1, 0, 0],
        [0.6667, 0.3333, 0], [0.6667, 0, 0.3333],
        [0.3333, 0.6667, 0], [0.3333, 0, 0.6667],
        [0, 1, 0], [0, 0.6667, 0.3333], [0, 0.3333, 0.6667], [0, 0, 1]], dtype='f4')

    def __init__(self, i):
        self._id = i
        self._position = None  # type: np.array
        self._normal = None  # type: np.array
        self._tex_coord = None  # type: np.array
        self._neighbor = None  # type: list[(ACTriangle, int)]
        self._pn_triangle_p = [None] * 10  # type: list
        self._pn_triangle_n = [None] * 6

    def __str__(self):
        return ','.join([str(x.id if x else None) + '-' + str(y) for x, y in self._neighbor])

    def as_element_for_shader(self, b_spline_body: BSplineBody) -> list:
        data = []
        sample_points = []
        for pattern in ACTriangle.SAMPLE_PATTERN:
            sample_points.append(self.get_sample_point(pattern, b_spline_body))
        data.append(sample_points)
        data.append(self.normal)
        normaladj = np.zeros((6, 4), dtype='f4')
        normaladj[:3, :] = self.normal
        normaladj[3:, :] = self.normal
        data.append(normaladj)
        data.append(self.normal)
        data.append(self.position)
        data.append([-1] * 8)
        return tuple(data)

    def get_sample_point(self, pattern: np.array, b_spline_body: BSplineBody):
        parameter = np.dot(pattern, self._position)
        cage_t_and_left_knot_index = b_spline_body.get_cage_t_and_left_knot_index(parameter)
        return (cage_t_and_left_knot_index[0], np.dot(pattern, self._normal), cage_t_and_left_knot_index[1])

    def genPNTriangle(self):
        # 三个顶点对应的控制顶点
        self._pn_triangle_p[0] = self.position[0]
        self._pn_triangle_p[6] = self.position[1]
        self._pn_triangle_p[9] = self.position[2]

        # 邻接三角形的六个法向nij, i表示近顶点编号, j远顶点编号
        # n02, n01, n10, n12, n21, n20
        n = []
        aux1 = [0, 1, 1, 2, 2, 0]
        aux2, aux3 = zip(*list(product([0, 1, 2], [True, False])))
        for x, y, z in zip(aux1, aux3, aux2):
            n.append(self.get_adjacency_normal(x, y, z))

        aux1 = [0, 0, 1, 1, 2, 2]
        aux2 = [2, 1, 0, 2, 1, 0]
        aux3 = [2, 1, 3, 7, 8, 5]
        for x, y, z, i in zip(aux1, aux2, n, aux3):
            self._pn_triangle_p[i] = self.gen_position_control_point(self.position[x],
                                                                     self.position[y],
                                                                     self.normal[x], z)

        E = reduce(lambda p, x: p + x, [self._pn_triangle_p[x] for x in aux3], np.array([0, 0, 0], dtype='f4')) / 6
        V = reduce(lambda p, x: p + x, [self.position[x] for x in range(3)], np.array([0, 0, 0], dtype='f4')) / 3
        self._pn_triangle_p[4] = E + (E - V) / 2

        # 生成法向PN - triangle
        for i, j in zip([0, 3, 5], self.normal):
            self._pn_triangle_n[i] = j
        for i, j, k in zip([1, 4, 2], [0, 1, 2], [1, 2, 0]):
            self._pn_triangle_n[i] = self.gen_normal_control_point(j, k)

    def get_adjacency_normal(self, triangle_index, flag, original_normal_index):
        triangle, neighbor_edge = self._neighbor[triangle_index]
        if triangle is None:
            return self.normal[original_normal_index]
        else:
            return triangle.normal[neighbor_edge - 1 if flag else neighbor_edge]

    @staticmethod
    def gen_position_control_point(p_s: np.array, p_e: np.array, n: np.array, n_adj: np.array):
        if all(abs(n - n_adj) < ZERO):
            return (2 * p_s + p_e - np.dot((p_e - p_s), n) * n) / 3
        else:
            T = np.cross(n, n_adj)
        return p_s + np.dot((p_e - p_s), T) / 3 * T

    def gen_normal_control_point(self, start, end):
        p_s = self.position[start]
        p_e = self.position[end]
        n_s = self.normal[start]
        n_e = self.normal[end]
        n = normalize(n_s + n_e)
        v = normalize(p_e - p_s)
        return normalize(n - 2 * v * np.dot(n, v))

    @property
    def id(self):
        return self._id

    @property
    def position(self):
        return self._position

    @property
    def normal(self):
        return self._normal

    @property
    def tex_coord(self):
        return self._tex_coord

    @property
    def neighbor(self):
        return self._neighbor

    @position.setter
    def position(self, value):
        self._position = value

    @normal.setter
    def normal(self, value):
        self._normal = value

    @tex_coord.setter
    def tex_coord(self, value):
        self._tex_coord = value

    @neighbor.setter
    def neighbor(self, value):
        self._neighbor = value
