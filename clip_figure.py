from matplotlib.pyplot import *
import matplotlib.image as mpimg
from PIL import Image

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
# unzoom_img = mpimg.imread("clip_figure/cvt_total.png")
# print(unzoom_img.shape)
# print(unzoom_img.transpose((1, 0, 2)).shape)
# print(unzoom_img)


def gen_error_cube(file_name):
    pic = mpimg.imread('error/' + file_name)
    colormap = mpimg.imread('res/colormap.png').transpose((1, 0, 2))[::-1, ::, ::]
    picPosition = (150, 0)
    outputSize = pic.shape[:2]
    picSize = [x * 0.8 for x in pic.shape[:2]]

    # picSize[1] += 200

    def ps2e(p, s):
        return (p[0], p[0] + s[0], p[1], p[1] + s[1])

    colorSize = (10, 200)
    colorMapExtent = (outputSize[0] - colorSize[0], outputSize[0],
                      0 + 50, colorSize[1] + 50)

    imshow(pic, extent=ps2e(picPosition, picSize), zorder=-1)
    imshow(colormap, extent=colorMapExtent, zorder=-1)

    text(outputSize[0] - 50, 55, '    0', fontsize=11)
    text(outputSize[0] - 63, 35 + colorSize[1], ' π/30', fontsize=11)
    gca().get_xaxis().set_visible(False)
    gca().get_yaxis().set_visible(False)

    xlim([150, outputSize[0]])
    ylim([50, outputSize[1] - 200])
    # grid()
    savefig('/home/ac/paperlzq/pic/7_with_colormap.png', bbox_inches='tight', pad_inches=-0.015)
    # show()


def gen_error_cube_and_teapot(file_name_cube, file_name_teapot, output_file_name):
    gcf().clear()
    cube = mpimg.imread('error/' + file_name_cube)
    teapot = mpimg.imread('error/' + file_name_teapot)

    original_size = teapot.shape[1::-1]

    colormap = mpimg.imread('res/colormap.png').transpose((1, 0, 2))[::-1, ::, ::]

    cube_size = list(original_size)
    teapot_size = list(original_size)
    color_map_size = colormap.shape[1::-1]

    cube_position = (0, 0)
    teapot_position = (cube_size[0] - 100, -150)
    color_map_position = [teapot_position[0] - 55, 50]

    text_offset = 35
    text_down_position = [color_map_position[0] + text_offset, color_map_position[1]]
    text_up_position = [color_map_position[0] + text_offset, color_map_position[1] + color_map_size[1] - 20]
    text_font_size = 20

    output_range_x = [0, teapot_size[0] * 2 - 100]
    output_range_y = [45, teapot_size[1] - 200]

    def get_range_size(x):
        return x[1] - x[0]

    # print(output_range_x)
    # print(output_range_y)

    def ps2e(p, s):
        return (p[0], p[0] + s[0], p[1], p[1] + s[1])

    imshow(cube, extent=ps2e(cube_position, [x * 0.8 for x in cube_size]), zorder=-1)
    imshow(teapot, extent=ps2e(teapot_position, teapot_size), zorder=-1)
    # imshow(colormap, extent=ps2e(color_map_position, color_map_size), zorder=-1)
    #
    # text(*text_down_position, '0', fontsize=text_font_size)
    # text(*text_up_position, top_text, fontsize=text_font_size)
    gca().get_xaxis().set_visible(False)
    gca().get_yaxis().set_visible(False)
    xlim(output_range_x)
    ylim(output_range_y)
    dpi = 100
    gcf().set_size_inches(get_range_size(output_range_x) / dpi, get_range_size(output_range_y) / dpi)
    savefig('/home/ac/paperlzq/pic/' + output_file_name, bbox_inches='tight', pad_inches=-3 / 100, dpi=dpi)


def gen_clip_figure_with_color_map():
    gcf().clear()
    left_image = mpimg.imread('clip_quality2.png')
    right_image = mpimg.imread('clip_quality1.png')

    original_size = right_image.shape[1::-1]

    colormap = mpimg.imread('res/colormap.png').transpose((1, 0, 2))[::, ::, ::]

    dst_size = [x for x in original_size]
    color_map_size = colormap.shape[1::-1]

    right_position = (0, 0)
    left_position = (original_size[0] + 50, 0)
    color_map_position = [left_position[0] - 50, 20]

    text_offset = 35
    text_down_position = [color_map_position[0] + text_offset, color_map_position[1]]
    text_up_position = [color_map_position[0] + text_offset, color_map_position[1] + color_map_size[1] - 20]
    text_font_size = 20

    output_range_x = [0, original_size[0] * 2 + 50]
    output_range_y = [0, original_size[1]]

    def get_range_size(x):
        return x[1] - x[0]

    def ps2e(p, s):
        return (p[0], p[0] + s[0], p[1], p[1] + s[1])

    imshow(left_image, extent=ps2e(right_position, dst_size), zorder=-1)
    imshow(right_image, extent=ps2e(left_position, dst_size), zorder=-1)
    imshow(colormap, extent=ps2e(color_map_position, color_map_size), zorder=-1)

    text(*text_down_position, '0', fontsize=text_font_size)
    text(*text_up_position, '1', fontsize=text_font_size)
    # gca().get_xaxis().set_visible(False)
    # gca().get_yaxis().set_visible(False)
    xlim(output_range_x)
    ylim(output_range_y)
    dpi = 100
    gcf().set_size_inches(get_range_size(output_range_x) / dpi, get_range_size(output_range_y) / dpi)
    png = '/home/ac/thesis/zju_thesis/figures/clip/clip_compare.png'
    savefig(png, bbox_inches='tight', pad_inches=-3 / 100, dpi=dpi)
    clip_image(png)
    show()


