from matplotlib.backend_bases import MouseButton
import shutil
from os.path import exists
import dill
from MtgDbHelper import *
import matplotlib.pyplot as plt
import numpy as np
from synergyAnalyzer import *
import gc
from GetImage import imageCombo
from CockatriceHelper import *
from LearnedSynergy import *
import cProfile

class CardProject:   

    def __init__(self 
        ,baseLocation='/media/VMShare/' 
        ,ramLocation='/dev/shm/'  
        ,resetDB= False 
        ,resetRawCardMatch = None 
        ,resetIcons = None 
        ,resetInputs = None 
        ,resetModel = None 
        ,resetTrainedCardMatch = None 
        ,namedCards = None 
        ,MatchType=1
        ,simWeight=0.5 
        ,IconicSize = 200 
        ,BasisSize = 125 
        ,fine = False 
        ,label = '9.' 
        ,coresAllowed=7 
        ,deckSeeds=None 
        ):
        
        #manage major objects to backup
        self.baseLocation=baseLocation
        self.ramLocation=ramLocation
        self.resetDB= resetDB
        self.resetRawCardMatch = resetRawCardMatch if resetRawCardMatch else resetDB
        self.resetIcons = resetIcons if resetIcons else resetRawCardMatch
        self.resetInputs = resetInputs if resetInputs else resetIcons
        self.resetModel = resetModel if resetModel else resetInputs
        self.resetTrainedCardMatch = resetTrainedCardMatch if resetTrainedCardMatch else resetDB
        
        
        self.namedCards = namedCards#pass in names list or integer for debug cases

        #options
        self.MatchType=MatchType
        self.simWeight=simWeight
        self.IconicSize = IconicSize
        self.BasisSize = BasisSize
        self.fine = fine
        self.label = label
        self.coresAllowed=coresAllowed

        if deckSeeds:
            self.deckSeeds=deckSeeds
        else:
            self.deckSeeds = [
            ['Garth One-Eye',"Volrath's Laboratory", 'Riptide Replicator', 'Mimic Vat'] \
            , ['Morophon, the Boundless']\
            , ['Reaper King', "Sylvia Brightspear", 'Khorvath Brightflame']\
            , ['Niv-Mizzet Reborn']\
            , ['O-Kagachi, Vengeful Kami']\
            , ['Ramos, Dragon Engine']\
            , ['Scion of the Ur-Dragon']\
            , ['The Ur-Dragon']\
            , ['Kyodai, Soul of Kamigawa']\
            , ['Tiamat']\
            , ['Gadrak, the Crown-Scourge']\
            , ['Lathliss, Dragon Queen']\
            , ['Inferno of the Star Mounts']\
            ]
        self.cardTypeBalance=[45, 80, 80, 91, 99, 100];

        self.cards=None
        self.BasisIndexes=None
        self.CardMatch=None
        self.updatedBelonging=None
        self.deckNames=None

    def debugCost(self):
        cards=self.cards
        cardMatch=self.CardMatch 
        fig, (ax1) = plt.subplots(nrows=1, figsize=(4, 4))
        h = ax1.imshow(cardMatch, extent=[.5, cardMatch.shape[1] + .5, .5, cardMatch.shape[0] + .5], vmin=-1.001,
                    vmax=0.001, aspect='auto',origin='lower')
        plt.colorbar(h)
        ax1.set_title('cardMatch mean:' + str(np.mean(np.mean(cardMatch)))
                            +' max: ' + str(np.max(np.max(cardMatch))))
        plt.tight_layout()


        def on_click(event):
            if event.button is MouseButton.LEFT:
                point = ax1.transData.inverted().transform([event.x, event.y])
                print('x=' + str(point[0]) + ' y=' + str(point[1]))
                x = round(point[0]) - 1
                y = round(point[1]) - 1
                x=max(0,min(x,len(cards.internalSet)-1))
                y=max(0,min(y,len(cards.internalSet)-1))
                pair = [cards.internalSet[x].multiverseid, cards.internalSet[y].multiverseid]
                #breakpoint()
                imageCombo(pair)
                cards.internalSet[x].synergy(cards.internalSet[y],showTable=True, printInfo=True)


        plt.connect('button_press_event', on_click)

        plt.show()

    def createOrLoadData(self):
    
        t = time()
        MtgDbHelper.saveLocation=self.baseLocation
        MtgDbHelper.initDb(self.resetDB)
        elapsed1 = time() - t
        print(f"DB time: {elapsed1} s")

        resetRawCardMatch=self.resetRawCardMatch;
        if self.namedCards:
            numCards=self.namedCards
            if numCards == -2:
                oldDecks = getDeckLists()
                cards = oldDecks[0]
                for deck in range(1, len(oldDecks)):
                    for card in oldDecks[deck]:
                        found = False
                        for check in cards:
                            if check.name == card.name:
                                found = True
                        if not found:
                            cards.append(card)
                cards = CardSet(cards)
            elif numCards == -3:
                cards0 = CardSet(MtgDbHelper.cards.internalSet)
                combos = getKnownCombos(genPairs=False, addGarbage=False)
                cards = []
                for combo in range(1, len(combos)):
                    for card in combos[combo][1]:
                        found = False
                        for check in cards:
                            if check == card:
                                found = True
                        if not found:
                            cards.append(card)
                cards = CardSet(cards0.subsetByNames(cards))
            elif numCards==-4:
                comboCards=[]
                combos = getKnownCombos(genPairs=True, addGarbage=True, namesOnly=True)                
                comboCards=comboCards+MtgDbHelper.cards.findCards(combos)
                cards = MtgDbHelper.cards.subsetByInds(comboCards)
                cards.showTable = False
            elif numCards is int:
                use=range(numCards)
                comboCards=[]
                if(numCards<0):
                    combos = getKnownCombos(genPairs=True, addGarbage=True, namesOnly=True)                
                    comboCards=comboCards+MtgDbHelper.cards.findCards(combos)
                    use=use+comboCards
                    comboCards=list(set(comboCards))
                cards = MtgDbHelper.cards.subsetByInds(use)
                cards.showTable = False
                resetRawCardMatch = True
            else:
                numCards = -1
                names = self.namedCards
                cards = MtgDbHelper.cards.subset(names)
                cards.showTable = False
                cards.printInfo = True
                for card in cards.internalSet:
                    print(card.name)
                    card.ParseText(True)
                    for e in range(len(card.Events)):
                        print(str(card.Triggers[e]) + ":" + str(card.Events[e]))
                resetRawCardMatch=True
        else:
            cards = CardSet(MtgDbHelper.cards.internalSet)
            cards.showTable = False
            numCards='D'
        self.cards=cards

        fname0 = 'CardInfo.' + self.label + str(numCards) + str(self.fine) 
        
        fname = fname0 + '.Weighted' + str(self.simWeight)+'.pkl'
        backupLoc = self.baseLocation+ fname
        backupLoc0 = self.ramLocation+ fname 
        if exists(backupLoc):
            shutil.copyfile(backupLoc, backupLoc0)
        if not resetRawCardMatch and exists(backupLoc0):
            with open(backupLoc0, 'rb') as file:
                rawCardMatch = dill.load(file)
        else:        
            fname= fname0+ '.Synergy.pkl'
            backupLoc = self.baseLocation+fname
            backupLoc0 = self.ramLocation+ fname
            if exists(backupLoc):
                shutil.copyfile(backupLoc, backupLoc0)
            if not resetRawCardMatch and exists(backupLoc0):
                #ideally this should be done after similarity 
                with open(backupLoc0, 'rb') as file:
                    synergy = dill.load(file)
            else:
                t = time()
                cards.fine = self.fine
                cards.synNotSim = True
                cards.mxPrcs = self.coresAllowed
                synergy = cards.synergy3()
                elapsed2 = time() - t
                full = len(MtgDbHelper.cards.internalSet) ** 2 / len(cards.internalSet) ** 2 / 60 / 60
                print(f"rawCardMatch for {len(cards.internalSet)}^2 {elapsed2} s expect {elapsed2 * full} hours")
                with open(backupLoc, "wb") as f:
                    dill.dump(synergy, f)
                gc.collect()

            
            fname= fname0 + '.Similarity.pkl'
            backupLoc = self.baseLocation+ fname
            backupLoc0 = self.ramLocation+ fname        
            if exists(backupLoc):
                shutil.copyfile(backupLoc, backupLoc0)
            if not resetRawCardMatch and exists(backupLoc0):
                with open(backupLoc0, 'rb') as file:
                    similarity = dill.load(file)
            else:
                t = time()
                cards.fine = self.fine
                cards.synNotSim = False
                similarity = cards.synergy3()
                elapsed2 = time() - t
                full = len(MtgDbHelper.cards.internalSet) ** 2 / len(cards.internalSet) ** 2 / 60 / 60
                print(f"rawCardMatch for {len(cards.internalSet)}^2 {elapsed2} s expect {elapsed2 * full} hours")
                with open(backupLoc, "wb") as f:
                    dill.dump(similarity, f)
                gc.collect()

            rawCardMatch=(1-self.simWeight)*synergy+self.simWeight*similarity
            with open(backupLoc, "wb") as f:
                dill.dump(rawCardMatch, f)
            
            del synergy 
            del similarity
            gc.collect()

        
        if numCards == -1:#helpful debug routines but skip the training
            self.CardMatch=rawCardMatch;
            self.debugCost()
            self.updatedBelonging=None

            location = '/media/VMShare/OldDecks/Dragons/'
            from os import listdir
            from os.path import isfile, join
            self.deckNames=[f for f in listdir(location) if isfile(join(location, f))]
            return

        
        # looking for a distance function... rawCardMatch as the base so I don't need to use Levenstein on raw text again
    
        if self.MatchType==0:
            cardMatch=rawCardMatch;
            del rawCardMatch
            deckBase=backupLoc.replace('.pkl','.Deck.')
        else:    
            
            iconLoc = backupLoc.replace('.pkl',  '.IS' + str(self.IconicSize)+'.pkl')
            inputsLoc = backupLoc.replace('.pkl', '.TrainingSetup'+str(self.BasisSize)+'inputs.pkl')
            TrainedCardMatchLoc = inputsLoc.replace('.pkl', '.TrainedCardMatch.pkl')
            deckBase=TrainedCardMatchLoc.replace('.pkl','.Deck.')
            if not self.resetTrainedCardMatch and exists(TrainedCardMatchLoc):
                # rawCardMatch = dill.load_session(backupLoc0)
                with open(TrainedCardMatchLoc, 'rb') as file:
                    trainedCardMatch = dill.load(file)
            else:
                if not self.resetInputs and exists(inputsLoc):
                    with open(inputsLoc, 'rb') as file:
                        items = dill.load(file)
                    X = items['X']
                    V = items['V']
                    combos = items['combos']
                    iconicCards = items['iconicCards']
                    cardDesciptions = items['cardDesciptions']
                    BasisCards = items['BasisCards']
                else:

                    if not self.resetIcons and exists(iconLoc):
                        with open(iconLoc, 'rb') as file:
                            iconicCards = dill.load(file)
                    else:

                        cardDist = np.corrcoef(rawCardMatch)  # np.cov(rawCardMatch)
                        np.nan_to_num(cardDist, copy=False, nan=0)
                        del rawCardMatch
                        iconicCards = findBasis3(cardDist, self.IconicSize)
                        with open(iconLoc, "wb") as f:
                            dill.dump(iconicCards, f)

                    iconicCards = iconicCards[0:self.BasisSize]
                    BasisCards = CardSet([cards.internalSet[i] for i in iconicCards])
                    if exists(backupLoc):
                        shutil.copyfile(backupLoc, backupLoc0)
                    with open(backupLoc0, 'rb') as file:
                        rawCardMatch = dill.load(file)
                    cardDesciptions = rawCardMatch[iconicCards, :]
                    del rawCardMatch

                    #combos = getKnownCombos(genPairs=True, addGarbage=True)
                    combos = getKnownCombosAndDeck(genPairs=True, addGarbage=True)
                    icons = len(iconicCards)
                    icons2 = icons * 2
                    X = np.zeros([2 * len(combos), icons2])
                    V = np.zeros([2 * len(combos), 1])
                    scale=0.125
                    for c in range(len(combos)):
                        if c % 10000 == 0:
                            print('making model loop ' + str(c) + ' of ' + str(len(combos)))
                        comboInds = cards.findCards(combos[c][1])
                        X[c, 0:icons] = cardDesciptions[:, comboInds[0]]
                        X[c, icons:icons2] = cardDesciptions[:, comboInds[1]]
                        V[c, 0] = combos[c][0] ** scale
                        X[c + len(combos), 0:icons] = cardDesciptions[:, comboInds[1]]
                        X[c + len(combos), icons:icons2] = cardDesciptions[:, comboInds[0]]
                        V[c + len(combos), 0] = combos[c][0] ** scale
                    items = dict()
                    items['X'] = X
                    items['V'] = V
                    items['combos'] = combos
                    items['iconicCards'] = iconicCards
                    items['cardDesciptions'] = cardDesciptions
                    items['BasisCards'] = BasisCards
                    with open(inputsLoc, "wb") as f:
                        dill.dump(items, f)

                    icons = len(iconicCards)
                    icons2 = icons * 2
                    LS = LearnedSynergy([icons2, 1])
                    LS.trainModel(X, V)
                    N = len(cards.internalSet)
                    trainedCardMatch = np.zeros([N, N])
                    for x in range(N):
                        if x % round(N / 10) == 0:
                            print('using model loop ' + str(x) + ' of ' + str(N))
                        X2 = np.zeros([N, icons2])
                        for y in range(N):
                            X2[y, 0:icons] = cardDesciptions[:, x]
                            X2[y, icons:icons2] = cardDesciptions[:, y]
                        trainedCardMatch[x, :] = LS.useModel(X2)[:, 0]
                    with open(TrainedCardMatchLoc, "wb") as f:
                        dill.dump(trainedCardMatch, f)

            cardMatch = trainedCardMatch + trainedCardMatch.transpose()
            del trainedCardMatch


        with open(iconLoc, 'rb') as file:
            iconicCards = dill.load(file)

        self.BasisIndexes=iconicCards[0:self.BasisSize]

        self.CardMatch=cardMatch

        commanders=[];
        for dk in self.deckSeeds:
            commanders.append(dk[0])

        commanderIndexes = cards.findCards(commanders)
        commanderPoolsByIdentity=cards.CardPoolByCommander(commanders)
        sourceInfo=cards.sources()
        belonging = np.zeros([cardMatch.shape[0], 1])
        for ci in range(len(commanderIndexes)):
            inds=cards.findCards(self.deckSeeds[ci])
            i=0
            for ind in inds:
                if ind>-1:
                    belonging[ind] = ci + 1
                else:
                    print('could not find '+self.deckSeeds[ci][i])
                i=i+1
        
        classes=cards.classes()
        comanderClasses=classes[commanderIndexes]
        updatedBelonging = findNetworks2(classes,comanderClasses,commanderPoolsByIdentity,\
            cardMatch, belonging, sourceInfo, self.cardTypeBalance )

        d=0
        self.deckNames=[]
        for deck in updatedBelonging:
            if d<len(commanders):
                deckLocation=deckBase+commanders[d]+".txt"
            else:
                deckLocation=deckBase+"other"+str(d)+".txt"
            self.deckNames.append(deckLocation)
            with open(deckLocation, 'w') as f:
                print(" ")
                multiCombo = []
                for c in range(len(deck)):
                        card =deck[c]
                        f.write(cards.internalSet[card].name+"\r\n")
                        if cards.internalSet[card].multiverseid:
                            multiCombo = [cards.internalSet[card].multiverseid]
                            #print(str(c) +" "+cards.internalSet[card].name)
                            print(cards.internalSet[card].name)
                        else:
                            print('can''t find ' + cards.internalSet[card].name)
                        #imageCombo(multiCombo)
                    #imageCombo(['0'])
            f.close()
            d=d+1            
        self.updatedBelonging=updatedBelonging


if __name__ == '__main__':
    names = ['The Mirari Conjecture', 'Power Conduit', 'Time Stretch'
        , 'Scion of the Ur-Dragon', 'Teneb, the Harvester'
        , 'Dragonsoul Knight', 'Bogardan Dragonheart'
        , 'Lathliss, Dragon Queen']
    names0 = ['The Mirari Conjecture', 'Power Conduit', 'Time Stretch']
    names0 = ['Scion of the Ur-Dragon', 'Teneb, the Harvester']
    cp=CardProject(namedCards=None)
    cp.createOrLoadData()
