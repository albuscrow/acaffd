from matplotlib.pyplot import *

point_size = 1
line_width = 1


def point(p, c):
    x = p[0::2]
    y = p[1::2]
    if c == 'r':
        plot(x, y, '.', markersize=point_size, color='r', linewidth=line_width)
    else:
        plot(x, y, '.', markersize=point_size, color='#888888', linewidth=line_width)


def line(p, c):
    for x1, y1, x2, y2 in zip(*[iter(p)] * 4):
        plot([x1, x2], [y1, y2], '.', [x1, x2], [y1, y2], '-', color=c, linewidth=line_width)


def triangles(p, c):
    for x1, y1, x2, y2, x3, y3 in zip(*[iter(p)] * 6):
        plot([x1, x2, x3, x1], [y1, y2, y3, y1], '-', color=c, linewidth=line_width)


def poly(p, c):
    x = p[0::2]
    y = p[1::2]
    x.append(x[0])
    y.append(y[0])
    plot(x, y, '-', color=c, linewidth=line_width)


table = {'ts': triangles,
         'poly': poly,
         'ls': line,
         'ps': point}


def clip():
    with open('figure.txt') as f:
        ls = []
        for l in f:
            ls.append(l)
    index = 0

    tokens = ls[0].split()
    table[tokens[0]](tokens[1:], 'k')

    axis('off')
    ylim([-1, 6])
    xlim([-1, 6])
    savefig('clip_figure' + str(index) + ".png")
    index += 1
    show()
    for i in range(1, len(ls) - 2):
        for l in ls[:i]:
            tokens = l.split()
            table[tokens[0]](tokens[1:], '#aaaaaa')

        tokens = ls[i].split()
        table[tokens[0]](tokens[1:], 'r')

        axis('off')
        ylim([-1, 6])
        xlim([-1, 6])
        savefig('clip_figure/clip_figure' + str(index) + ".png")
        index += 1
        show()
    tokens = ls[-2].split()
    table[tokens[0]](tokens[1:], 'k')

    axis('off')
    ylim([-1, 6])
    xlim([-1, 6])
    savefig('clip_figure/clip_figure' + str(index) + ".png")
    index += 1
    show()

    tokens = ls[-2].split()
    table[tokens[0]](tokens[1:], '#aaaaaa')

    tokens = ls[-1].split()
    table[tokens[0]](tokens[1:], 'r')

    axis('off')
    ylim([-1, 6])
    xlim([-1, 6])
    savefig('clip_figure/clip_figure' + str(index) + ".png")
    index += 1
    show()


def cvt_zoom():
    with open('figure_cvt.txt') as f:
        ls = []
        for l in f:
            ls.append(l)
    index = 0
    for i in range(len(ls) - 1):
        tokens = ls[i].split()
        table[tokens[0]](tokens[1:], '#aaaaaa')

        tokens = ls[i + 1].split()
        table[tokens[0]](tokens[1:], 'r')

        axis('off')
        xlim([1.8, 2.05])
        ylim([0.7, 0.905])
        savefig('clip_figure/v_zoom_clip_figure' + str(index) + ".png")
        index += 1
        show()

def cvt():
    with open('figure_cvt.txt') as f:
        ls = []
        for l in f:
            ls.append(l)
    index = 0
    for i in range(len(ls) - 1):
        tokens = ls[i].split()
        table[tokens[0]](tokens[1:], '#aaaaaa')

        tokens = ls[i + 1].split()
        table[tokens[0]](tokens[1:], 'r')

        axis('off')
        xlim([-1, 6])
        ylim([-1, 6])
        savefig('clip_figure/v_clip_figure' + str(index) + ".png")
        index += 1
        show()


def cvt_fine():
    with open('figure_cvt.txt') as f:
        ls = []
        for l in f:
            ls.append(l)
    index = 0
    for i in range(len(ls) - 1):
        tokens = ls[i].split()
        table[tokens[0]](tokens[1:], '#aaaaaa')

        tokens = ls[i + 1].split()
        table[tokens[0]](tokens[1:], 'r')
        plot([1.8, 2.05, 2.05, 1.8, 1.8], [0.7, 0.7, 0.95, 0.95, 0.7], '-k')

        axis('off')
        xlim([-1, 6])
        ylim([-1, 6])
        savefig('clip_figure/v_f_clip_figure' + str(index) + ".png")
        index += 1
        show()


def cvt_total():
    with open('figure_cvt.txt') as f:
        ls = []
        for l in f:
            ls.append(l)
    index = 0
    for i in range(len(ls) - 1):
        tokens = ls[i].split()
        table[tokens[0]](tokens[1:], '#aaaaaa')

    tokens = ls[-1].split()
    table[tokens[0]](tokens[1:], 'r')
    plot([1.8, 2.05, 2.05, 1.8, 1.8], [0.7, 0.7, 0.95, 0.95, 0.7], '-k')
    axis('off')
    xlim([-1, 6])
    ylim([-1, 6])
    savefig('clip_figure/t_v_clip_figure' + str(index) + ".png")
    index += 1
    show()

    for i in range(len(ls) - 1):
        tokens = ls[i].split()
        table[tokens[0]](tokens[1:], '#aaaaaa')

    tokens = ls[-1].split()
    table[tokens[0]](tokens[1:], 'r')

    axis('off')
    xlim([1.8, 2.05])
    ylim([0.7, 0.905])
    # xlim([-1, 6])
    # ylim([-1, 6])
    savefig('clip_figure/t_v_clip_figure' + str(index) + ".png")
    index += 1
    show()


# clip()
# cvt()
# cvt_total()
cvt_zoom()
