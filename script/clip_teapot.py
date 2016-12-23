from PIL import Image, ImageChops
import itertools
import sys


def crop_teapot(file_path, output_file_name=None):
    img = Image.open(file_path)  # type: Image.Image
    w, h = img.size
    crop = img.crop((0, 100, w, h - 230))
    if output_file_name is not None:
        # crop.save('/home/ac/thesis/zju_thesis/figures/result/' + file_path)
        crop.save(file_path)


def crop_cube(file_path, output_file_name=None):
    img = Image.open(file_path)  # type: Image.Image
    w, h = img.size
    crop = img.crop((0, 70, w, h - 60))
    if output_file_name is not None:
        # crop.save('/home/ac/thesis/zju_thesis/figures/result/' + file_path)
        crop.save(file_path)

if __name__ == '__main__':
    for i in range(1, 8):
        crop_cube('cube/cube%d.png' % i, 'cube/cube%d.png' % i)

    for i in range(1, 8):
        crop_teapot('teapot/teapot%d.png' % i, 'teapot/teapot%d.png' % i)
