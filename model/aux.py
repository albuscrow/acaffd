import numpy as np


class BSplineBody:
    def __init__(self, lx, ly, lz, *argv):
        if len(argv) == 0:
            # 阶数，阶数 = p + 1,当阶数=1时，基函数为常数。是每个knot区间所对应的顶点数。当knot左右重合顶点为阶数时，b-spline始末与控制顶点重合
            self.order_x = 3
            self.order_y = 3
            self.order_z = 3
            # 控制顶点数，knot节点数 = 阶数 + 控制顶点数
            self.ctrl_x = 5
            self.ctrl_y = 5
            self.ctrl_z = 5
        elif len(argv) == 6:
            self.order_x = argv[0]
            self.order_y = argv[1]
            self.order_z = argv[2]
            # 控制顶点数，knot节点数 = 阶数 + 控制顶点数
            self.ctrl_x = argv[3]
            self.ctrl_y = argv[4]
            self.ctrl_z = argv[5]
        else:
            raise Exception('input argv number error')
        self.ctrlPoints = []

        knot_list = self.get_knot_list(lx)
        get_knot_list = self.get_knot_list(ly)
        self_get_knot_list = self.get_knot_list(lz)
        for x in knot_list:
            for y in get_knot_list:
                for z in self_get_knot_list:
                    self.ctrlPoints.append([x, y, z])

        self.is_hit = []
        self.reset_is_hit()

    def reset_is_hit(self):
        self.is_hit = [False] * self.ctrl_x * self.ctrl_y * self.ctrl_z

    def get_knot_list(self, length):
        if self.ctrl_x == 5 and self.order_x == 3:
            first = -length / 2
            last = length / 2
            step = length / 6
            return [first, first + step, first + 3 * step, first + 5 * step, last]
        else:
            raise Exception('unImplement for other order and ctrl point')

    def move(self, x, y, z):
        for i in range(len(self.is_hit)):
            if self.is_hit[i]:
                self.ctrlPoints[i][0] += x
                self.ctrlPoints[i][1] += y
                self.ctrlPoints[i][2] += z


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
