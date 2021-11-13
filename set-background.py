#!/usr/bin/env python3

from argh import *
import os
import cv2
import numpy as np
import json
import colorgram
from colour import Color
from shutil import copyfile
from PIL import Image, ImageEnhance

def isbright(imagePath, dim=10, thresh=0.5):
    # Load image from given path
    image = cv2.imread(imagePath)
    # Resize image to 10x10
    image = cv2.resize(image, (dim, dim))
    # Convert color space to LAB format and extract L channel
    L, A, B = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2LAB))
    # Normalize L channel by dividing all pixel values with maximum pixel value
    L = L/np.max(L)
    # Return True if mean is greater than thresh else False
    return np.mean(L) > thresh

def changebrightness(imagePath, factor: int=1):
    image = Image.open(imagePath)
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

def loadImage(imagePath):
    return Image.open(imagePath)

def generatepalette(path, reverse: bool = False, accuracy = 10):
    paletteraw = colorgram.extract(path, accuracy)
    paletteraw.sort(key=lambda c: c.hsl.l)
    palette = [Color(rgb=(c.rgb[0]/255, c.rgb[1]/255, c.rgb[2]/255)) for c in paletteraw]

    if palette[1].get_luminance() > 0.1:
        palette[1].set_luminance(0.1)

    if reverse:
        palette = palette[::-1]

    palettesum = {
        'primary': palette[(len(palette) - 1) // 2].hex,
        'background': palette[1].hex,
        'foreground': palette[len(palette) - 1].hex,
        'high': palette[0].hex,
        'accent': palette[2].hex
    }

    return dict({
        'sum': palettesum,
        'raw': paletteraw,
        'all': palette
    })


def setbackground(path : 'path to the background image',
                  darkfolder : 'where to save the dark version of your bg' = os.path.expanduser('~/.config/dark-mode.d'),
                  lightfolder : 'set where to save the light version of your bg' = os.path.expanduser('~/.config/light-mode.d')):
    completepath, ext = os.path.splitext(path)

    if not os.path.exists(darkfolder):
        print(' [*] Creating dark-theme folder at ' + darkfolder)
        os.makedirs(darkfolder)
    if not os.path.exists(lightfolder):
        print(' [*] Creating light-theme folder at ' + lightfolder)
        os.makedirs(lightfolder)

    darkpath = os.path.join(darkfolder, 'dark.png')
    lightpath = os.path.join(lightfolder, 'light.png')

    if isbright(path):
        print(' [*] The image selected is bright')
        print(' [*] Creating a darker version of it')
        changebrightness(path, 0.6).save(darkpath)
        print(' [*] Image created and saved at ' + darkpath)
        print(' [*] Copying light-mode image to ' + lightpath)
        loadImage(path).save(lightpath)

        os.system('nitrogen --set-auto ' + lightpath)
        print(' [*] Chosen wallpaper has been set as current background')
    else:
        print(' [*] The image selected is dark')
        print(' [*] Creating a lighter version of it')
        changebrightness(path, 1.4).save(lightpath)
        print(' [*] Image created and saved at ' + lightpath)
        print(' [*] Copying light-mode image to ' + darkpath)
        loadImage(path).save(darkpath)

        os.system('nitrogen --set-auto ' + darkpath)
        print(' [*] Chosen wallpaper has been set as current background')

    with open(os.path.join(darkfolder, 'palette.json'), 'w') as file:
        file.write(json.dumps(generatepalette(path)['sum']))

    with open(os.path.join(lightfolder, 'palette.json'), 'w') as file:
        file.write(json.dumps(generatepalette(path, True)['sum']))


if __name__ == '__main__':
    dispatch_command(setbackground)
