import numpy as np
import random
from tkinter import *
import math

with open('20.txt') as file:
    factor, offset_number_l, indexes_l, parameter_l = file

factor = int(factor)

offset_number = np.asarray([int(x) for x in offset_number_l.strip().split(" ")], dtype=np.int)
offset_number.shape = (-1, 2)

indexes = np.asarray([int(x) for x in indexes_l.strip().split(" ")], dtype=np.int)
indexes.shape = (-1, 4)

parameter = np.asarray([float(x) for x in parameter_l.strip().split(" ")], dtype=np.float32)
parameter.shape = (-1, 4)

look_up_table_for_i = [0]
for i in range(1, factor):
    ii = min(factor - i, i)
    look_up_table_for_i.append(int(look_up_table_for_i[-1] + (1 + ii) * ii / 2 + max(0, (i + 1) * (factor - 2 * i))))

print(look_up_table_for_i)


def get_offset(i, j, k):
    if j - i + 1 <= factor - 2 * i:
        return look_up_table_for_i[i - 1] + (j - i) * (i + 1) + k - j
    else:
        qianmianbudongpaishu = max((factor - 2 * i), 0)
        shouxiang = min(i, factor - i)
        xiangshu = j - i - qianmianbudongpaishu
        return look_up_table_for_i[i - 1] + (i + 1) * qianmianbudongpaishu + xiangshu * (shouxiang + (shouxiang + 1 - xiangshu)) / 2 + k - j


# print(get_offset(10, 10, 14))


def gen_point(m):
    return [random.random() * m + 10, random.random() * m + 10]


def point_distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def gen_triangle():
    while True:
        # p1 = gen_point(15)
        p1 = [10, 10]
        # p2 = gen_point(15)
        p2 = gen_point(300)
        p3 = gen_point(300)
        if point_distance(p1, p2) < factor - 1 and point_distance(p2, p3) < factor -1 and point_distance(p3, p1) < factor - 1:
            return [p1, p2, p3]


def redrawAll(canvas):
    t = gen_triangle()
    # t = []
    # triangle = [ x for x in [0,0, 0, 2, 2, 2]]
    # for i in range(3):
    #     t.append([triangle[i * 2], triangle[i * 2 + 1]])
    l01 = point_distance(t[0], t[1])
    l12 = point_distance(t[1], t[2])
    l20 = point_distance(t[2], t[0])
    if l01 < l12 and l01 < l20:
        if l12 < l20:
            p0 = t[0]
            p1 = t[1]
            p2 = t[2]
        else:
            p0 = t[1]
            p1 = t[0]
            p2 = t[2]
    elif l12 < l20:
        if l01 < l20:
            p0 = t[2]
            p1 = t[1]
            p2 = t[0]
        else:
            p0 = t[1]
            p1 = t[2]
            p2 = t[0]
    else:
        if l12 < l01:
            p0 = t[0]
            p1 = t[2]
            p2 = t[1]
        else:
            p0 = t[2]
            p1 = t[0]
            p2 = t[1]

    i = min(l01, l12, l20)
    k = max(l01, l12, l20)
    j = l01 + l12 + l20 - i - k
    i = math.ceil(i)
    j = math.ceil(j)
    k = math.ceil(k)

    offset = offset_number[get_offset(i, j, k)]
    print(i, j, k)
    print(offset)

    canvas.delete(ALL)
    temp = t[0] + t[1] + t[2]
    # temp = [x * 20 for x in temp]
    print("triangle", temp)
    # canvas.create_polygon(*temp, fill='', outline="red", width=2)
    for i in range(offset[0], offset[0] + offset[1]):
        sp0 = parameter[indexes[i][0]]
        sp1 = parameter[indexes[i][1]]
        sp2 = parameter[indexes[i][2]]
        spp0 = sample(p0, p1, p2, sp0)
        spp1 = sample(p0, p1, p2, sp1)
        spp2 = sample(p0, p1, p2, sp2)
        canvas.create_polygon(*spp0, *spp1, *spp2, fill='', outline="blue", width=2)
    # i, j, k = [x * 100 for x in [2.4, 3.4, 5.6]]
    # s = (i + j + k) / 2
    # a = (s * (s - i) * (s - j) * (s - k)) ** 0.5
    # y = 2 * a / i
    # x = (k ** 2 - y ** 2) ** 0.5
    # canvas.create_polygon(0, 0, i, 0, x, y,  fill='', outline="blue", width=2)
    # # canvas.create_polygon(0, 0, i, 0, x/ 2, y / 2,  fill='', outline="blue", width=2)
    # for j in range(1, 6):
    #     i_ = x * (j / 6)
    #     y_i_ = y * (j / 6)
    #     canvas.create_polygon(0, 0, i, 0, i_, y_i_, fill='', outline="blue", width=2)


def sample(p1, p2, p3, sp):
    return [(p1[0] * sp[0] + p2[0] * sp[1] + p3[0] * sp[2]) * 20,
            (p1[1] * sp[0] + p2[1] * sp[1] + p3[1] * sp[2]) * 20]


def init(canvas):
    redrawAll(canvas)


########### copy-paste below here ###########

def run():
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=950, height=1080)
    canvas.pack()
    # Store canvas in root and in canvas itself for callbacks
    root.canvas = canvas.canvas = canvas
    # Set up canvas data and call init
    canvas.data = {}
    init(canvas)
    # set up events
    # root.bind("<Button-1>", mousePressed)
    # root.bind("<Key>", keyPressed)
    # timerFired(canvas)
    # and launch the app
    root.mainloop()  # This call BLOCKS (so your program waits until you close the window!)

run()
