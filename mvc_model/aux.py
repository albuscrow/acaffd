from itertools import product

import numpy as np
from functools import reduce

from Constant import ZERO
from pre_computer_data.aux_matrix.sample_aux_matrix import get_aux_matrix_offset


class BSplineBody:
    def __init__(self, lx, ly, lz, *argv):
        if len(argv) == 0:
            # 阶数，阶数 = p + 1,当阶数=1时，基函数为常数。是每个knot区间所对应的顶点数。当knot左右重合顶点为阶数时，b-spline始末与控制顶点重合
            self._order = [4, 4, 4]  # type: list
            # self._order = [3, 3, 3]  # type: list
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

    @property
    def step(self):
        return [l / s for l, s in zip(self._size, self.get_cage_size())]

    def init_data(self):
        aux = [self.get_control_point_aux_list(size, cpn, o) for size, cpn, o in
               zip(self._size, self._control_point_number, self._order)]
        self._ctrlPoints = np.array(list(product(*aux)), dtype='f4')
        self._ctrlPoints.shape = (*self._control_point_number, 3)
        self._control_points_backup = self._ctrlPoints.copy()
        self.reset_hit_record()
        self._step = [x / y for x, y in zip(self._size, self.get_cage_size())]
        self._knots = [self.get_knots(size, order, internal_number) for size, order, internal_number in
                       zip(self._size, self._order, self.get_cage_size())]

    def reset_hit_record(self):
        self._is_hit = [False] * self.get_control_point_number()

    @property
    def is_hit(self):
        return np.array(self._is_hit, dtype=np.float32)

    @property
    def control_points(self):
        control_points = self._ctrlPoints.reshape((self.get_control_point_number(), 3))
        hit = np.array(self._is_hit, dtype='f4').reshape((self.get_control_point_number(), 1))
        return np.hstack((control_points, hit))

    @property
    def normal_control_points(self):
        return self._ctrlPoints

    @staticmethod
    def get_control_point_aux_list(length, control_point_number, order):
        if control_point_number == order:
            step = length / (control_point_number - 1)
            return np.arange(-length / 2, length / 2 + step / 2, step)
        elif control_point_number > order:
            result = [0]
            for i in range(1, int(control_point_number / 2) + 1):
                step = min(i, order - 1)
                result.append(result[-1] + step)
            for i in range(int(control_point_number / 2) - (control_point_number + 1) % 2, 0, -1):
                step = min(i, order - 1)
                result.append(result[-1] + step)
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
        self._control_points_backup = self._ctrlPoints.copy()

    def rotate(self, m):
        for i, is_hit in enumerate(self._is_hit):
            if is_hit:
                u = i // (self._control_point_number[1] * self._control_point_number[2])
                v = i % (self._control_point_number[1] * self._control_point_number[2]) // self._control_point_number[2]
                w = i % self._control_point_number[2]
                self._ctrlPoints[u, v, w] = np.dot(self._ctrlPoints[u, v, w], m[:3, :3])
        self._control_points_backup = self._ctrlPoints.copy()

    @property
    def min_parameter(self):
        return [-x / 2 for x in self._size]

    def get_info(self):
        return np.array(
            [*self._order, 0,
             *self._control_point_number, 0,
             *self._size, 0], dtype='float32')

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
            intermediate_results_1 = np.zeros((*self._order, 3))
            for w in range(self._order[2]):
                control_points = self._ctrlPoints[interval_index[0]:interval_index[0] + self._order[0],
                                 interval_index[1]:interval_index[1] + self._order[1],
                                 interval_index[2] + w]
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
        parameter = [min(max(x, -l / 2), l / 2) for x, l in zip(parameter, self._size)]
        self._ctrlPoints = self._control_points_backup.copy()
        displacement = np.asarray(displacement, dtype=np.float32)
        Rs = np.zeros((*self._control_point_number,), dtype=np.float32)
        aux = 0
        for ijk in product(*[range(x) for x in self._control_point_number]):
            Rs[ijk] = self.R(parameter, ijk)
            aux += Rs[ijk] ** 2
        if aux != 0:
            for i, j, k in product(*[range(x) for x in self._control_point_number]):
                k_aux = displacement * Rs[i, j, k] / aux
                self._ctrlPoints[i, j, k] += k_aux

    def R(self, parameter, ijk):
        return reduce(lambda p, x: p * x, [self.B(knots, order, i, para) for knots, order, i, para in
                                           zip(self._knots, self._order, ijk, parameter)], 1)

    @staticmethod
    def B(knots, order, i, t):
        temp = [0] * order
        # k = 1
        for index in range(i, i + order):
            if knots[index] <= t < knots[index + 1]:
                temp[index - i] = 1
            elif t == knots[index + 1] == knots[-1]:
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

    @staticmethod
    def get_knots(length, order, internal_number):
        res = [- length / 2] * order
        step = length / internal_number
        for i in range(1, internal_number):
            res.append(res[-1] + step)
        res += [length / 2] * order
        return res

    def get_split_line(self):
        return [list(np.arange(step - length / 2, length / 2 - ZERO, step)) for step, length in
                zip(self._step, self._size)]

    def hit_point(self, select_name):
        self._is_hit[select_name] = True

    def get_cage_t_and_left_knot_index(self, parameter):
        parameter = [x - y for x, y in zip(parameter, self.min_parameter)]
        temp = [x / y for x, y in zip(parameter, self._step)]
        left_knot_index = [(int(x) - 1 if x >= y else int(x)) for x, y in zip(temp, self.get_cage_size())]
        cage_t = [x - y for x, y in zip(temp, left_knot_index)]
        return cage_t + [0], [x + y - 1 for x, y in zip(left_knot_index, self._order)] + [0]

    def save_control_point_position(self):
        self._control_points_backup = self._ctrlPoints.copy()

    def change_control_points(self, control_points):
        self._ctrlPoints = control_points
        self._control_points_backup = self._ctrlPoints.copy()

    @property
    def control_point_number(self):
        return self._control_point_number


