import numpy as np
from PIL import Image


class TIFFImage:
    def __init__(self, filename, mode=None):
        self.frame = 0
        self.im = Image.open(filename)
        self.mode = mode

        self.width, self.height = self.im.size
        self.stack = self.im.n_frames

        self.chanel = 1
        if self.mode == 'RGB':
            self.chanel = 3

    def size(self):
        return (self.height, self.width)

    def stackSize(self):
        return self.stack

    def getImage(self):
        return self.im

    def getAllFrames(self):
        imArray = np.zeros((self.stack, self.height, self.width))
        for i in range(self.stack):
            self.im.seek(i)
            imArray[i] = np.array(self.im.getchannel(0))

        return imArray

    def getNextFrame(self):
        self.im.seek(self.frame)
        self.frame += 1

        return np.array(self.im.getchannel(0))

    def getFrame(self, ind):
        self.im.seek(ind)
        self.frame = ind + 1

        return np.array(self.im.getchannel(0))


def saveTiff(imArray, filename):
    im_out = [Image.fromarray(i.astype(np.uint8)) for i in imArray]
    im_out[0].save(filename, save_all=True, append_images=im_out[1:])


"""
im = TIFFImage('3-2.tif', "RGB")
imArray = im.getFrame(0)
saveTiff([imArray], "testttt.tif")
"""

"""
size = 256
step = 128

imArray = np.full((size,size), np.arange(0,size,1))
fullArray = np.zeros((step+1,size,size))
fullArray[0] = imArray

for i in range(step+1):
    fullArray[i] = np.roll(imArray, int(i*(size/step)))

im_out = [Image.fromarray(i) for i in fullArray]
im_out[0].save('test.tif', save_all=True, append_images=im_out[1:])
"""
