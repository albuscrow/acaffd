from matplotlib.pyplot import *
import matplotlib.image as mpimg

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
    global point_size
    point_size = 10
    global line_width
    line_width = 5

    # read from file
    before_cvt = []
    after_cvt = []
    ls = before_cvt
    with open('figure2.txt') as f:
        for l in f:
            if l.strip() == 'cvt':
                ls = after_cvt
                continue
            ls.append(l)

    # original triangle black
    index = 0
    tokens = before_cvt[0].split()
    table[tokens[0]](tokens[1:], 'k')
    axis('off')
    ylim([-1, 6])
    xlim([-1, 6])
    savefig('clip_figure' + str(index) + ".png")
    index += 1
    show()

    for i in range(1, len(before_cvt) - 1):
        for l in before_cvt[:i]:
            tokens = l.split()
            table[tokens[0]](tokens[1:], '#aaaaaa')

        tokens = before_cvt[i].split()
        table[tokens[0]](tokens[1:], 'r')

        axis('off')
        ylim([-1, 6])
        xlim([-1, 6])
        savefig('clip_figure/clip_figure' + str(index) + ".png")
        index += 1
        show()
    # cvt 之前的分割结果
    tokens = before_cvt[-1].split()
    table[tokens[0]](tokens[1:], 'k')
    axis('off')
    ylim([-1, 6])
    xlim([-1, 6])
    savefig('clip_figure/clip_figure' + str(index) + ".png")
    index += 1
    show()

    # cvt
    tokens = before_cvt[-1].split()
    table[tokens[0]](tokens[1:], '#aaaaaa')
    tokens = after_cvt[-1].split()
    table[tokens[0]](tokens[1:], 'r')
    axis('off')
    ylim([-1, 6])
    xlim([-1, 6])
    savefig('clip_figure/clip_figure' + str(index) + ".png")
    index += 1
    show()

    # 最终结果
    tokens = after_cvt[-1].split()
    table[tokens[0]](tokens[1:], 'k')
    axis('off')
    ylim([-1, 6])
    xlim([-1, 6])
    savefig('clip_figure/clip_figure' + str(index) + ".png")
    index += 1
    show()


def cvt():
    global point_size
    point_size = 4
    global line_width
    line_width = 2

    # read from file
    before_cvt = []
    after_cvt = []
    ls = before_cvt
    with open('figure1.txt') as f:
        for l in f:
            if l.strip() == 'cvt':
                ls = after_cvt
                continue
            ls.append(l)

    after_cvt = [before_cvt[-1]] + after_cvt
    cvt_zoom_compare(after_cvt)
    cvt_zoom_total(after_cvt)
    cvt_compare(after_cvt)
    cvt_total(after_cvt)


def cvt_zoom_compare(ls):
    index = 0
    # zoom every iter
    for i in range(len(ls) - 1):
        tokens = ls[i].split()
        table[tokens[0]](tokens[1:], '#aaaaaa')

        tokens = ls[i + 1].split()
        table[tokens[0]](tokens[1:], 'r')

        gca().get_xaxis().set_visible(False)
        gca().get_yaxis().set_visible(False)
        xlim([1.8, 2.05])
        ylim([0.7, 0.905])
        savefig('clip_figure/cvt_zoom_compare' + str(index) + ".png", bbox_inches='tight', pad_inches=0)
        index += 1
        show()


def cvt_zoom_total(ls):
    d = (0.4, 0.4, 0.4)
    o = (0.8, 0.8, 0.8)
    for i in range(len(ls) - 1):
        tokens = ls[i].split()
        table[tokens[0]](tokens[1:], interpolate_color(o, d, i / (len(ls) - 1)))

    tokens = ls[-1].split()
    table[tokens[0]](tokens[1:], 'r')

    gca().get_xaxis().set_visible(False)
    gca().get_yaxis().set_visible(False)
    xlim([1.8, 2.05])
    ylim([0.7, 0.905])
    savefig('clip_figure/cvt_zoom_total.png', bbox_inches='tight', pad_inches=0)
    show()


def cvt_compare(ls):
    index = 0
    for i in range(len(ls) - 1):
        tokens = ls[i].split()
        table[tokens[0]](tokens[1:], '#aaaaaa')

        tokens = ls[i + 1].split()
        table[tokens[0]](tokens[1:], 'r')
        plot([1.8, 2.05, 2.05, 1.8, 1.8], [0.7, 0.7, 0.95, 0.95, 0.7], '-k')

        gca().get_xaxis().set_visible(False)
        gca().get_yaxis().set_visible(False)
        xlim([-0.05, 6])
        ylim([-0.05, 6])
        savefig('clip_figure/cvt_compare' + str(index) + ".png", bbox_inches='tight', pad_inches=0)
        index += 1
        show()


