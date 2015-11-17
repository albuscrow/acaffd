import numpy as np
from copy import deepcopy


class BSplineBody:
    def __init__(self, lx, ly, lz, *argv):
        if len(argv) == 0:
            # 阶数，阶数 = p + 1,当阶数=1时，基函数为常数。是每个knot区间所对应的顶点数。当knot左右重合顶点为阶数时，b-spline始末与控制顶点重合
            self.order_u = 3
            self.order_v = 3
            self.order_w = 3
            # 控制顶点数，knot节点数 = 阶数 + 控制顶点数
            self.ctrl_u = 5
            self.ctrl_v = 5
            self.ctrl_w = 5
        elif len(argv) == 6:
            self.order_u = argv[0]
            self.order_v = argv[1]
            self.order_w = argv[2]
            # 控制顶点数，knot节点数 = 阶数 + 控制顶点数
            self.ctrl_u = argv[3]
            self.ctrl_v = argv[4]
            self.ctrl_w = argv[5]
        else:
            raise Exception('input argv number error')
        self.ctrlPoints = []

        self.lu = lx
        self.lv = ly
        self.lw = lz
        aux_x = self.get_knot_list(self.lu)
        aux_y = self.get_knot_list(self.lv)
        aux_z = self.get_knot_list(self.lw)
        for x in aux_x:
            for y in aux_y:
                for z in aux_z:
                    self.ctrlPoints.append([x, y, z])
        self.control_points_backup = deepcopy(self.ctrlPoints)

        self.is_hit = []
        self.reset_is_hit()

    def reset_is_hit(self):
        self.is_hit = [False] * self.ctrl_u * self.ctrl_v * self.ctrl_w

    def get_knot_list(self, length):
        if self.ctrl_u == 5 and self.order_u == 3:
            first = -length / 2
            last = length / 2
            step = length / 6
            return [first, first + step, first + 3 * step, first + 5 * step, last]
        else:
            raise Exception('unImplement for other order and ctrl point')

    def move(self, x, y, z):
        for i in range(len(self.is_hit)):
            if self.is_hit[i]:
                self.ctrlPoints[i][0] = self.control_points_backup[i][0] + x
                self.ctrlPoints[i][1] = self.control_points_backup[i][1] + y
                self.ctrlPoints[i][2] = self.control_points_backup[i][2] + z

    def get_info(self):
        return np.array(
            [self.order_u, self.order_v, self.order_w,
             self.ctrl_u, self.ctrl_v, self.ctrl_w,
             self.lu, self.lv, self.lw,
             -self.lu / 2, -self.lv / 2, -self.lw / 2], dtype='float32')


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
