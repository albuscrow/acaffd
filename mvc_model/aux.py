from itertools import product

import numpy as np

from pre_computer_data.aux_matrix.sample_aux_matrix import get_aux_matrix_offset


class BSplineBody:
    def __init__(self, lx, ly, lz, *argv):
        if len(argv) == 0:
            # 阶数，阶数 = p + 1,当阶数=1时，基函数为常数。是每个knot区间所对应的顶点数。当knot左右重合顶点为阶数时，b-spline始末与控制顶点重合
            self.order_u = 3
            self.order_v = 3
            self.order_w = 3
            # 控制顶点数，knot节点数 = 阶数 + 控制顶点数
            self.control_point_number_u = 5
            self.control_point_number_v = 5
            self.control_point_number_w = 5
        elif len(argv) == 6:
            self.order_u = argv[0]
            self.order_v = argv[1]
            self.order_w = argv[2]
            # 控制顶点数，knot节点数 = 阶数 + 控制顶点数
            self.control_point_number_u = argv[3]
            self.control_point_number_v = argv[4]
            self.control_point_number_w = argv[5]
        else:
            raise Exception('input argv number error')

        self.lu = lx
        self.lv = ly
        self.lw = lz

        self.ctrlPoints = None
        self.control_points_backup = None
        self.is_hit = None

        self.init_data()

    def init_data(self):
        self.ctrlPoints = np.zeros((self.control_point_number_u,
                                    self.control_point_number_v,
                                    self.control_point_number_w,
                                    3), dtype=np.float32)
        aux_x = self.get_control_point_aux_list(self.lu, self.control_point_number_u, self.order_u)
        aux_y = self.get_control_point_aux_list(self.lv, self.control_point_number_v, self.order_v)
        aux_z = self.get_control_point_aux_list(self.lw, self.control_point_number_w, self.order_w)
        for u, x in enumerate(aux_x):
            for v, y in enumerate(aux_y):
                for w, z in enumerate(aux_z):
                    self.ctrlPoints[u, v, w] = [x, y, z]
        self.control_points_backup = self.ctrlPoints.copy()
        self.reset_is_hit()

    def reset_is_hit(self):
        self.is_hit = [False] * self.control_point_number_u * self.control_point_number_v * self.control_point_number_w

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

    def move(self, x, y, z):
        # self.ctrlPoints = self.control_points_backup
        # self.move_dffd([1, 0.5, 0.5], [0.5, 0.5, 0.5])
        for i, is_hit in enumerate(self.is_hit):
            if is_hit:
                u = i // (self.control_point_number_v * self.control_point_number_w)
                v = i % (self.control_point_number_v * self.control_point_number_w) // self.control_point_number_w
                w = i % self.control_point_number_w
                self.ctrlPoints[u, v, w] += [d / 10 for d in [x, y, z]]

    def get_info(self):
        return np.array(
            [self.order_u, self.order_v, self.order_w,
             self.control_point_number_u, self.control_point_number_v, self.control_point_number_w,
             self.lu, self.lv, self.lw,
             -self.lu / 2, -self.lv / 2, -self.lw / 2], dtype='float32')

    def get_control_point_for_sample(self):
        # uvw三个方向的区间数
        interval_number_u, interval_number_v, interval_number_w = self.get_cage_size()
        result = np.zeros((interval_number_u, interval_number_v, interval_number_w,
                           self.order_u, self.order_v, self.order_w,
                           4), dtype=np.float32)
        for interval_index_u, interval_index_v, interval_index_w in \
                product(range(interval_number_u),
                        range(interval_number_v),
                        range(interval_number_w)):

            left_u_index = interval_index_u + self.order_u - 1
            left_v_index = interval_index_v + self.order_v - 1
            left_w_index = interval_index_w + self.order_w - 1

            mu = get_aux_matrix_offset(self.order_u, self.control_point_number_u, left_u_index)
            mv = get_aux_matrix_offset(self.order_v, self.control_point_number_v, left_v_index)
            mw = get_aux_matrix_offset(self.order_w, self.control_point_number_w, left_w_index)

            control_point_base_u = left_u_index - self.order_u + 1
            control_point_base_v = left_v_index - self.order_v + 1
            control_point_base_w = left_w_index - self.order_w + 1

            intermediate_results_1 = np.zeros((self.order_u, self.order_v, self.order_w, 3))
            for w in range(self.order_w):
                control_points = self.ctrlPoints[control_point_base_u:control_point_base_u + self.order_u,
                                 control_point_base_v:control_point_base_v + self.order_v,
                                 control_point_base_w + w]
                intermediate_results_1[..., w, 0] = mu.dot(control_points[..., 0])
                intermediate_results_1[..., w, 1] = mu.dot(control_points[..., 1])
                intermediate_results_1[..., w, 2] = mu.dot(control_points[..., 2])

            intermediate_results_2 = np.zeros((self.order_u, self.order_v, self.order_w, 3))
            for u in range(self.order_u):
                control_point = intermediate_results_1[u, ...]
                intermediate_results_2[u, ..., 0] = mv.dot(control_point[..., 0])
                intermediate_results_2[u, ..., 1] = mv.dot(control_point[..., 1])
                intermediate_results_2[u, ..., 2] = mv.dot(control_point[..., 2])

            for v in range(self.order_v):
                control_point = intermediate_results_2[:, v, ...]
                result[interval_index_u, interval_index_v, interval_index_w, :, v, :, 0] = \
                    control_point[..., 0].dot(mw.T)
                result[interval_index_u, interval_index_v, interval_index_w, :, v, :, 1] = \
                    control_point[..., 1].dot(mw.T)
                result[interval_index_u, interval_index_v, interval_index_w, :, v, :, 2] = \
                    control_point[..., 2].dot(mw.T)

        return result

    def get_control_point_number(self):
        return self.control_point_number_u * self.control_point_number_v * self.control_point_number_w

    def get_cage_size(self):
        interval_number_u = self.control_point_number_u - self.order_u + 1
        interval_number_v = self.control_point_number_v - self.order_v + 1
        interval_number_w = self.control_point_number_w - self.order_w + 1
        return [interval_number_u, interval_number_v, interval_number_w]

    def change_control_point(self, u, v, w):
        self.control_point_number_u = u
        self.control_point_number_v = v
        self.control_point_number_w = w
        self.init_data()

    def move_dffd(self, parameter, displacement):
        displacement = np.asarray(displacement, dtype=np.float32)
        Rs = np.zeros((self.control_point_number_u,
                       self.control_point_number_v,
                       self.control_point_number_w), dtype=np.float32)

        aux = 0
        for i, j, k in product(
                range(self.control_point_number_u),
                range(self.control_point_number_v),
                range(self.control_point_number_w)):
            Rs[i, j, k] = self.R(parameter, i, j, k)
            aux += Rs[i, j, k] ** 2

        for i, j, k in product(
                range(self.control_point_number_u),
                range(self.control_point_number_v),
                range(self.control_point_number_w)):
            k_aux = displacement * Rs[i, j, k] / aux
            self.ctrlPoints[i, j, k] += k_aux

    def R(self, parameter, i, j, k):
        return self.B(self.get_knots(self.lu, self.order_u, self.control_point_number_u), self.order_u, i, parameter[0]) \
               * self.B(self.get_knots(self.lv, self.order_v, self.control_point_number_v), self.order_v, j, parameter[1]) \
               * self.B(self.get_knots(self.lw, self.order_w, self.control_point_number_w), self.order_w, k, parameter[2])

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

def aux_multiply(value, v, result):
    result[0] += value * v[0]
    result[1] += value * v[1]
    result[2] += value * v[2]


from matplotlib.pylab import plot, show

if __name__ == '__main__':
    # print(BSplineBody.get_control_point_aux_list(1, 5, 3))
    # print(BSplineBody.get_control_point_aux_list(1, 6, 2))
    # print(BSplineBody.get_control_point_aux_list(1, 6, 6))
    # print(BSplineBody.get_control_point_aux_list(1, 6, 7))
    knots = [0, 0, 0, 0, 1 / 3, 2 / 3, 1, 1, 1, 1]
    body = BSplineBody(2, 2, 2)
    # body.move_dffd([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    # print(body.get_knots(1, 3, 5))
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
    # body.B(knots, 3, 2, 1 / 3)
    # print(body.B(knots, 3, 1, 0.5), body.B(knots, 3, 3, 0.5))
    # print(body.B(knots, 3, 1, 1 / 3), body.B(knots, 3, 2, 1 / 3))
    # print(body.B(knots, 3, 2, 2 / 3), body.B(knots, 3, 3, 2 / 3))