def aux_multiply(value, v, result):
    result[0] += value * v[0]
    result[1] += value * v[1]
    result[2] += value * v[2]


from matplotlib.pylab import plot, show

if __name__ == '__main__':
    # knots = [0, 0, 0, 0, 1 / 3, 2 / 3, 1, 1, 1, 1]
    # body = BSplineBody(2, 2, 2)
    # x = np.linspace(-0.4481132075471698, 0.4481132075471698, 100)
    # knots = [-0.4481132075471698, -0.4481132075471698, -0.4481132075471698, -0.14937106918238996, 0.1493710691823899,
    #          0.4481132075471698, 0.4481132075471698, 0.4481132075471698]
    # y1 = [body.B(knots, 3, 0, i) for i in x]
    # y2 = [body.B(knots, 3, 1, i) for i in x]
    # y3 = [body.B(knots, 3, 2, i) for i in x]
    # y4 = [body.B(knots, 3, 3, i) for i in x]
    # y5 = [body.B(knots, 3, 4, i) for i in x]
    # # y6 = [body.B(knots, 3, 5, i) for i in x]
    # plot(x, y1)
    # plot(x, y2)
    # plot(x, y3)
    # plot(x, y4)
    # plot(x, y5)
    # # plot(x, y6)
    # show()
    # knots = [-0.4481132075471698, -0.4481132075471698, -0.4481132075471698, -0.14937106918238996, 0.1493710691823899,
    #          0.4481132075471698, 0.4481132075471698, 0.4481132075471698]
    # order = 3
    # i = 4
    # t = -0.0521475225687
    x = [0.05, 1.04999995, 2.04999995, 3.04999971, 4.04999971, 5.04999971]
    y = [0.0006791732583630148, 5.5609607572219544e-06, 5.560960757221953e-06, 5.560960757221926e-06,
         5.560960757221922e-06]

    x = [0.05, 0.1, 0.15000001, 0.2, 0.25, 0.30000001,
         0.35000002, 0.40000001, 0.45000002, 0.5, 0.55000001, 0.60000002,
         0.65000004, 0.70000005, 0.75, 0.80000001, 0.85000002, 0.90000004,
         0.95000005, 1., 1.04999995, 1.10000002, 1.14999998, 1.19999993,
         1.25, 1.29999995, 1.35000002, 1.39999998, 1.44999993, 1.5,
         1.54999995, 1.60000002, 1.64999998, 1.69999993, 1.75, 1.79999995,
         1.85000002, 1.89999998, 1.94999993, 2., 2.04999995, 2.0999999,
         2.1500001, 2.20000005, 2.25, 2.29999995, 2.3499999, 2.4000001,
         2.45000005, 2.5, 2.54999995, 2.5999999, 2.6500001, 2.70000005,
         2.75, 2.79999995, 2.8499999, 2.9000001, 2.95000005, 3.,
         3.04999995, 3.0999999, 3.1500001, 3.20000005, 3.25, 3.29999995,
         3.3499999, 3.4000001, 3.45000005, 3.5, 3.54999995, 3.5999999,
         3.6500001, 3.70000005, 3.75, 3.79999995, 3.8499999, 3.9000001,
         3.95000005, 4., 4.05000019, 4.10000038, 4.1500001, 4.20000029,
         4.25000048, 4.30000019, 4.35000038, 4.4000001, 4.45000029, 4.50000048,
         4.55000019, 4.60000038, 4.6500001, 4.70000029, 4.75000048, 4.80000019,
         4.85000038, 4.9000001, 4.95000029, 5.00000048, 5.05000019, 5.10000038,
         5.1500001, 5.20000029, 5.25000048, 5.30000019, 5.35000038, 5.4000001,
         5.45000029, 5.50000048, 5.55000019, 5.60000038, 5.6500001, 5.70000029,
         5.75000048, 5.80000019, 5.85000038, 5.9000001, 5.95000029]
    y = [0.0006791732583630173, 0.0012720886366343945, 0.0015403463432766252, 0.0016654880009915583,
         0.001338302856298494, 0.0013201204696562667, 0.00019462347912300348, 0.00019462347912300356,
         5.5609607572219265e-06, 5.5609607572219544e-06, 5.560960757221912e-06, 5.560960757221919e-06,
         5.560960757221893e-06, 5.560960757221951e-06, 5.560960757221937e-06, 5.560960757221952e-06,
         5.560960757221898e-06, 5.5609607572219375e-06, 5.560960757221957e-06, 5.560960757221952e-06,
         5.56096075722194e-06, 5.5609607572219544e-06, 5.5609607572219544e-06, 5.5609607572219485e-06,
         5.560960757221903e-06, 5.5609607572219655e-06, 5.560960757221956e-06, 5.560960757221958e-06,
         5.560960757221979e-06, 5.560960757221935e-06, 5.560960757221925e-06, 5.560960757221952e-06,
         5.56096075722191e-06, 5.560960757221969e-06, 5.560960757221933e-06, 5.560960757221923e-06,
         5.560960757221972e-06, 5.5609607572219926e-06, 5.56096075722191e-06, 5.560960757221933e-06,
         5.560960757221922e-06, 5.56096075722193e-06, 5.560960757221951e-06, 5.5609607572219765e-06,
         5.560960757221933e-06, 5.560960757221953e-06, 5.560960757221938e-06, 5.560960757221939e-06,
         5.56096075722197e-06, 5.560960757221961e-06, 5.5609607572219375e-06, 5.560960757221951e-06,
         5.560960757221907e-06, 5.560960757221949e-06, 5.56096075722192e-06, 5.560960757221976e-06,
         5.5609607572219655e-06, 5.560960757221981e-06, 5.560960757221964e-06, 5.560960757221962e-06,
         5.560960757221939e-06, 5.560960757221916e-06, 5.56096075722191e-06, 5.560960757221961e-06,
         5.560960757221901e-06, 5.560960757221959e-06, 5.5609607572219595e-06, 5.56096075722195e-06,
         5.5609607572219e-06, 5.5609607572219655e-06, 5.5609607572219434e-06, 5.560960757221949e-06,
         5.5609607572219316e-06, 5.560960757221953e-06, 5.56096075722195e-06, 5.560960757221961e-06,
         5.560960757221979e-06, 5.560960757221939e-06, 5.56096075722195e-06, 5.560960757221958e-06,
         5.560960757221936e-06, 5.560960757221937e-06, 5.5609607572219265e-06, 5.560960757221946e-06,
         5.560960757221939e-06, 5.560960757221978e-06, 5.560960757221961e-06, 5.560960757221892e-06,
         5.5609607572219265e-06, 5.560960757221932e-06, 5.560960757221913e-06, 5.560960757221959e-06,
         5.560960757221963e-06, 5.5609607572219544e-06, 5.560960757221939e-06, 5.560960757221974e-06,
         5.5609607572218935e-06, 5.5609607572219765e-06, 5.560960757221953e-06, 5.560960757221925e-06,
         5.5609607572218714e-06, 5.560960757221943e-06, 5.560960757221968e-06, 5.560960757221904e-06,
         5.560960757221922e-06, 5.560960757221978e-06, 5.560960757221931e-06, 5.56096075722195e-06,
         5.560960757221904e-06, 5.560960757221969e-06, 5.560960757221891e-06, 5.5609607572218935e-06,
         5.560960757221911e-06, 5.560960757221963e-06, 5.560960757221914e-06, 5.560960757221943e-06,
         5.560960757221983e-06, 5.560960757221947e-06, 5.560960757221932e-06]

    x = [0.05, 0.1, 0.15000001, 0.2, 0.25, 0.30000001,
         0.35000002, 0.40000001, 0.45000002, 0.5, 0.55000001, 0.60000002,
         0.65000004, 0.70000005, 0.75, 0.80000001, 0.85000002, 0.90000004,
         0.95000005, 1., 1.04999995, 1.10000002, 1.14999998, 1.19999993,
         1.25, 1.29999995, 1.35000002, 1.39999998, 1.44999993, 1.5,
         1.54999995, 1.60000002, 1.64999998, 1.69999993, 1.75, 1.79999995,
         1.85000002, 1.89999998, 1.94999993, 2., 2.04999995, 2.0999999,
         2.1500001, 2.20000005, 2.25, 2.29999995, 2.3499999, 2.4000001,
         2.45000005, 2.5, 2.54999995, 2.5999999, 2.6500001, 2.70000005,
         2.75, 2.79999995, 2.8499999, 2.9000001, 2.95000005, 3.,
         3.04999995, 3.0999999, 3.1500001, 3.20000005, 3.25, 3.29999995,
         3.3499999, 3.4000001, 3.45000005, 3.5, 3.54999995, 3.5999999,
         3.6500001, 3.70000005, 3.75, 3.79999995, 3.8499999, 3.9000001,
         3.95000005, 4., 4.05000019, 4.10000038, 4.1500001, 4.20000029,
         4.25000048, 4.30000019, 4.35000038, 4.4000001, 4.45000029, 4.50000048,
         4.55000019, 4.60000038, 4.6500001, 4.70000029, 4.75000048, 4.80000019,
         4.85000038, 4.9000001, 4.95000029, 5.00000048, 5.05000019, 5.10000038,
         5.1500001, 5.20000029, 5.25000048, 5.30000019, 5.35000038, 5.4000001,
         5.45000029, 5.50000048, 5.55000019, 5.60000038, 5.6500001, 5.70000029,
         5.75000048, 5.80000019, 5.85000038, 5.9000001, 5.95000029]
    y = [0.0002909580234339167, 0.001084186353095951, 0.0012120814342542056, 0.0024920564506944287,
         0.002785379724042397, 0.004201688712200758, 0.004497417958025158, 0.00501347681221027, 0.006163919279154582,
         0.006506013351713678, 0.006988150077892916, 0.008096267916826628, 0.00823933549668271, 0.0084511200765441,
         0.008403012350460226, 0.01022768173478371, 0.01073003174076603, 0.010916289840390713, 0.010916289840390713,
         0.011465643123696757, 0.013636856943705594, 0.0158728153520681, 0.015872815352068054, 0.01587281535206808,
         0.015872815352068095, 0.01587281535206807, 0.015872815352068054, 0.015872815352068092, 0.015872815352068068,
         0.01587281535206807, 0.015872815352068033, 0.015872815352068068, 0.0158728153520681, 0.015872815352068102,
         0.015872815352068092, 0.015872815352068064, 0.01587281535206807, 0.0158728153520681, 0.01587281535206807,
         0.020160314392105496, 0.02072004171803773, 0.020720041718037745, 0.020720041718037745, 0.02023218919188061,
         0.02023218919188067, 0.02023218919188071, 0.020232189191880714, 0.0202321891918807, 0.02023218919188069,
         0.02023218919188069, 0.02023218919188071, 0.020232189191880683, 0.02023218919188069, 0.02023218919188069,
         0.020232189191880703, 0.020232189191880714, 0.02023218919188067, 0.02023218919188065, 0.020232189191880627,
         0.020232189191880634, 0.020232189191880634, 0.020232189191880634, 0.02023218919188067, 0.02023218919188061,
         0.02023218919188067, 0.020232189191880634, 0.020232189191880676, 0.020232189191880714, 0.020232189191880696,
         0.020232189191880755, 0.020232189191880696, 0.020232189191880745, 0.02023218919188067, 0.020232189191880634,
         0.02023218919188071, 0.02023218919188067, 0.020232189191880703, 0.020232189191880686, 0.020232189191880627,
         0.02023218919188067, 0.02023218919188058, 0.020232189191880683, 0.02023218919188069, 0.020232189191880724,
         0.02023218919188071, 0.020232189191880707, 0.02023218919188071, 0.02023218919188061, 0.02023218919188065,
         0.0202321891918807, 0.02023218919188069, 0.02023218919188061, 0.02023218919188067, 0.020232189191880637,
         0.02023218919188061, 0.0202321891918807, 0.02023218919188066, 0.02023218919188075, 0.02023218919188069,
         0.020232189191880634, 0.020232189191880634, 0.020232189191880686, 0.020232189191880655, 0.020232189191880724,
         0.020232189191880696, 0.020232189191880745, 0.020232189191880683, 0.0202321891918807, 0.02023218919188065,
         0.02023218919188061, 0.02023218919188069, 0.02023218919188071, 0.0202321891918807, 0.02023218919188069,
         0.02023218919188071, 0.020232189191880707, 0.0202321891918807, 0.0202321891918807, 0.020232189191880724]

    plot(x[:len(y)], y)
    show()
