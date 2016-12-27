import PIL.Image as Image

if __name__ == '__main__':
    img = Image.open('/home/ac/thesis/zju_thesis/figures/sffd/sffd_0.png')  # type: Image.Image
    background = Image.new(img.mode, (400, 281), (255, 255, 255, 255))
    background.paste(img, (100, 0))
    background.save('/home/ac/thesis/zju_thesis/figures/sffd/sffd_0.png')
