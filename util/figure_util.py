from matplotlib.figure import Figure, Axes
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


def get_img(fig: Figure, area=None):
    axes = fig.gca()  # type Axes
    ori_xlim, ori_ylim = None, None
    if area is not None:
        ori_xlim, ori_ylim = axes.get_xlim(), axes.get_ylim()
        temp_xlim = (area[0], area[1])
        temp_ylim = (area[2], area[3])
        axes.set_xlim(temp_xlim)
        axes.set_ylim(temp_ylim)

    # axes.axis('off')
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)
    temp_file_name = "temp_figure_util.png"
    fig.savefig(temp_file_name, pad_inches=0, bbox_inches='tight')
    # axes.axis('on')
    axes.get_xaxis().set_visible(True)
    axes.get_yaxis().set_visible(True)

    if area is not None:
        axes.set_xlim(ori_xlim)
        axes.set_ylim(ori_ylim)

    return Image.open(temp_file_name)


def draw_zoom(fig: Figure, zoomed_area, show_left_low, show_x_length):
    # get gca
    axes = fig.gca()  # type: Axes
    axes.set_aspect(1 / axes.get_data_ratio())

    # get zoomed image
    zoomed_image = get_img(fig, zoomed_area)  # type: Image.Image

    # compute extent
    scale = show_x_length / zoomed_image.size[0]
    show_size = [size * scale for size in zoomed_image.size]
    show_size[1] = show_size[0] * (zoomed_area[2] - zoomed_area[3]) / (zoomed_area[0] - zoomed_area[1])
    # show_size[1] = show_size[1] * axes.get_data_ratio()
    extent = (show_left_low[0], show_left_low[0] + show_size[0], show_left_low[1], show_left_low[1] + show_size[1])

    # draw image
    axes.imshow(zoomed_image, extent=extent, aspect='auto')

    # draw two lines
    def left_right_bottom_top_2_left_top_point_right_bottom_point(left_right_bottom_top):
        return [left_right_bottom_top[0], left_right_bottom_top[3]], \
               [left_right_bottom_top[1], left_right_bottom_top[2]]

    ori_left_top_point, ori_right_bottom_point = left_right_bottom_top_2_left_top_point_right_bottom_point(zoomed_area)
    des_left_top_point, des_right_bottom_point = left_right_bottom_top_2_left_top_point_right_bottom_point(extent)
    axes.plot([ori_left_top_point[0], des_left_top_point[0]], [ori_left_top_point[1], des_left_top_point[1]], '-k')
    axes.plot([ori_right_bottom_point[0], des_right_bottom_point[0]],
              [ori_right_bottom_point[1], des_right_bottom_point[1]], '-k')

    # draw two react
    def left_right_bottom_top_2_xs_ys(lrbt):
        return [lrbt[0], lrbt[0], lrbt[1], lrbt[1], lrbt[0]], [lrbt[2], lrbt[3], lrbt[3], lrbt[2], lrbt[2]]

    axes.plot(*left_right_bottom_top_2_xs_ys(zoomed_area), '-k')
    axes.plot(*left_right_bottom_top_2_xs_ys(extent), '-k')


def split_lr(file_path: str):
    dot_position = file_path.rfind('.')
    left_file_path = file_path[:dot_position] + '0' + file_path[dot_position:]
    right_file_path = file_path[:dot_position] + '1' + file_path[dot_position:]
    im = Image.open(file_path)  # type: Image.Image
    width, height = im.size
    im.crop((0, 0, int(width / 2), height)) \
        .save(left_file_path)
    im.crop((int(width / 2), 0, width, height)) \
        .save(right_file_path)


if __name__ == '__main__':
    # x = np.arange(0, 6.0, 0.1)
    # y = [xx ** 2 for xx in x]
    # plt.plot(x, y)
    # print(plt.gca().get_data_ratio())
    # plt.gca().set_aspect(1 / plt.gca().get_data_ratio())
    # plt.gca().set_xlim([0, 1])
    # plt.gca().set_ylim([0, 0.5])
    # plt.ylim([0, 10])
    # plt.xlim([0, 10])
    # plt.show()
    # draw_zoom(plt.gcf(), (0, 1, 0, 0.5), (1, 5), 3)
    # plt.show()

    png = '/home/ac/thesis/zju_thesis/figures/clip/clip_compare.png'
    splitLR(png)
