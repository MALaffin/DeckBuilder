import matplotlib.pyplot as plt
import requests
import numpy as np
from matplotlib import image
from os.path import exists
from os import makedirs


def getImageLocByMultiverseId(multiverseid):
    image_url = 'https://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=' + multiverseid + '&type=card'
    imDir='/media/VMShare/Images/';
    if not exists(imDir):
        makedirs(imDir)
    imLoc = imDir + multiverseid + '.jpg'
    if not exists(imLoc):
        req = requests.get(image_url,verify=False).content
        with open(imLoc, 'wb') as handler:
            handler.write(req)
    return imLoc

def getImageByMultiverseId(multiverseid):
    imLoc = getImageLocByMultiverseId(multiverseid)
    img = image.imread(imLoc)
    return img


def imageCombo(multiIds):
    figId = str(multiIds)
    fig, ax = plt.subplots(nrows=1, ncols=len(multiIds), figsize=(5*len(multiIds), 7), num=figId)
    for ind in range(len(multiIds)):
        title = str(multiIds[ind])
        data = getImageByMultiverseId(multiIds[ind])
        if len(multiIds) == 1:
            h = ax.imshow(data, aspect='auto')
            ax.set_title(title)
        else:
            h = ax[ind].imshow(data, aspect='auto')
            ax[ind].set_title(title)
        plt.tight_layout()
    plt.show(block=True)
    print(multiIds)
