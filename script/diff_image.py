from PIL import Image, ImageChops
import itertools
import sys
import matplotlib.pyplot as plt

sys.path.append('./')
import multi_sampling


def draw_figure(distribution: dict):
    # print(distribution.keys())
    # print(distribution.values())
    plt.plot(list(distribution.keys())[1:], list(distribution.values())[1:])
    plt.show()


def diff(img1_file_path: str, img2_file_path: str):
    img1 = Image.open(img1_file_path)  # type: Image.Image
    img2 = Image.open(img2_file_path)  # type: Image.Image

    new_img = Image.new(img1.mode, img1.size)
    pixel_number = 0
    can_not_diff_point_number = 0
    total_rgb_diff = (0, 0, 0, 0)
    max_rgb_diff = (0, 0, 0, 0)
    distribution = {}
    for i, j in itertools.product(*[range(s) for s in img1.size]):
        p1 = img1.getpixel((i, j))
        p2 = img2.getpixel((i, j))

        if p1 == p2 == (255, 255, 255, 255):
            continue

        pixel_number += 1
        rgb_diff = tuple(abs(x - y) for x, y in zip(p1, p2))
        if rgb_diff[0] > max_rgb_diff[0]:
            max_rgb_diff = rgb_diff

        key = rgb_diff[0]
        if key in distribution:
            distribution[key] += 1
        else:
            distribution[key] = 1

        if key <= 5:
            can_not_diff_point_number += 1

        total_rgb_diff = tuple(x + y for x, y in zip(total_rgb_diff, rgb_diff))

        result_red = sum(rgb_diff)
        result_red = int(result_red ** 0.25) * 64
        if result_red == 0:
            new_p = (255,) * 4
        else:
            new_p = (int(255 * (result_red / 192 / 2 + 0.5)), 0, 0, 255)
        new_img.putpixel((i, j), new_p)

    print('average rgb diff:', tuple(x / pixel_number for x in total_rgb_diff))
    print('pixel number:', pixel_number)
    print('max rgb diff', max_rgb_diff)
    print('<5 point percent', can_not_diff_point_number / pixel_number)

    draw_figure(distribution)


    # color = Image.open('colormap.png')  # type: Image.Image
    # color_width = color.size[0] - 1
    # for i, j in itertools.product(*[range(s) for s in img1.size]):
    #     p = new_img.getpixel((i, j))[0] / max_p
    #     print(p)
    #     new_img.putpixel((i, j), color.getpixel((int(p * color_width), 0)))

    # multi_sampling.multi_sampling2_helper(new_img).save(
    #     '/home/ac/thesis/zju_thesis/figures/result/renderer_effect4.png')


if __name__ == '__main__':
    diff('renderer_effect/renderer_effect3.png', 'renderer_effect/renderer_effect2.png')
