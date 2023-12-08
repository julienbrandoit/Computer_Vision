import TiffManager as Tm
import numpy as np
import random as rd
import time

start_time = time.time()
voisinInit = [[-1, -1], [-1, 0], [-1, 1],
                  [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]

def print_time():
    global start_time
    new_time = time.time()
    print(new_time - start_time)
    start_time = new_time

def getNeighbor(i, j, h, w):
    if i == 0 or i == h-1 or j == 0 or j == w-1:
        voisin = []
        for k in voisinInit:
            if 0 <= i + k[0] < h and 0 <= j + k[1] < w:
                voisin.append(k)

        return voisin

    return voisinInit

def Init_ViBe(im, N):
    h, w = len(im), len(im[0])
    samples = np.empty((h, w, N))

    for i in range(h):
        for j in range(w):
            voisin = getNeighbor(i, j, h, w)
            samplesCoord = rd.choices(voisin, k=N)

            for ind, k in enumerate(samplesCoord):
                samples[i][j][ind] = im[i + k[0]][j + k[1]]

    return samples


def isBackground(pixel, sample, R, Vmin):
    for i in sample:
        if np.abs(pixel - i) < R:
            Vmin -= 1

        if Vmin == 0:
            return True

    return False

def SegAndUpdate(im, samples, N, R, Vmin, phi):
    h, w = len(im), len(im[0])
    mask = np.zeros(im.shape)

    for i in range(h):
        for j in range(w):
            if isBackground(im[i][j], samples[i][j], R, Vmin):
                test_up = rd.randint(0, phi-1)
                if test_up == 0:
                    update = rd.randint(0, N-1)
                    samples[i][j][update] = im[i][j]

                test_dif = rd.randint(0, phi-1)
                if test_dif == 0:
                    voisin = getNeighbor(i, j, h, w)
                    offset = rd.choice(voisin)
                    update = rd.randint(0, N-1)
                    samples[i + offset[0]][j+ offset[1]][update] = im[i][j]
            else:
                mask[i][j] = 255

            

    return mask


def ViBe(listImage, Nsample=20, R=20, Vmin=2, phi=16):
    samples = Init_ViBe(listImage[0], Nsample)
    print("Initialisation terminée")
    print_time()

    segMap = np.empty(listImage.shape)
    for ind, im in enumerate(listImage):
        if ind == 50:
            phi = 16

        print(f"image : {ind+1}")
        print_time()
        segMap[ind] = SegAndUpdate(im, samples, Nsample, R, Vmin, phi)

    return segMap


im = Tm.TIFFImage('3-2.tif')
imArray = im.getAllFrames()
print("Load terminé")
print_time()
segMap = ViBe(imArray, phi=1)
Tm.saveTiff(segMap, 'çamarchestp2.tif')
