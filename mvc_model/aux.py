from itertools import product

import numpy as np

from pre_computer_data.aux_matrix.sample_aux_matrix import get_aux_matrix_offset


class BSplineBody:
    def __init__(self, lx, ly, lz, *argv):
        if len(argv) == 0:
            # 阶数，阶数 = p + 1,当阶数=1时，基函数为常数。是每个knot区间所对应的顶点数。当knot左右重合顶点为阶数时，b-spline始末与控制顶点重合
            self._order_u = 3
            self._order_v = 3
            self._order_w = 3
            # 控制顶点数，knot节点数 = 阶数 + 控制顶点数
            self._control_point_number_u = 5
            self._control_point_number_v = 5
            self._control_point_number_w = 5
        elif len(argv) == 6:
            self._order_u = argv[0]
            self._order_v = argv[1]
            self._order_w = argv[2]
            # 控制顶点数，knot节点数 = 阶数 + 控制顶点数
            self._control_point_number_u = argv[3]
            self._control_point_number_v = argv[4]
            self._control_point_number_w = argv[5]
        else:
            raise Exception('input argv number error')

        self._size = [lx, ly, lz]

        self._ctrlPoints = None  # type: np.array
        self._control_points_backup = None  # type: np.array
        self._is_hit = None  # type: list

        self.init_data()

    def init_data(self):
        self._ctrlPoints = np.zeros((self._control_point_number_u,
                                     self._control_point_number_v,
                                     self._control_point_number_w,
                                     3), dtype=np.float32)  # type: np.array
        aux_x = self.get_control_point_aux_list(self._size[0], self._control_point_number_u, self._order_u)
        aux_y = self.get_control_point_aux_list(self._size[1], self._control_point_number_v, self._order_v)
        aux_z = self.get_control_point_aux_list(self._size[2], self._control_point_number_w, self._order_w)
        for u, x in enumerate(aux_x):
            for v, y in enumerate(aux_y):
                for w, z in enumerate(aux_z):
                    self._ctrlPoints[u, v, w] = [x, y, z]
        self._control_points_backup = self._ctrlPoints.copy()
        self.reset_hit_record()

    def reset_hit_record(self):
        self._is_hit = [
                           False] * self._control_point_number_u * self._control_point_number_v * self._control_point_number_w

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
                u = i // (self._control_point_number_v * self._control_point_number_w)
                v = i % (self._control_point_number_v * self._control_point_number_w) // self._control_point_number_w
                w = i % self._control_point_number_w
                self._ctrlPoints[u, v, w] += xyz

    def get_info(self):
        return np.array(
            [self._order_u, self._order_v, self._order_w,
             self._control_point_number_u, self._control_point_number_v, self._control_point_number_w,
             self._size[0], self._size[1], self._size[2],
             -self._size[0] / 2, -self._size[1] / 2, -self._size[2] / 2], dtype='float32')

    def get_control_point_for_sample(self):
        # uvw三个方向的区间数
        interval_number_u, interval_number_v, interval_number_w = self.get_cage_size()
        result = np.zeros((interval_number_u, interval_number_v, interval_number_w,
                           self._order_u, self._order_v, self._order_w,
                           4), dtype=np.float32)
        for interval_index_u, interval_index_v, interval_index_w in \
                product(range(interval_number_u),
                        range(interval_number_v),
                        range(interval_number_w)):

            left_u_index = interval_index_u + self._order_u - 1
            left_v_index = interval_index_v + self._order_v - 1
            left_w_index = interval_index_w + self._order_w - 1

            mu = get_aux_matrix_offset(self._order_u, self._control_point_number_u, left_u_index)
            mv = get_aux_matrix_offset(self._order_v, self._control_point_number_v, left_v_index)
            mw = get_aux_matrix_offset(self._order_w, self._control_point_number_w, left_w_index)

            control_point_base_u = left_u_index - self._order_u + 1
            control_point_base_v = left_v_index - self._order_v + 1
            control_point_base_w = left_w_index - self._order_w + 1

            intermediate_results_1 = np.zeros((self._order_u, self._order_v, self._order_w, 3))
            for w in range(self._order_w):
                control_points = self._ctrlPoints[control_point_base_u:control_point_base_u + self._order_u,
                                 control_point_base_v:control_point_base_v + self._order_v,
                                 control_point_base_w + w]
                intermediate_results_1[..., w, 0] = mu.dot(control_points[..., 0])
                intermediate_results_1[..., w, 1] = mu.dot(control_points[..., 1])
                intermediate_results_1[..., w, 2] = mu.dot(control_points[..., 2])

            intermediate_results_2 = np.zeros((self._order_u, self._order_v, self._order_w, 3))
            for u in range(self._order_u):
                control_point = intermediate_results_1[u, ...]
                intermediate_results_2[u, ..., 0] = mv.dot(control_point[..., 0])
                intermediate_results_2[u, ..., 1] = mv.dot(control_point[..., 1])
                intermediate_results_2[u, ..., 2] = mv.dot(control_point[..., 2])

            for v in range(self._order_v):
                control_point = intermediate_results_2[:, v, ...]
                result[interval_index_u, interval_index_v, interval_index_w, :, v, :, 0] = \
                    control_point[..., 0].dot(mw.T)
                result[interval_index_u, interval_index_v, interval_index_w, :, v, :, 1] = \
                    control_point[..., 1].dot(mw.T)
                result[interval_index_u, interval_index_v, interval_index_w, :, v, :, 2] = \
                    control_point[..., 2].dot(mw.T)

        return result

    def get_control_point_number(self):
        return self._control_point_number_u * self._control_point_number_v * self._control_point_number_w

    def get_cage_size(self):
        interval_number_u = self._control_point_number_u - self._order_u + 1
        interval_number_v = self._control_point_number_v - self._order_v + 1
        interval_number_w = self._control_point_number_w - self._order_w + 1
        return [interval_number_u, interval_number_v, interval_number_w]

    def change_control_point_number(self, u, v, w):
        self._control_point_number_u = u
        self._control_point_number_v = v
        self._control_point_number_w = w
        self.init_data()

    def move_dffd(self, parameter, displacement):
        displacement = np.asarray(displacement, dtype=np.float32)
        Rs = np.zeros((self._control_point_number_u,
                       self._control_point_number_v,
                       self._control_point_number_w), dtype=np.float32)

        aux = 0
        for i, j, k in product(
                range(self._control_point_number_u),
                range(self._control_point_number_v),
                range(self._control_point_number_w)):
            Rs[i, j, k] = self.R(parameter, i, j, k)
            aux += Rs[i, j, k] ** 2

        for i, j, k in product(
                range(self._control_point_number_u),
                range(self._control_point_number_v),
                range(self._control_point_number_w)):
            k_aux = displacement * Rs[i, j, k] / aux
            self._ctrlPoints[i, j, k] += k_aux

    def R(self, parameter, i, j, k):
        return self.B(self.get_knots(self._size[0], self._order_u, self._control_point_number_u), self._order_u, i,
                      parameter[0]) \
               * self.B(self.get_knots(self._size[1], self._order_v, self._control_point_number_v), self._order_v, j,
                        parameter[1]) \
               * self.B(self.get_knots(self._size[2], self._order_w, self._control_point_number_w), self._order_w, k,
                        parameter[2])

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