def cvt_total(ls):
    d = (0.4, 0.4, 0.4)
    o = (0.8, 0.8, 0.8)
    for i in range(len(ls) - 1):
        tokens = ls[i].split()
        table[tokens[0]](tokens[1:], interpolate_color(o, d, i / (len(ls) - 1)))

    tokens = ls[-1].split()
    table[tokens[0]](tokens[1:], 'r')
    plot([1.8, 2.05, 2.05, 1.8, 1.8], [0.7, 0.7, 0.95, 0.95, 0.7], '-k')
    gca().get_xaxis().set_visible(False)
    gca().get_yaxis().set_visible(False)
    xlim([-0.05, 6])
    ylim([-0.05, 6])
    savefig('clip_figure/cvt_total.png', bbox_inches='tight', pad_inches=0)
    show()


def interpolate_color(o, d, p):
    if 0 > p or p > 1:
        raise Exception()
    return tuple((oo + (dd - oo) * p for oo, dd in zip(o, d)))


def show_cvt_in_different_stage():
    ls = []
    with open('cvt.txt') as f:
        for l in f:
            ls.append(l)
    index = 0
    for l1, l2 in zip(*[iter(ls)] * 2):
        tokens = l1.split()
        table[tokens[0]](tokens[1:], 'k')
        tokens = l2.split()
        table[tokens[0]](tokens[1:], 'r')
        axis('off')
        # xlim([-1, 6])
        # ylim([-1, 6])
        savefig('clip_figure/show_cvt_in_different_stage%d.png' % index)
        index += 1
        show()


def cvt_for_paper():
    zoom = 'clip_figure/cvt_zoom_compare%d.png'
    unzoom = 'clip_figure/cvt_compare%d.png'
    index = 0
    unzoom_image_position = (200, 300)
    unzoom_image_width = 800

    zoom_image_position = (0, 0)
    zoom_image_width = 400

    def pw2e(p, w):
        return (p[0], p[0] + w, p[1], p[1] + w * 0.75)

    for i in range(5):
        unzoom_img = mpimg.imread(unzoom % index)[5:-3, 5:-3]
        zoom_img = mpimg.imread(zoom % index)[5:-3, 5:-3]
        # print(zoom_img)
        imshow(unzoom_img, extent=pw2e(unzoom_image_position, unzoom_image_width), zorder=-1)
        imshow(zoom_img, extent=pw2e(zoom_image_position, zoom_image_width), zorder=-1)
        # axis('off')
        plot([443, 0], [396, 300], 'k', linewidth=1)
        plot([476, 400], [374, 0], 'k', linewidth=1)
        plot([0, 400, 400, 0, 0], [0, 0, 300, 300, 0], 'k', linewidth=1)
        gca().get_xaxis().set_visible(False)
        gca().get_yaxis().set_visible(False)
        xlim([-50, 950])
        ylim([-50, 950])
        grid()
        savefig('clip_figure/cvt_for_paper%d.png' % index)
        index += 1
        show()

    unzoom_img = mpimg.imread("clip_figure/cvt_total.png")[5:-3, 5:-3]
    zoom_img = mpimg.imread("clip_figure/cvt_zoom_total.png")[5:-3, 5:-3]
    # print(zoom_img)
    imshow(unzoom_img, extent=pw2e(unzoom_image_position, unzoom_image_width), zorder=-1)
    imshow(zoom_img, extent=pw2e(zoom_image_position, zoom_image_width), zorder=-1)
    # axis('off')
    plot([443, 0], [396, 300], 'k', linewidth=1)
    plot([476, 400], [374, 0], 'k', linewidth=1)
    plot([0, 400, 400, 0, 0], [0, 0, 300, 300, 0], 'k', linewidth=1)
    gca().get_xaxis().set_visible(False)
    gca().get_yaxis().set_visible(False)
    xlim([-50, 950])
    ylim([-50, 950])
    grid()
    savefig('clip_figure/cvt_for_paper%d.png' % index)
    index += 1
    show()


# clip()
# cvt()
# show_cvt_in_different_stage()
# cvt_for_paper()
unzoom_img = mpimg.imread("clip_figure/cvt_total.png")
print(unzoom_img.shape)
print(unzoom_img.transpose((1, 0, 2)).shape)
# print(unzoom_img)
