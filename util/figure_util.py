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

    temp_file_name = "temp_figure_util.png"
    plt.savefig(temp_file_name)

    if area is not None:
        axes.set_xlim(ori_xlim)
        axes.set_ylim(ori_ylim)

    return Image.open(temp_file_name)


def draw_zoom(fig: Figure, zoomed_area, show_left_low):
    # get gca
    axes = fig.gca()  # type: Axes

    # get zoomed image
    zoomed_image = get_img(fig, zoomed_area)  # type: Image.Image

    # compute extent
    show_size = [size / 200 for size in zoomed_image.size]
    show_size[1] = show_size[1] * axes.get_data_ratio()
    extent = (show_left_low[0], show_left_low[0] + show_size[0], show_left_low[1], show_left_low[1] + show_size[1])

    axes.imshow(zoomed_image, extent=extent, aspect='auto')


if __name__ == '__main__':
    x = np.arange(0, 5, 0.1)
    y = [xx ** 2 for xx in x]
    plt.plot(x, y)
    # plt.gca().set_aspect(1)
    # plt.ylim([0, 10])
    # plt.xlim([0, 10])
    # plt.show()
    draw_zoom(plt.gcf(), (0, 1, 0, 0.5), (0, 5))
    plt.show()
