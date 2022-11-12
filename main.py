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

if __name__ == '__main__':

    # LearnedSynergy.selfTest()

    # Decks=getDeckLists()

    resetDB= False#True#
    resetSynergy = resetDB # True # 
    resetIcons = resetSynergy  # True #
    resetInputs = resetIcons  # True #
    resetModel = resetInputs  # True #
    resetTrainedSynergy = resetModel  # True #
    numCards = None # -1 # 250 #   -4 # -3  # 
    simWeight=0.8
    runTrain=False
    IconicSize = 200
    BasisSize = 125
    fine = False
    label = '8.'

    coresAllowed=7
    
    t = time()
    MtgDbHelper.initDb(resetDB)
    elapsed1 = time() - t
    print(f"DB time: {elapsed1} s")

    if numCards:
        if numCards == -1:
            names = ['The Mirari Conjecture', 'Power Conduit', 'Time Stretch'
                , 'Scion of the Ur-Dragon', 'Teneb, the Harvester'
                , 'Dragonsoul Knight', 'Bogardan Dragonheart'
                , 'Lathliss, Dragon Queen']
            names0 = ['The Mirari Conjecture', 'Power Conduit', 'Time Stretch']
            names0 = ['Scion of the Ur-Dragon', 'Teneb, the Harvester']
            cards = MtgDbHelper.cards.subset(names)
            cards.showTable = False
            cards.printInfo = True
            for card in cards.internalSet:
                print(card.name)
                card.ParseText(True)
                for e in range(len(card.Events)):
                    print(str(card.Triggers[e]) + ":" + str(card.Events[e]))
            resetSynergy=True
        elif numCards == -2:
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
        else:
            use=range(numCards)
            comboCards=[]
            if(numCards<0):
                combos = getKnownCombos(genPairs=True, addGarbage=True, namesOnly=True)                
                comboCards=comboCards+MtgDbHelper.cards.findCards(combos)
                use=use+comboCards
                comboCards=list(set(comboCards))
            cards = MtgDbHelper.cards.subsetByInds(use)
            cards.showTable = False
            resetSynergy = True
    else:
        cards = CardSet(MtgDbHelper.cards.internalSet)
        cards.showTable = False

    checkWords = False
    if checkWords:
        texts = []
        for card in cards.internalSet:
            for e in card.Events:
                texts = texts + e
        for card in cards.internalSet:
            for t in card.Triggers:
                texts = texts + t
        tmp = list(set(texts))
        print('post parse words ' + str(len(tmp)))

    fname = label + str(numCards) + str(fine) + '.pkl'
    backupLoc = '/media/VMShare/SQLTest.' + fname
    backupLoc0 = '/dev/shm/SQLTest.' + fname
    if exists(backupLoc):
        shutil.copyfile(backupLoc, backupLoc0)
    if not resetSynergy and exists(backupLoc0):
        #ideally this should be done after synergy2 
        with open(backupLoc0, 'rb') as file:
            synergy1 = dill.load(file)
    else:
        t = time()
        cards.fine = fine
        cards.synNotSim = True
        cards.mxPrcs = coresAllowed
        synergy1 = cards.synergy3()
        elapsed2 = time() - t
        full = len(MtgDbHelper.cards.internalSet) ** 2 / len(cards.internalSet) ** 2 / 60 / 60
        print(f"synergy for {len(cards.internalSet)}^2 {elapsed2} s expect {elapsed2 * full} hours")
        with open(backupLoc, "wb") as f:
            dill.dump(synergy1, f)
        gc.collect()

    fname = label + str(numCards) + str(fine) + '.Similarity.pkl'
    backupLoc = '/media/VMShare/SQLTest.' + fname
    backupLoc0 = '/dev/shm/SQLTest.' + fname
    if exists(backupLoc):
        shutil.copyfile(backupLoc, backupLoc0)
    if not resetSynergy and exists(backupLoc0):
        with open(backupLoc0, 'rb') as file:
            synergy2 = dill.load(file)
    else:
        t = time()
        cards.fine = fine
        cards.synNotSim = False
        synergy2 = cards.synergy3()
        elapsed2 = time() - t
        full = len(MtgDbHelper.cards.internalSet) ** 2 / len(cards.internalSet) ** 2 / 60 / 60
        print(f"synergy for {len(cards.internalSet)}^2 {elapsed2} s expect {elapsed2 * full} hours")
        with open(backupLoc, "wb") as f:
            dill.dump(synergy2, f)
        gc.collect()


    fname = label + str(numCards) + str(fine) + '.Weighted'+str(simWeight)+'.pkl'
    backupLoc = '/media/VMShare/SQLTest.' + fname
    backupLoc0 = '/dev/shm/SQLTest.' + fname
    if exists(backupLoc):
        shutil.copyfile(backupLoc, backupLoc0)
    if not resetSynergy and exists(backupLoc0):
        with open(backupLoc0, 'rb') as file:
            synergy = dill.load(file)
    else:
        synergy=(1-2*simWeight)*synergy1+2*simWeight*synergy2
        with open(backupLoc, "wb") as f:
            dill.dump(synergy, f)
        gc.collect()
    del synergy1 
    del synergy2
    gc.collect()

    showSynergy = False
    if showSynergy or numCards == -1:
        fig, (ax1) = plt.subplots(nrows=1, figsize=(4, 4))
        h = ax1.imshow(synergy, extent=[.5, synergy.shape[1] + .5, .5, synergy.shape[0] + .5], vmin=-1.001,
                       vmax=0.001, aspect='auto',origin='lower')
        plt.colorbar(h)
        ax1.set_title('synergy mean:' + str(np.mean(np.mean(synergy)))
                            +' max: ' + str(np.max(np.max(synergy))))
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
        exit(0)

    # # loops not strong enough to find combos
    # combos = findLoops3(synergy,numcombos=3)  # passes like C#
    # for combo in combos:
    #     print(combo)
    #     multiCombo = []
    #     for loc0 in combo:
    #         loc = loc0
    #         # loc = iconicCards[loc0]
    #         if cards.internalSet[loc].multiverseid:
    #             multiCombo = multiCombo + [cards.internalSet[loc].multiverseid]
    #             print(cards.internalSet[loc].name)
    #         else:
    #             print('can''t find ' + cards.internalSet[loc].name)
    #     if len(combo) > 0:
    #         imageCombo(multiCombo)
    #         nCards = len(combo)
    #         c0 = combo[nCards - 1]
    #         # for c1 in combo:
    #         #     s10 = cards.internalSet[c0].synergy(cards.internalSet[c1], showTable=True, printInfo=False)
    #         #     s01 = cards.internalSet[c1].synergy(cards.internalSet[c0], showTable=True, printInfo=False)
    #         #     c0 = c1

    # looking for a distance function... synergy as the base so I don't need to use Levenstein on raw text again
    if runTrain:
        cardDist = np.corrcoef(synergy)  # np.cov(synergy)
        np.nan_to_num(cardDist, copy=False, nan=0)
        del synergy
        showCov = False
        if showCov:
            fig, (ax1) = plt.subplots(nrows=1, figsize=(4, 4))
            h = ax1.imshow(cardDist, extent=[.5, cardDist.shape[1] + .5, .5, cardDist.shape[0] + .5], aspect='auto')
            plt.colorbar(h)
            ax1.set_title('synergy_COV')
            plt.tight_layout()
            plt.show()

        iconLoc = backupLoc.replace('.pkl',  '.is' + str(IconicSize)+'.pkl')
        if not resetIcons and exists(iconLoc):
            # synergy = dill.load_session(backupLoc0)
            with open(iconLoc, 'rb') as file:
                iconicCards = dill.load(file)
        else:
            iconicCards = findBasis3(cardDist, IconicSize)
            with open(iconLoc, "wb") as f:
                dill.dump(iconicCards, f)

        showIcons = False  # len(iconicCards) <= 32
        if showIcons:
            showCards = []
            for loc in iconicCards:
                if cards.internalSet[loc].multiverseid:
                    if cards.internalSet[loc].multiverseid == '0':
                        print('invalid id' + cards.internalSet[loc].name)
                    showCards = [cards.internalSet[loc].multiverseid]
                    print(cards.internalSet[loc].name)
                else:
                    print('can''t find ' + cards.internalSet[loc].name)
                # if len(showCards)>1:
                imageCombo(showCards)
                plt.show(block=True)

        inputsLoc = iconLoc.replace('.pkl', '.CD'+str(BasisSize)+'inputs.pkl')
        if not resetInputs and exists(inputsLoc):
            with open(inputsLoc, 'rb') as file:
                items = dill.load(file)
            X = items['X']
            V = items['V']
            combos = items['combos']
            iconicCards = items['iconicCards']
            cardDesciptions = items['cardDesciptions']
            BasisCards = items['BasisCards']
        else:
            iconicCards = iconicCards[0:BasisSize]
            BasisCards = CardSet([cards.internalSet[i] for i in iconicCards])
            if exists(backupLoc):
                shutil.copyfile(backupLoc, backupLoc0)
            with open(backupLoc0, 'rb') as file:
                synergy = dill.load(file)
            cardDesciptions = synergy[iconicCards, :]
            del synergy

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

        TrainedSynergyLoc = inputsLoc.replace('.pkl', '.TrainedSynergy.pkl')
        if not resetTrainedSynergy and exists(TrainedSynergyLoc):
            # synergy = dill.load_session(backupLoc0)
            with open(TrainedSynergyLoc, 'rb') as file:
                synergyTrained = dill.load(file)
        else:
            icons = len(iconicCards)
            icons2 = icons * 2
            LS = LearnedSynergy([icons2, 1])
            LS.trainModel(X, V)
            N = len(cards.internalSet)
            synergyTrained = np.zeros([N, N])
            for x in range(N):
                if x % round(N / 10) == 0:
                    print('using model loop ' + str(x) + ' of ' + str(N))
                X2 = np.zeros([N, icons2])
                for y in range(N):
                    X2[y, 0:icons] = cardDesciptions[:, x]
                    X2[y, icons:icons2] = cardDesciptions[:, y]
                synergyTrained[x, :] = LS.useModel(X2)[:, 0]
            with open(TrainedSynergyLoc, "wb") as f:
                dill.dump(synergyTrained, f)

        showSynergyTrained = False
        if showSynergyTrained:
            fig, (ax1) = plt.subplots(nrows=1, figsize=(4, 4))
            h = ax1.imshow(synergyTrained, extent=[.5, synergyTrained.shape[1] + .5, .5, synergyTrained.shape[0] + .5],
                        # vmin=-.001,
                        # vmax=1.001,
                        aspect='auto')
            plt.colorbar(h)
            ax1.set_title('synergy ' + str(np.mean(np.mean(synergyTrained))))
            plt.tight_layout()
            plt.show()
            synergyTrained = synergyTrained.transpose()
            fig, (ax1) = plt.subplots(nrows=1, figsize=(4, 4))
            h = ax1.imshow(synergyTrained, extent=[.5, synergyTrained.shape[1] + .5, .5, synergyTrained.shape[0] + .5],
                        vmin=-1.001,
                        vmax=.001,
                        aspect='auto')
            plt.colorbar(h)
            ax1.set_title('synergy mean:' + str(np.mean(np.mean(synergyTrained)))
                                + ' max: ' + str(np.max(np.max(synergy))))
            plt.tight_layout()
            plt.show()
            #plt.pause(0.5)

        synergy = synergyTrained + synergyTrained.transpose()
    
    showSynergy = False
    if showSynergy:
        fig, (ax1) = plt.subplots(nrows=1, figsize=(4, 4))
        h = ax1.imshow(synergy, extent=[.5, synergy.shape[1] + .5, .5, synergy.shape[0] + .5], vmin=-1.001,
                       vmax=0.001, aspect='auto')
        plt.colorbar(h)
        ax1.set_title('synergy')
        plt.tight_layout()
        plt.show()

    commanders = ['Garth One-Eye'
        , 'Morophon, the Boundless'
        , 'Reaper King'
        , 'Niv-Mizzet Reborn'
        , 'O-Kagachi, Vengeful Kami'
        , 'Ramos, Dragon Engine'
        , 'Scion of the Ur-Dragon'
        , 'The Ur-Dragon'
        , 'Kyodai, Soul of Kamigawa'
        , 'Tiamat'
        , 'Gadrak, the Crown-Scourge'
        , 'Lathliss, Dragon Queen'
        , 'Inferno of the Star Mounts'
        ]
    commanderIndexes = cards.findCards(commanders)
    commanderPoolsByIdentity=cards.CardPoolByCommander(commanders)
    sourceInfo=cards.sources()
    belonging = np.zeros([synergy.shape[0], 1])
    for ci in range(len(commanderIndexes)):
        belonging[commanderIndexes[ci]] = ci + 1
    # worthy of Garth
    manualSetup = cards.findCards(["Volrath's Laboratory", 'Riptide Replicator', 'Mimic Vat'])
    # worthy of Reaper with changelings
    belonging[manualSetup] = 1;
    manualSetup = cards.findCards(["Sylvia Brightspear", 'Khorvath Brightflame'])
    belonging[manualSetup] = 3;
    classes=cards.classes()
    comanderClasses=classes[commanderIndexes]
    updatedBelonging = findNetworks2(classes,comanderClasses,commanderPoolsByIdentity,\
         synergy, belonging, sourceInfo, [45, 80, 80, 91, 99, 100] )

    for deck in updatedBelonging:
        print(" ")
        multiCombo = []
        for c in range(len(deck)):
            card =deck[c];
            if cards.internalSet[card].multiverseid:
                multiCombo = [cards.internalSet[card].multiverseid]
                #print(str(c) +" "+cards.internalSet[card].name)
                print(cards.internalSet[card].name)
            else:
                print('can''t find ' + cards.internalSet[card].name)
            #imageCombo(multiCombo)
        #imageCombo(['0'])

    # # BasisSynergy = synergyTrained[iconicCards, :] * -1.0
    # # BasisSynergy = BasisSynergy[:, iconicCards]
    # BasisSynergy=synergyTrained*-1.0
    # # loops not strong enough to find combos
    # combos = findLoops2(BasisSynergy)  # passes like C#
    # for combo in combos:
    #     print(combo)
    #     multiCombo = []
    #     for loc0 in combo:
    #         loc=loc0
    #         # loc = iconicCards[loc0]
    #         if cards.internalSet[loc].multiverseid:
    #             multiCombo = multiCombo + [cards.internalSet[loc].multiverseid]
    #             print(cards.internalSet[loc].name)
    #         else:
    #             print('can''t find ' + cards.internalSet[loc].name)
    #     if len(multiCombo) > 1:
    #         imageCombo(multiCombo)

    # BasisSynergy = synergy[:, iconicCards]
    #
