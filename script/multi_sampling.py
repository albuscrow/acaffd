from PIL import Image
import functools as fun
import itertools as iter


def multi_sampling2_helper(img):
    width, height = img.size
    new_img = Image.new(img.mode, img.size)

    def kernel2(i, j):
        offset = [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
        positions = [tuple(xy + ori for xy, ori in zip(offset_element, [i, j])) for offset_element in offset]
        pixels = [img.getpixel(p) for p in positions if 0 <= p[0] < width and 0 <= p[1] < height]

        def foo(p, r):
            return tuple(x + y for x, y in zip(p, r))

        return tuple(int(x / len(pixels)) for x in fun.reduce(foo, pixels, (0, 0, 0, 0)))

    for i, j in iter.product(*[range(xy) for xy in new_img.size]):
        xy = (i, j)
        new_pixel = kernel2(i, j)
        new_img.putpixel(xy, new_pixel)
    return new_img


def multi_sampling2(file_name: str):
    dot_position = file_name.rfind('.')
    new_file_name = file_name[:dot_position] + '_sampled2' + file_name[dot_position:]
    img = Image.open(file_name)  # type: Image.Image
    multi_sampling2_helper(img).save(new_file_name)


def multi_sampling_help(img):
    width, height = img.size
    new_img = Image.new(img.mode, tuple(int(xy / 2) for xy in img.size))

    def kernel(i, j):
        indices = [(i * 2, j * 2), (i * 2 + 1, j * 2), (i * 2, j * 2 + 1), (i * 2 + 1, j * 2 + 1)]
        pixels = [img.getpixel(p) for p in indices]

        def foo(p, r):
            return tuple(x + y for x, y in zip(p, r))

        return tuple(int(x / len(pixels)) for x in fun.reduce(foo, pixels, (0, 0, 0, 0)))

    for i, j in iter.product(*[range(xy) for xy in new_img.size]):
        xy = (i, j)
        new_pixel = kernel(i, j)
        new_img.putpixel(xy, new_pixel)

    return new_img


def multi_sampling(input):
    dot_position = input.rfind('.')
    new_file_name = input[:dot_position] + '_sampled2' + input[dot_position:]
    img = Image.open(input)  # type: Image.Image
    multi_sampling_help(img).save(new_file_name)


if __name__ == '__main__':
    multi_sampling('/home/ac/thesis/zju_thesis/figures/result/renderer_effect4.png')
