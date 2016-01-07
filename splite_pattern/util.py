import numpy as np
import random
from tkinter import *

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
    look_up_table_for_i.append(int(look_up_table_for_i[-1] + (1 + ii) * ii / 2 + max(0, i * (factor - 2 * i))))

print(look_up_table_for_i)


def get_offset(i, j, k):
    if j - i <= factor - 2 * i:
        return look_up_table_for_i[i - 1] + (j - i) * i + k - j
    else:
        # print(compute_n + (j - i) * (factor - 2 * i))
        h = min(i, factor - i)
        gl = h - (factor - j)
        qianmian = max((factor - 2 * i) * i, 0)
        zhebian = (h + (h - gl + 1)) * gl / 2
        return look_up_table_for_i[i - 1] + qianmian + zhebian + k - j


print(get_offset(10, 10, 14))


def gen_point(m):
    return [random.random() * m, random.random() * m]


def point_distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def gen_triangle():
    while True:
        p1 = gen_point(19)
        p2 = gen_point(19)
        p3 = gen_point(19)
        if point_distance(p1, p2) < factor and point_distance(p2, p3) < factor and point_distance(p3, p1) < factor:
            return [p1, p2, p3]


def redrawAll(canvas):
    # t = gen_triangle()
    # l01 = point_distance(t[0], t[1])
    # l12 = point_distance(t[1], t[2])
    # l20 = point_distance(t[2], t[0])
    # if l01 < l12 and l01 < l20:
    #     if l12 < l20:
    #         p0 = t[0]
    #         p1 = t[1]
    #         p2 = t[2]
    #     else:
    #         p0 = t[1]
    #         p1 = t[0]
    #         p2 = t[2]
    # elif l12 < l20:
    #     if l01 < l20:
    #         p0 = t[2]
    #         p1 = t[1]
    #         p2 = t[0]
    #     else:
    #         p0 = t[1]
    #         p1 = t[2]
    #         p2 = t[0]
    # else:
    #     if l12 < l01:
    #         p0 = t[0]
    #         p1 = t[2]
    #         p2 = t[1]
    #     else:
    #         p0 = t[2]
    #         p1 = t[0]
    #         p2 = t[1]
    #
    # i = min(l01, l12, l20)
    # k = max(l01, l12, l20)
    # j = l01 + l12 + l20 - i - k
    # i = round(i)
    # j = round(j)
    # k = round(k)
    #
    # offset = offset_number[get_offset(i, j, k)]
    # print(i, j, k)
    # print(offset)
    #
    # canvas.delete(ALL)
    # for i in range(offset[0], offset[0] + offset[1]):
    #     sp0 = parameter[indexes[i][0]]
    #     sp1 = parameter[indexes[i][1]]
    #     sp2 = parameter[indexes[i][2]]
    #     spp0 = sample(p0, p1, p2, sp0)
    #     spp1 = sample(p0, p1, p2, sp1)
    #     spp2 = sample(p0, p1, p2, sp2)
    #     canvas.create_polygon(*spp0, *spp1, *spp2, fill='', outline="blue", width=2)
    # draw a red rectangle on the left half
    # canvas.create_rectangle(0, 0, 250, 600, fill="red")
    # draw semi-transparent rectangles in the middle
    # canvas.create_rectangle(200, 75, 300, 125, fill="blue", stipple="")
    # canvas.create_rectangle(200, 175, 300, 225, fill="blue", stipple="gray75")
    # canvas.create_rectangle(200, 275, 300, 325, fill="blue", stipple="gray50")
    # canvas.create_rectangle(200, 375, 300, 425, fill="blue", stipple="gray25")
    # canvas.create_rectangle(200, 475, 300, 525, fill="blue", stipple="gray12")
    i, j, k = [x * 100 for x in [2.4, 3.4, 5.6]]
    s = (i + j + k) / 2
    a = (s * (s - i) * (s - j) * (s - k)) ** 0.5
    y = 2 * a / i
    x = (k ** 2 - y ** 2) ** 0.5
    canvas.create_polygon(0, 0, i, 0, x, y,  fill='', outline="blue", width=2)
    # canvas.create_polygon(0, 0, i, 0, x/ 2, y / 2,  fill='', outline="blue", width=2)
    for j in range(1, 6):
        i_ = x * (j / 6)
        y_i_ = y * (j / 6)
        canvas.create_polygon(0, 0, i, 0, i_, y_i_, fill='', outline="blue", width=2)


def sample(p1, p2, p3, sp):
    return [(p1[0] * sp[0] + p2[0] * sp[1] + p3[0] * sp[2]) * 20,
            (p1[1] * sp[0] + p2[1] * sp[1] + p3[1] * sp[2]) * 20]


def init(canvas):
    redrawAll(canvas)


########### copy-paste below here ###########

def run():
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=500, height=600)
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
