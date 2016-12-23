from PIL import Image
from matplotlib.pyplot import *
import matplotlib.image as mpimg

import sys

sys.path.append('../')
import util.figure_util as figutil


def gen_clip_figure_with_color_map(f4, f5, f1, f2, f3, low_text, high_text):
    gcf().clear()
    left_image = mpimg.imread(f4)
    right_image = mpimg.imread(f5)

    original_size = right_image.shape[1::-1]

    colormap = mpimg.imread('colormap.png').transpose((1, 0, 2))[::-1, ::, ::]

    dst_size = [x for x in original_size]
    color_map_size = colormap.shape[1::-1]

    right_position = (0, 0)
    left_position = (original_size[0], 0)
    color_map_position = [left_position[0] - 30, 20]

    text_offset = 35
    text_down_position = [color_map_position[0] + text_offset, color_map_position[1]]
    text_up_position = [color_map_position[0] + text_offset, color_map_position[1] + color_map_size[1] - 20]
    text_font_size = 24

    output_range_x = [0, original_size[0] * 2 + 50]
    output_range_y = [0, original_size[1]]

    def get_range_size(x):
        return x[1] - x[0]

    def ps2e(p, s):
        return p[0], p[0] + s[0], p[1], p[1] + s[1]

    imshow(left_image, extent=ps2e(right_position, dst_size), zorder=-1)
    imshow(right_image, extent=ps2e(left_position, dst_size), zorder=-1)
    imshow(colormap, extent=ps2e(color_map_position, color_map_size), zorder=-1)

    text(*text_down_position, low_text, fontsize=text_font_size)
    text(*text_up_position, high_text, fontsize=text_font_size)
    # gca().get_xaxis().set_visible(False)
    # gca().get_yaxis().set_visible(False)
    xlim(output_range_x)
    ylim(output_range_y)
    dpi = 100
    gcf().set_size_inches(get_range_size(output_range_x) / dpi, get_range_size(output_range_y) / dpi)
    # png = '/home/ac/thesis/zju_thesis/figures/clip/clip_compare.png'
    png = f3
    gca().axis('off')
    # savefig(png)
    savefig(png, bbox_inches='tight', pad_inches=-3 / 100, dpi=dpi)
    show()
    figutil.split_lr(png, f1, f2)


if __name__ == '__main__':
    temp = '/home/ac/thesis/zju_thesis/figures/result/cube%d.png'
    temp2 = 'cube/cube%d.png'
    for i, j, k in ((4, 6, '0.04'), (5, 7, '30°')):
        gen_clip_figure_with_color_map(temp2 % i, temp2 % j, temp % i, temp % j, 'cube/res.png', '0', k)

    temp = '/home/ac/thesis/zju_thesis/figures/result/teapot%d.png'
    temp2 = 'teapot/teapot%d.png'
    for i, j, k in ((4, 6, '0.04'), (5, 7, '30°')):
        gen_clip_figure_with_color_map(temp2 % i, temp2 % j, temp % i, temp % j, 'cube/res.png', '0', k)
