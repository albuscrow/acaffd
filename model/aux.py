import numpy as np
from itertools import product
from aux_matrix.sample_aux_matrix import get_aux_matrix_offset, sample_aux_matrix


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
        self.ctrlPoints = np.zeros((self.control_point_number_u,
                                    self.control_point_number_v,
                                    self.control_point_number_w,
                                    3), dtype=np.float32)

        self.lu = lx
        self.lv = ly
        self.lw = lz
        aux_x = self.get_knot_list(self.lu)
        aux_y = self.get_knot_list(self.lv)
        aux_z = self.get_knot_list(self.lw)
        for u, x in enumerate(aux_x):
            for v, y in enumerate(aux_y):
                for w, z in enumerate(aux_z):
                    self.ctrlPoints[u, v, w] = [x, y, z]

        # print(self.ctrlPoints.size)
        # for u in self.ctrlPoints:
        #     for v in self.ctrlPoints:
        #         for w in self.ctrlPoints:
        #             print(w)
        self.control_points_backup = self.ctrlPoints.copy()

        self.is_hit = []
        self.reset_is_hit()

    def reset_is_hit(self):
        self.is_hit = [False] * self.control_point_number_u * self.control_point_number_v * self.control_point_number_w

    def get_knot_list(self, length):
        if self.control_point_number_u == 5 and self.order_u == 3:
            first = -length / 2
            last = length / 2
            step = length / 6
            return [first, first + step, first + 3 * step, first + 5 * step, last]
        else:
            raise Exception('unImplement for other order and ctrl point')

    def move(self, x, y, z):
        for i, is_hit in enumerate(self.is_hit):
            if is_hit:
                u = i // (self.control_point_number_v * self.control_point_number_w)
                v = i % (self.control_point_number_v * self.control_point_number_w) // self.control_point_number_w
                w = i % self.control_point_number_w
                self.ctrlPoints[u, v, w] = self.control_points_backup[u, v, w] + [x, y, z]
                # self.ctrlPoints.flat[i][0] = self.control_points_backup.flat[i][0] + x
                # self.ctrlPoints.flat[i][1] = self.control_points_backup.flat[i][1] + y
                # self.ctrlPoints.flat[i][2] = self.control_points_backup.flat[i][2] + z

    def get_info(self):
        return np.array(
            [self.order_u, self.order_v, self.order_w,
             self.control_point_number_u, self.control_point_number_v, self.control_point_number_w,
             self.lu, self.lv, self.lw,
             -self.lu / 2, -self.lv / 2, -self.lw / 2], dtype='float32')

    def get_control_point_for_sample(self):
        # uvw三个方向的区间数
        interval_number_u = self.control_point_number_u - self.order_u + 1
        interval_number_v = self.control_point_number_v - self.order_v + 1
        interval_number_w = self.control_point_number_w - self.order_w + 1
        result = np.zeros((interval_number_u, interval_number_v, interval_number_w,
                           self.order_u, self.order_v, self.order_w,
                           3))
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
            for w, u, v in product(range(self.order_w),
                                   range(self.order_u),
                                   range(self.order_v)):
                control_points = self.ctrlPoints[
                    (control_point_base_u + l) * self.control_point_number_v * self.control_point_number_w +
                    (control_point_base_v + v) * self.control_point_number_w +
                    control_point_base_w + w]
                intermediate_results_1[w, ..., 0] = mu.dot()
                mu_u_l = sample_aux_matrix[mu + u * self.order_u + l]
                aux_multiply(mu_u_l, control_point, intermediate_results_1[u, v, w])

            box = np.zeros((self.order_u, self.order_v, self.order_w, 4))
            for u, v, w, l in product(range(self.order_u),
                                      range(self.order_v),
                                      range(self.order_w),
                                      range(self.order_v)):
                control_point = result[interval_index_u][interval_index_v][interval_index_w][u][l][w]
                Mv_v_l = sample_aux_matrix[mv + v * self.order_v + l]
                aux_multiply(Mv_v_l, control_point, box[u][v][w])

            for v, w, u in product(range(self.order_v),
                                   range(self.order_w),
                                   range(self.order_u)):
                result[interval_index_u, interval_index_v, interval_index_w, u, v, w] = 0
                for l in range(self.order_w):
                    control_point = box[interval_index_u, interval_index_v, l]
                    Mw_k_l = sample_aux_matrix[mw + w * self.order_w + l]
                    aux_multiply(Mw_k_l, control_point,
                                 result[interval_index_u, interval_index_v, interval_index_w, u, v, w])

        return result


def aux_multiply(value, v, result):
    result[0] += value * v[0]
    result[1] += value * v[1]
    result[2] += value * v[2]


if __name__ == '__main__':
    def foo(x, y, z, *all, **dict):
        print(x)
        print(y)
        print(z)
        for i in all:
            print(i)
        for k, v in dict.items():
            print(k)
            print(v)


    foo(2, 1, 3, a=2, b=3)