def clip_image(image_path):
    ori = Image.open(image_path)
    w, h = ori.size
    ori.crop((0, 0, w / 2, h)).save('0.'.join(image_path.split('.')))
    ori.crop((w / 2, 0, w, h)).save('1.'.join(image_path.split('.')))


def gen_error_cube_and_teapot_with_color_map(file_name_cube, file_name_teapot, top_text, output_file_name):
    gcf().clear()
    cube = mpimg.imread('error/' + file_name_cube)
    teapot = mpimg.imread('error/' + file_name_teapot)

    original_size = teapot.shape[1::-1]

    colormap = mpimg.imread('res/colormap.png').transpose((1, 0, 2))[::-1, ::, ::]

    cube_size = list(original_size)
    teapot_size = list(original_size)
    color_map_size = colormap.shape[1::-1]

    cube_position = (0, 0)
    teapot_position = (cube_size[0] - 100, -150)
    color_map_position = [teapot_position[0] - 55, 50]

    text_offset = 35
    text_down_position = [color_map_position[0] + text_offset, color_map_position[1]]
    text_up_position = [color_map_position[0] + text_offset, color_map_position[1] + color_map_size[1] - 20]
    text_font_size = 20

    output_range_x = [0, teapot_size[0] * 2 - 100]
    output_range_y = [45, teapot_size[1] - 200]

    def get_range_size(x):
        return x[1] - x[0]

    # print(output_range_x)
    # print(output_range_y)

    def ps2e(p, s):
        return (p[0], p[0] + s[0], p[1], p[1] + s[1])

    imshow(cube, extent=ps2e(cube_position, [x * 0.8 for x in cube_size]), zorder=-1)
    imshow(teapot, extent=ps2e(teapot_position, teapot_size), zorder=-1)
    imshow(colormap, extent=ps2e(color_map_position, color_map_size), zorder=-1)

    text(*text_down_position, '0', fontsize=text_font_size)
    text(*text_up_position, top_text, fontsize=text_font_size)
    gca().get_xaxis().set_visible(False)
    gca().get_yaxis().set_visible(False)
    xlim(output_range_x)
    ylim(output_range_y)
    dpi = 100
    gcf().set_size_inches(get_range_size(output_range_x) / dpi, get_range_size(output_range_y) / dpi)
    savefig('/home/ac/paperlzq/pic/' + output_file_name, bbox_inches='tight', pad_inches=-3 / 100, dpi=dpi)


def gen_error_teapot(file_name):
    pic = mpimg.imread('error/' + file_name)
    colormap = mpimg.imread('res/colormap.png').transpose((1, 0, 2))[::-1, ::, ::]
    picPosition = (0, -150)
    picSize = list(pic.shape[:2])

    # picSize[1] += 200

    def ps2e(p, s):
        return (p[0], p[0] + s[0], p[1], p[1] + s[1])

    colorSize = (10, 200)
    colorMapExtent = (0, colorSize[0],
                      0 + 50, colorSize[1] + 50)

    imshow(pic, extent=ps2e(picPosition, picSize), zorder=-1)
    imshow(colormap, extent=colorMapExtent, zorder=-1)
    gca().get_xaxis().set_visible(False)
    gca().get_yaxis().set_visible(False)
    xlim([0, picSize[0]])
    ylim([50, picSize[1] - 200])
    grid()
    savefig('/home/ac/paperlzq/pic/teapot7_with_colormap.png', bbox_inches='tight', pad_inches=0, frameon=True)
    # show()


# gen_error_teapot('teapot/teapot7.png')
# gen_error_cube('cube/cube7.png')
# gen_error_cube_and_teapot('cube/cube0.png', 'teapot/teapot0.png', 'error0')
# gen_error_cube_and_teapot('cube/cube1.png', 'teapot/teapot1.png', 'error1')
# gen_error_cube_and_teapot('cube/cube2.png', 'teapot/teapot2.png', 'error2')
# gen_error_cube_and_teapot('cube/cube3.png', 'teapot/teapot3.png', 'error3')
#
# gen_error_cube_and_teapot_with_color_map('cube/cube4.png', 'teapot/teapot4.png', '0.04', 'error4')
# gen_error_cube_and_teapot_with_color_map('cube/cube5.png', 'teapot/teapot5.png', 'π/30', 'error5')
# gen_error_cube_and_teapot_with_color_map('cube/cube6.png', 'teapot/teapot6.png', '0.04', 'error6')
# gen_error_cube_and_teapot_with_color_map('cube/cube7.png', 'teapot/teapot7.png', 'π/30', 'error7')

gen_clip_figure_with_color_map()
