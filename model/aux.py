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
        aux_x = self.get_control_point_aux_list(self.lu)
        aux_y = self.get_control_point_aux_list(self.lv)
        aux_z = self.get_control_point_aux_list(self.lw)
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

    def get_control_point_aux_list(self, length):
        if self.control_point_number_u == 5 and self.order_u == 3:
            return [-length / 2, -length / 3, 0, length / 3, length / 2]
        else:
            raise Exception('unImplement for other order and ctrl point')

    def move(self, x, y, z):
        for i, is_hit in enumerate(self.is_hit):
            if is_hit:
                u = i // (self.control_point_number_v * self.control_point_number_w)
                v = i % (self.control_point_number_v * self.control_point_number_w) // self.control_point_number_w
                w = i % self.control_point_number_w
                self.ctrlPoints[u, v, w] = self.control_points_backup[u, v, w] + [x, y, z]

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

            intermediate_results_2 = np.zeros((self.order_u, self.order_v, self.order_w, 4))
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
