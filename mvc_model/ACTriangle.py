from itertools import product

import numpy as np
from functools import reduce

from Constant import ZERO
from mvc_model.aux import BSplineBody
from util.util import normalize, equal_vec
from math import pow, factorial

SPLIT_PARAMETER_CHANGE_AUX = [[1, 0, 2], [0, 2, 1], [2, 1, 0]]


class ACTriangle:
    DATA_TYPE = [('samplePoint', [('parameter', '4f4'),
                                  ('sample_point_original_normal', '4f4'),
                                  ('knot_left_index', '4u4')], 37),
                 ('normal_adj', '4f4', 3),
                 ('adjacency_normal', '4f4', 6),
                 ('original_normal', '4f4', 3),
                 ('original_position', '4f4', 3),
                 ('need_adj', '4i4'),
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
        self._is_original_edge = [True, True, True]  # type: list
        self._parameter = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype='f4')

    def __str__(self):
        return ','.join([str(x.id if x else None) + '-' + str(y) for x, y in self._neighbor])

    def as_element_for_shader(self, b_spline_body: BSplineBody) -> list:
        data = []
        sample_points = []
        for pattern in ACTriangle.SAMPLE_PATTERN:
            sample_points.append(self.get_sample_point(pattern, b_spline_body))
        data.append(sample_points)

        # ('normal_adj', '4f4', 3),
        # ('adjacency_normal', '4f4', 6),
        # ('original_normal', '4f4', 3),
        # ('original_position', '4f4', 3),
        # ('need_adj', '8i4'),

        # v4
        pn_normal = [self.get_normal_in_pn_triangle(x) for x in self._parameter]

        # v4
        pn_normal_adjacent = np.zeros((6, 4), dtype='f4')
        is_sharp = []
        aux1 = [2, 0, 0, 1, 1, 2]
        aux2 = [5, 0, 1, 2, 3, 4]
        for i in range(3):
            if not self._is_original_edge[i]:
                # 是内部三角形
                is_sharp.append(-1)
            else:
                if self.neighbor[i][0] is None:
                    # 没有邻接三角形
                    is_sharp.append(-1)
                else:
                    is_sharp.append(-1)
                    for j in range(2):
                        index = i * 2 + j
                        adjacent_parameter = self.transform_parameter(self._parameter[aux1[index]], i)
                        adjacent_normal = self.neighbor[i][0].get_normal_in_pn_triangle(adjacent_parameter)
                        pn_normal_adjacent[aux2[index]] = adjacent_normal
                        if not equal_vec(adjacent_normal, pn_normal[aux1[index]]):
                            is_sharp[-1] = 1

        data.append(pn_normal)
        data.append(pn_normal_adjacent)
        data.append(self.normalv4)
        data.append(self.positionv4)
        data.append(is_sharp + [-1])
        # print(pn_normal)
        # print(pn_normal_adjacent.shape)
        # print(sample_points)
        return tuple(data)

    def transform_parameter(self, parameter, edge_index):
        unchange = SPLIT_PARAMETER_CHANGE_AUX[edge_index][self.neighbor[edge_index][1]]
        aux = None
        if unchange == 0:
            aux = [0, 2, 1]
            # return parameter.xzy
        elif unchange == 1:
            aux = [2, 1, 0]
            # return parameter.zyx
        else:
            aux = [1, 0, 2]
            # return parameter.yxz
        return np.array([parameter[x] for x in aux], dtype='f4')

    def get_sample_point(self, pattern: np.array, b_spline_body: BSplineBody):
        parameter = np.dot(pattern, self.positionv3)
        cage_t_and_left_knot_index = b_spline_body.get_cage_t_and_left_knot_index(parameter)
        return cage_t_and_left_knot_index[0], np.dot(pattern, self.normalv4), cage_t_and_left_knot_index[1]

    def gen_pn_triangle(self):
        # 三个顶点对应的控制顶点
        self._pn_triangle_p[0] = self.positionv3[0]
        self._pn_triangle_p[6] = self.positionv3[1]
        self._pn_triangle_p[9] = self.positionv3[2]

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
            self._pn_triangle_p[i] = self.gen_position_control_point(self.positionv3[x],
                                                                     self.positionv3[y],
                                                                     self.normalv3[x], z)

        E = reduce(lambda p, x: p + x, [self._pn_triangle_p[x] for x in aux3], np.array([0, 0, 0], dtype='f4')) / 6
        V = reduce(lambda p, x: p + x, [self.positionv3[x] for x in range(3)], np.array([0, 0, 0], dtype='f4')) / 3
        self._pn_triangle_p[4] = E + (E - V) / 2

        # 生成法向PN - triangle
        for i, j in zip([0, 3, 5], self.normalv3):
            self._pn_triangle_n[i] = j
        for i, j, k in zip([1, 4, 2], [0, 1, 2], [1, 2, 0]):
            self._pn_triangle_n[i] = self.gen_normal_control_point(j, k)

    def get_adjacency_normal(self, triangle_index, flag, original_normal_index):
        triangle, neighbor_edge = self._neighbor[triangle_index]
        if triangle is None:
            return self.normalv3[original_normal_index]
        else:
            return triangle.normalv3[neighbor_edge - 1 if flag else neighbor_edge]

    @staticmethod
    def gen_position_control_point(p_s: np.array, p_e: np.array, n: np.array, n_adj: np.array):
        if all(abs(n - n_adj) < ZERO):
            return (2 * p_s + p_e - np.dot((p_e - p_s), n) * n) / 3
        else:
            # print(n, n_adj)
            T = np.cross(n, n_adj)
        return p_s + np.dot((p_e - p_s), T) / 3 * T

    # def gen_normal_control_point(self, start, end):
    #     p_s = self.positionv3[start]
    #     p_e = self.positionv3[end]
    #     n_s = self.normalv3[start]
    #     n_e = self.normalv3[end]
    #     n = normalize(n_s + n_e)
    #     v = normalize(p_e - p_s)
    #     return normalize(n - 2 * v * np.dot(n, v))

    def gen_normal_control_point(self, start, end):
        p_s = self.positionv3[start]
        p_e = self.positionv3[end]
        n_s = self.normalv3[start]
        n_e = self.normalv3[end]
        n = n_s + n_e
        v = p_e - p_s
        return normalize(n - 2 * np.dot(n, v) / np.dot(v, v) * v)

    def get_position_in_pn_triangle(self, parameter: np.array):
        result = np.array([0] * 4, dtype='f4')
        ctrl_point_index = 0
        for i in range(3, -1, -1):
            for j in range(3 - i, -1, -1):
                k = 3 - i - j
                n = 6.0 * pow(parameter[0], i) * pow(parameter[1], j) * pow(parameter[2], k) \
                    / factorial(i) / factorial(j) / factorial(k)
                result += self._pn_triangle_p[ctrl_point_index] * n
                ctrl_point_index += 1
        return result

    def get_normal_in_pn_triangle(self, parameter: np.array):
        result = np.array([0] * 3, dtype='f4')
        ctrl_point_index = 0
        for i in range(2, -1, -1):
            for j in range(2 - i, -1, -1):
                k = 2 - i - j
                n = 2.0 * pow(parameter[0], i) * pow(parameter[1], j) * pow(parameter[2], k) \
                    / factorial(i) / factorial(j) / factorial(k)
                result += self._pn_triangle_n[ctrl_point_index] * n
                ctrl_point_index += 1
        return np.append(normalize(result), 0)

    @property
    def id(self):
        return self._id

    @property
    def positionv4(self):
        return self._position

    @property
    def normalv4(self):
        return self._normal

    @property
    def positionv3(self):
        return self._position[:, :3]

    @property
    def normalv3(self):
        return self._normal[:, :3]

    @property
    def tex_coord(self):
        return self._tex_coord

    @property
    def neighbor(self):
        return self._neighbor

    @positionv4.setter
    def positionv4(self, value):
        self._position = value

    @normalv4.setter
    def normalv4(self, value):
        self._normal = value

    @tex_coord.setter
    def tex_coord(self, value):
        self._tex_coord = value

    @neighbor.setter
    def neighbor(self, value):
        self._neighbor = value
