from PIL import Image, ImageChops
import itertools
import sys


def crop_teapot(file_path):
    img = Image.open('teapot/' + file_path)  # type: Image.Image
    w, h = img.size
    img.crop((0, 100, w, h - 230)).save('/home/ac/thesis/zju_thesis/figures/result/' + file_path)


def crop_cube(file_path):
    img = Image.open('cube/' + file_path)  # type: Image.Image
    w, h = img.size
    img.crop((0, 70, w, h - 60)).save('/home/ac/thesis/zju_thesis/figures/result/' + file_path)


if __name__ == '__main__':
    for i in range(1, 8):
        crop_cube('cube%d.png' % i)
