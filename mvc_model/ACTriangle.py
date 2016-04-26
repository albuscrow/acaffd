from itertools import product

import numpy as np
from functools import reduce
from numbers import Number

from numpy.linalg import LinAlgError

from Constant import ZERO
from mvc_model.aux import BSplineBody
from util.util import normalize, equal_vec
from math import pow, factorial, sqrt
import config as conf

SPLIT_PARAMETER_CHANGE_AUX = [[1, 0, 2], [0, 2, 1], [2, 1, 0]]

SPLIT_PARAMETER_EDGE_INFO_AUX = [-1, 2, 0, -1, 1, -1, -1]

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


class ACPoly:
    class Point:
        def __init__(self, p, n, t, para, uv):
            self.position = p  # type: np.array
            self.normal = n  # type: np.array
            self.tex_coord = t  # type: np.array
            self.parameter = para  # type: np.array
            self.bezier_uv = uv
            self.is_new = False

        def large_than(self, component, value):
            return self.position[component] > value

        @staticmethod
        def split(p1, p2, component, value):
            t = (value - p1.position[component]) / (p2.position[component] - p1.position[component])

            if abs(t - 0) < ZERO:
                return [], [p1, p2]
            elif abs(t - 1) < ZERO:
                return [p2], [p2]
            else:
                mid = p1 * (1 - t) + p2 * t
                mid.is_new = True
                return [mid], [mid, p2]

        def __eq__(self, other):
            return all(abs(self.position - other.position) < ZERO)

        def __add__(self, other):
            if isinstance(other, ACPoly.Point):
                res = ACPoly.Point(self.position + other.position,
                                   self.normal + other.normal,
                                   self.tex_coord + other.tex_coord,
                                   self.parameter + other.parameter,
                                   self.bezier_uv + other.bezier_uv)

                return res
            else:
                raise Exception('input must be Number')

        def __mul__(self, other):
            if isinstance(other, Number):
                res = ACPoly.Point(self.position * other,
                                   self.normal * other,
                                   self.tex_coord * other,
                                   self.parameter * other,
                                   self.bezier_uv * other)
                return res
            else:
                raise Exception('input must be Number')

    def __init__(self, t, p=None):
        self._triangle = t  # type: ACTriangle
        if p:
            self._points = p
        else:
            self._points = []
            for x in zip(t.positionv4, t.normalv3, t.tex_coord, t.parameter, t.bezier_uv):
                self._points.append(ACPoly.Point(*x))

    def split_x(self, x):
        return self.split(0, x)

    def split_y(self, y):
        return self.split(1, y)

    def split_z(self, z):
        return self.split(2, z)

    UP = 'u'
    DOWN = 'd'

    def split(self, component, value):
        up = []
        down = []
        if self._points[-1].large_than(component, value):
            last = ACPoly.UP
        else:
            last = ACPoly.DOWN

        for i in range(len(self._points)):
            if self._points[i].large_than(component, value):
                if last == ACPoly.UP:
                    up.append(self._points[i])
                else:
                    down_points, up_points = ACPoly.Point.split(self._points[i - 1], self._points[i], component, value)
                    down += down_points
                    up += up_points
                    last = ACPoly.UP
            else:
                if last == ACPoly.UP:
                    up_points, down_points = ACPoly.Point.split(self._points[i - 1], self._points[i], component, value)
                    down += down_points
                    up += up_points
                    last = ACPoly.DOWN
                else:
                    down.append(self._points[i])

        return ACPoly.check_then_new(self._triangle, up), ACPoly.check_then_new(self._triangle, down)

    def to_triangle(self):
        res = []
        c, pre = self._points[:2]
        for p in self._points[2:]:
            ps = [c, pre, p]
            if c == pre == p:
                continue
            t = ACTriangle(self._triangle.id)
            t.positionv4 = np.array([p.position for p in ps], dtype='f4')
            # original normal not need normalize
            t.normalv3 = np.array([p.normal for p in ps], dtype='f4')
            t.tex_coord = np.array([p.tex_coord for p in ps], dtype='f4')
            t.bezier_uv = np.array([p.bezier_uv for p in ps], dtype='f4')
            t.parameter = np.array([p.parameter for p in ps], dtype='f4')
            t.neighbor = self._triangle.neighbor
            t.pn_triangle_p = self._triangle.pn_triangle_p
            t.pn_triangle_n = self._triangle.pn_triangle_n
            t.bezier_id = self._triangle.bezier_id
            res.append(t)
            pre = p
        return res

    @staticmethod
    def check_then_new(triangle, points):
        if points is None or len(points) == 0:
            return None

        # res = [points[0]]
        # for p in points[1:]:
        #     if not p == res[-1]:
        #         res.append(p)
        # if res[0] == res[-1]:
        #     res = res[1:]

        # res = []
        # for i, p in enumerate(points):
        #     if p.is_new:
        #         p.is_new = False
        #         p1 = points[i - 1]
        #         p2 = points[(i + 1) % len(points)]
        #         if (p == p1 and not p1.is_new) or (p == p2 and not p2.is_new):
        #             continue
        #     res.append(p)
        res = points

        if len(res) < 3:
            return None
        else:
            return ACPoly(triangle, res)


