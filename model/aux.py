import numpy as np


class BSplineBody:
    def __init__(self, *argv):
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
        self.point = []
        for x in np.arange(-1, 1.001, 2 / (self.ctrl_x - 1)):
            for y in np.arange(-1, 1.001, 2 / (self.ctrl_y - 1)):
                for z in np.arange(-1, 1.001, 2 / (self.ctrl_z - 1)):
                    self.point.append([x, y, z])
