from itertools import product

import numpy as np
from functools import reduce

from pre_computer_data.aux_matrix.sample_aux_matrix import get_aux_matrix_offset


class BSplineBody:
    def __init__(self, lx, ly, lz, *argv):
        if len(argv) == 0:
            # 阶数，阶数 = p + 1,当阶数=1时，基函数为常数。是每个knot区间所对应的顶点数。当knot左右重合顶点为阶数时，b-spline始末与控制顶点重合
            self._order = [3, 3, 3]  # type: list
            # 控制顶点数，knot节点数 = 阶数 + 控制顶点数
            self._control_point_number = [5, 5, 5]  # type: list
        elif len(argv) == 6:
            self._order = argv[:3]  # type: list
            # 控制顶点数，knot节点数 = 阶数 + 控制顶点数
            self._control_point_number = argv[3:]  # type: list
        else:
            raise Exception('input argv number error')

        self._ctrlPoints = None  # type: np.array
        self._control_points_backup = None  # type: np.array
        self._is_hit = None  # type: list
        self._knots = None  # type: list
        self._step = None  # type: list

        self._size = [lx, ly, lz]

        self.init_data()

    def init_data(self):
        # self._ctrlPoints = np.zeros((self._control_point_number_u,
        #                              self._control_point_number_v,
        #                              self._control_point_number_w,
        #                              3), dtype=np.float32)  # type: np.array
        aux = [self.get_control_point_aux_list(size, cpn, o) for size, cpn, o in
               zip(self._size, self._control_point_number, self._order)]
        # for u, x in enumerate(aux[0]):
        #     for v, y in enumerate(aux[1]):
        #         for w, z in enumerate(aux[2]):
        #             self._ctrlPoints[u, v, w] = [x, y, z]
        self._ctrlPoints = np.array(list(product(*aux)), dtype='f4')
        self._ctrlPoints.shape = (*self._control_point_number, 3)
        self._control_points_backup = self._ctrlPoints.copy()
        self.reset_hit_record()
        self._knots = [self.get_knots(size, order, cpn) for size, order, cpn in
                       zip(self._size, self._order, self._control_point_number)]
        self._step = [x / y for x, y in zip(self._size, self.get_cage_size())]

    def reset_hit_record(self):
        self._is_hit = [False] * self.get_control_point_number()

    @property
    def is_hit(self):
        return np.array(self._is_hit, dtype=np.float32)

    @property
    def control_points(self):
        return np.array(self._ctrlPoints, dtype=np.float32)

    @staticmethod
    def get_control_point_aux_list(length, control_point_number, order):
        if control_point_number == order:
            step = length / (control_point_number - 1)
            return np.arange(-length / 2, length / 2 + step / 2, step)
        elif control_point_number > order:
            if control_point_number % 2 == 1:
                # k = length / ((1 + (control_point_number - 1) / 2) * (control_point_number - 1) / 2)
                result = [0]
                for i in range(1, int(control_point_number / 2) + 1):
                    step = min(i, order - 1)
                    result.append(result[-1] + step)

                for i in range(int(control_point_number / 2), 0, -1):
                    step = min(i, order - 1)
                    result.append(result[-1] + step)
            else:
                # k = length / ((1 + (control_point_number - 2) / 2) * (
                #     control_point_number - 2) / 2 + control_point_number / 2)
                result = [0]
                for i in range(1, int(control_point_number / 2) + 1):
                    step = min(i, order - 1)
                    result.append(result[-1] + step)
                for i in range(int(control_point_number / 2) - 1, 0, -1):
                    step = min(i, order - 1)
                    result.append(result[-1] + step)
            # print(result)
            return [(x / result[-1] - 0.5) * length for x in result]
        else:
            raise Exception('control point number can not less than order')

    def move(self, xyz):
        for i, is_hit in enumerate(self._is_hit):
            if is_hit:
                u = i // (self._control_point_number[1] * self._control_point_number[2])
                v = i % (self._control_point_number[1] * self._control_point_number[2]) // self._control_point_number[2]
                w = i % self._control_point_number[2]
                self._ctrlPoints[u, v, w] += xyz

    @property
    def min_parameter(self):
        return [-x / 2 for x in self._size]

    def get_info(self):
        return np.array(
            [*self._order,
             *self._control_point_number,
             *self._size,
             *self.min_parameter], dtype='float32')

    def get_control_point_for_sample(self):
        # uvw三个方向的区间数
        interval_number = self.get_cage_size()
        result = np.zeros((*interval_number,
                           *self._order,
                           4), dtype=np.float32)
        for interval_index in product(*[range(x) for x in interval_number]):

            left_index = [x + y - 1 for x, y in zip(interval_index, self._order)]

            m = [get_aux_matrix_offset(order, cpn, li) for order, cpn, li in
                 zip(self._order, self._control_point_number, left_index)]

            control_point_base = [x - y + 1 for x, y in zip(left_index, self._order)]

            intermediate_results_1 = np.zeros((*self._order, 3))
            for w in range(self._order[2]):
                control_points = self._ctrlPoints[control_point_base[0]:control_point_base[0] + self._order[0],
                                 control_point_base[1]:control_point_base[1] + self._order[1],
                                 control_point_base[2] + w]
                for i in range(3):
                    intermediate_results_1[..., w, i] = m[0].dot(control_points[..., i])

            intermediate_results_2 = np.zeros((*self._order, 3))
            for u in range(self._order[0]):
                control_point = intermediate_results_1[u, ...]
                for i in range(3):
                    intermediate_results_2[u, ..., i] = m[1].dot(control_point[..., i])

            for v in range(self._order[1]):
                control_point = intermediate_results_2[:, v, ...]
                for i in range(3):
                    result[interval_index[0], interval_index[1], interval_index[2], :, v, :, i] = \
                        control_point[..., i].dot(m[2].T)

        return result

    def get_control_point_number(self):
        return reduce(lambda p, x: p * x, self._control_point_number, 1)

    def get_cage_size(self):
        return [x - y + 1 for x, y in zip(self._control_point_number, self._order)]

    def change_control_point_number(self, u, v, w):
        self._control_point_number = [u, v, w]
        self.init_data()

    def move_dffd(self, parameter, displacement):
        displacement = np.asarray(displacement, dtype=np.float32)
        Rs = np.zeros((*self._control_point_number,), dtype=np.float32)
        aux = 0
        for ijk in product(*[range(x) for x in self._control_point_number]):
            Rs[ijk] = self.R(parameter, ijk)
            aux += Rs[ijk] ** 2

        for i, j, k in product(*[range(x) for x in self._control_point_number]):
            k_aux = displacement * Rs[i, j, k] / aux
            self._ctrlPoints[i, j, k] += k_aux

    def R(self, parameter, ijk):
        return reduce(lambda p, x: p * x, [self.B(knots, order, i, para) for knots, order, i, para in
                                           zip(self._knots, self._order, ijk, parameter)], 1)

    def B(self, knots, order, i, t):
        temp = [0] * order
        # k = 1
        for index in range(i, i + order):
            if knots[index] <= t < knots[index + 1]:
                temp[index - i] = 1
            elif t == knots[index + 1] == 1:
                temp[index - i] = 1
            else:
                temp[index - i] = 0
        # k = [2, k]
        for k in range(2, order + 1):
            for index in range(i, i + order - k + 1):
                if knots[index + k - 1] - knots[index] == 0:
                    first = 0
                else:
                    first = (t - knots[index]) / (knots[index + k - 1] - knots[index]) * temp[index - i]

                if knots[index + k] - knots[index + 1] == 0:
                    second = 0
                else:
                    second = (knots[index + k] - t) / (knots[index + k] - knots[index + 1]) * temp[index - i + 1]
                temp[index - i] = first + second
        return temp[0]

    def get_knots(self, length, order, control_point_number):
        res = [- length / 2] * order
        internal_number = control_point_number - order + 1
        step = length / internal_number
        for i in range(1, internal_number):
            res.append(res[-1] + step)
        res += [length / 2] * order
        return res

    def hit_point(self, select_name):
        self._is_hit[select_name] = True

    def get_cage_t_and_left_knot_index(self, parameter):
        parameter = [x - y for x, y in zip(parameter, self.min_parameter)]
        temp = [x / y for x, y in zip(parameter, self._step)]
        left_knot_index = [(int(x) - 1 if x >= y else int(x)) for x, y in zip(temp, self.get_cage_size())]
        cage_t = [x - y for x, y in zip(temp, left_knot_index)]
        return cage_t + [0], [x + y - 1 for x, y in zip(left_knot_index, self._order)] + [0]


def aux_multiply(value, v, result):
    result[0] += value * v[0]
    result[1] += value * v[1]
    result[2] += value * v[2]


from matplotlib.pylab import plot, show

if __name__ == '__main__':
    knots = [0, 0, 0, 0, 1 / 3, 2 / 3, 1, 1, 1, 1]
    body = BSplineBody(2, 2, 2)
    x = np.linspace(0, 1, 100)
    y1 = [body.B(knots, 4, 0, i) for i in x]
    y2 = [body.B(knots, 4, 1, i) for i in x]
    y3 = [body.B(knots, 4, 2, i) for i in x]
    y4 = [body.B(knots, 4, 3, i) for i in x]
    y5 = [body.B(knots, 4, 4, i) for i in x]
    y6 = [body.B(knots, 4, 5, i) for i in x]
    plot(x, y1)
    plot(x, y2)
    plot(x, y3)
    plot(x, y4)
    plot(x, y5)
    plot(x, y6)
    show()
