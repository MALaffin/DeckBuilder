import numpy as np
import tensorflow as tf
from synergyAnalyzer import plot
import matplotlib.pyplot as plt
from CockatriceHelper import *
import dill

if False:
    if not MtgDbHelper.cards:
        MtgDbHelper.initDb(False)
    combos = getKnownCombos(addGarbage=False, genPairs=False, namesOnly=False)
    ind=0;
    for combo in combos:
        ind=ind+1
        CD=CockatriceDeck()
        CD.setByInds(MtgDbHelper.cards.findCards(combo[1]))
        CD.saveText('/media/VMShare/TrainingInfo/Combos/combo'+str(ind)+'.txt')

if True:
    deckAndCombos=[];
    location = '/media/VMShare/TrainingInfo/Decks/'
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(location) if isfile(join(location, f))]
    decks = []
    for file in onlyfiles:
        CD=CockatriceDeck()
        CD.load(location + file)
        deckAndCombos=deckAndCombos+CD.cardSetIndexes
        decks.append(CD.cardSetIndexes)
    
    location = '/media/VMShare/TrainingInfo/Combos/'
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(location) if isfile(join(location, f))]
    combos = []
    for file in onlyfiles:
        CD=CockatriceDeck()
        CD.loadText(location + file)
        deckAndCombos=deckAndCombos+CD.cardSetIndexes
        combos.append(CD.cardSetIndexes)


    iconLoc0 = '/media/VMShare/Version17/CardInfo.DFalse.Merged.IS-1.pkl'
    with open(iconLoc0, 'rb') as file:
        iconInfo = dill.load(file)
        file.close()
    iconicCards=iconInfo[0]
    location = '/media/VMShare/TrainingInfo/Chaff/chaff0.txt'
    chaff = []
    for ind in iconicCards:
        if not ind in deckAndCombos:
            chaff.append(ind)
    CD=CockatriceDeck()
    CD.setByInds(chaff)
    CD.saveText(location)



if False:
    #about 700 basis cards, sizein~2*(700*3)=4200 for card pairs of basis vectors of size 3
    #expect ~1000 cards from a pool of ~10000 about 10% of the combos are relevent
    #maybe as many as 700*700*0.1~=50000 relevent good groups
    #the pair input structure implies a symetric training scheme on the input layer would be best; 
    # trust that the basis made that layer
    #4200 values for defining which basis each card belongs to 
    #50000/4200~need about 12 nodes after input to mix enough; maybe want ~4x few to control granualrity of underlying distribution
    #try 50
    sizeIn=(4200,1)
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=sizeIn),
        tf.keras.layers.Dense(50, activation='sigmoid'),
        tf.keras.layers.Dense(1, activation='linear')
    ])
    tf.random.set_seed(0)
    model.compile(optimizer='adam',
                    loss='mean_squared_error',  # self.error,#
                    metrics=['mean_absolute_error']
                    )
    modelLoc="temp"
    model.save(modelLoc)

    model2=tf.keras.models.load_model("temp")