class ACTriangle:
    # vec4 pn_position[3];
    # vec4 pn_normal[3];
    # vec4 original_position[3];
    # vec4 original_normal[3];
    # vec4 adjacency_pn_normal_parameter[6];
    # vec4 parameter_in_original2_texcoord2[3];
    # ivec4 adjacency_triangle_index3_original_triangle_index1;
    # vec2 bezier_uv[3];
    # uint bezier_patch_id;
    # float triangle_quality;

    if conf.IS_FAST_MODE:
        DATA_TYPE = [('pn_position', '4f4', 3),
                     ('pn_normal', '4f4', 3),
                     ('original_position', '4f4', 3),
                     ('original_normal', '4f4', 3),
                     ('adjacency_pn_normal_parameter', '4f4', 6),
                     ('parameter_in_original2_texcoord2', '4f4', 3),
                     ('adjacency_triangle_index3_original_triangle_index1', '4i4'),
                     # ('bezier_uv', '2f4', 3),
                     # ('bezier_patch_id', 'u4'),
                     ('triangle_quality_and_padding', '4f4')]
    else:
        DATA_TYPE = [('pn_position', '4f4', 3),
                     ('pn_normal', '4f4', 3),
                     ('original_position', '4f4', 3),
                     ('original_normal', '4f4', 3),
                     ('adjacency_pn_normal_parameter', '4f4', 6),
                     ('parameter_in_original2_texcoord2', '4f4', 3),
                     ('adjacency_triangle_index3_original_triangle_index1', '4i4'),
                     ('bezier_uv', '2f4', 3),
                     ('bezier_patch_id', 'u4'),
                     ('triangle_quality_and_padding', 'f4')]

    def __init__(self, i):
        self._id = i
        self._position = None  # type: np.array
        self._normal = None  # type: np.array
        self._tex_coord = None  # type: np.array
        self._bezier_uv = None  # type: np.array
        self._neighbor = None  # type: list[(ACTriangle, int)]
        self._pn_triangle_p = [None] * 10  # type: list
        self._pn_triangle_n = [None] * 6
        self._parameter = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype='f4')
        self.bezier_id = -1

    def __str__(self):
        return ','.join([str(x.id if x else None) + '-' + str(y) for x, y in self._neighbor])

    def as_element_for_shader(self) -> list:
        original_position = self.positionv4
        pn_position = [self.get_position_in_pn_triangle(x) for x in self._parameter]
        self.positionv4 = np.array(pn_position, dtype='f4')

        # v4
        pn_normal = [self.get_normal_in_pn_triangle(x) for x in self._parameter]

        pn_normal_parameter_adjacent = np.zeros((6, 4), dtype='f4')
        adjacency_triangle_index3_original_triangle_index1 = np.zeros((4,), dtype='i4')
        aux2 = [5, 0, 1, 2, 3, 4]
        occupy_edge_info = [ACTriangle.occupy_edge(p) for p in self.parameter]
        original_edge_info = [SPLIT_PARAMETER_EDGE_INFO_AUX[occupy_edge_info[i] & occupy_edge_info[i - 1]] for i in
                              range(3)]

        for i in range(3):
            current_edge = original_edge_info[i]
            adjacency_triangle_index3_original_triangle_index1[i] = -1
            if current_edge != -1 and self.neighbor[current_edge][0]:
                adjacency_triangle_index3_original_triangle_index1[i] = self.neighbor[current_edge][0].id
            if adjacency_triangle_index3_original_triangle_index1[i] != -1:
                for j in range(2):
                    index = i * 2 + j
                    adjacent_normal_parameter_index = aux2[index]
                    adjacent_parameter = self.transform_parameter(self._parameter[adjacent_normal_parameter_index // 2],
                                                                  current_edge)
                    pn_normal_parameter_adjacent[adjacent_normal_parameter_index] = np.append(adjacent_parameter, 0)

        adjacency_triangle_index3_original_triangle_index1[3] = self.id
        t = [self.positionv3[i - 1] - self.positionv3[i] for i in [1, 2, 0]]
        l = [sqrt(sum([y * y for y in x])) for x in t]
        perimeter = sum(l)
        temp = (-l[0] + l[1] + l[2]) * (l[0] - l[1] + l[2]) * (l[0] + l[1] - l[2])
        if temp <= 0:
            triangle_quality = 0
        else:
            double_area = sqrt(perimeter * temp) / 2
            radius = double_area / perimeter
            triangle_quality = radius / max(l[0], max(l[1], l[2])) * 3.4

        if conf.IS_FAST_MODE:
            data = [pn_position,
                    pn_normal,
                    original_position,
                    self.normalv4,
                    pn_normal_parameter_adjacent,
                    np.hstack((self.parameter[:, :2], self._tex_coord)),
                    adjacency_triangle_index3_original_triangle_index1,
                    # self.bezier_uv,
                    # self.bezier_id,
                    (triangle_quality, 0, 0, 0)]
        else:
            data = [pn_position,
                    pn_normal,
                    original_position,
                    self.normalv4,
                    pn_normal_parameter_adjacent,
                    np.hstack((self.parameter[:, :2], self._tex_coord)),
                    adjacency_triangle_index3_original_triangle_index1,
                    self.bezier_uv,
                    self.bezier_id,
                    triangle_quality]

        return tuple(data)

    @staticmethod
    def occupy_edge(parameter) -> int:
        return sum(map(lambda x: x[1] if parameter[x[0]] < ZERO else 0, enumerate([1, 2, 4])))

    def transform_parameter(self, parameter, edge_index):
        unchange = SPLIT_PARAMETER_CHANGE_AUX[edge_index][self.neighbor[edge_index][1]]
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
        return self._pn_triangle_p, self._pn_triangle_n

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
    #     if all(abs(v) < ZERO):
    #         return n
    #     else:
    #         return normalize(n - 2 * v * np.dot(n, v))

    def gen_normal_control_point(self, start, end):
        p_s = self.positionv3[start]
        p_e = self.positionv3[end]
        n_s = self.normalv3[start]
        n_e = self.normalv3[end]
        n = n_s + n_e
        v = p_e - p_s
        if all(abs(v) < ZERO):
            return normalize(n)
        else:
            return normalize(n - 2 * np.dot(n, v) / np.dot(v, v) * v)

    def get_position_in_pn_triangle(self, parameter: np.array):
        result = np.array([0] * 3, dtype='f4')
        ctrl_point_index = 0
        for i in range(3, -1, -1):
            for j in range(3 - i, -1, -1):
                k = 3 - i - j
                n = 6.0 * pow(parameter[0], i) * pow(parameter[1], j) * pow(parameter[2], k) \
                    / factorial(i) / factorial(j) / factorial(k)
                result += self._pn_triangle_p[ctrl_point_index] * n
                ctrl_point_index += 1
        return np.append(result, 1)

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

    def intersect(self, start_point: np.mat, direction: np.mat):
        position = [x[:3] for x in self._position]
        E1 = np.mat(position[1] - position[0], dtype='f4')[:, :3]
        E2 = np.mat(position[2] - position[0], dtype='f4')[:, :3]
        try:
            i = np.row_stack((-direction[0, :3], E1, E2)).I
        except LinAlgError:
            return None, None
        T = start_point[0, :3] - np.mat(position[0], dtype='f4')
        t, u, v = np.array(np.dot(T, i))[0]
        if all([0 <= x <= 1 for x in [u, v, 1 - u - v]]) and t > 0:
            return t, np.array((start_point[0, :3] + t * direction[0, :3]), dtype='f4').reshape(3, )
        else:
            return None, None

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
    def bezier_uv(self):
        return self._bezier_uv

    @property
    def parameter(self):
        return self._parameter

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

    @bezier_uv.setter
    def bezier_uv(self, value):
        self._bezier_uv = value

    @neighbor.setter
    def neighbor(self, value):
        self._neighbor = value

    @positionv3.setter
    def positionv3(self, value):
        self._position = np.zeros((3, 4), dtype='f4')
        self._position[:, :3] = value

    @normalv3.setter
    def normalv3(self, value):
        self._normal = np.zeros((3, 4), dtype='f4')
        self._normal[:, :3] = value

    @parameter.setter
    def parameter(self, value):
        self._parameter = value

    @property
    def pn_triangle_p(self):
        return self._pn_triangle_p

    @pn_triangle_p.setter
    def pn_triangle_p(self, pn_triangle_p):
        self._pn_triangle_p = pn_triangle_p

    @property
    def pn_triangle_n(self):
        return self._pn_triangle_n

    @pn_triangle_n.setter
    def pn_triangle_n(self, pn_triangle_n):
        self._pn_triangle_n = pn_triangle_n


if __name__ == '__main__':
    t = ACTriangle(0)
    t.positionv3 = np.array([0, 0, 0, 1, 1, 0, 1, 0, 0], dtype='f4').reshape((3, 3))
    tuv = t.intersect(np.mat([-1, -1, 1], dtype='f4'), np.mat([1, 1, 0], dtype='f4'))
    print(tuv)
