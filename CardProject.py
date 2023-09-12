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
        ,resetTrainedCardMatchUse = None
        ,namedCards = None 
        ,MatchType=2
        ,preProcSize=16
        ,trainingWeight=0.5
        ,BasisSize = -1 
        ,fine = False 
        ,costType = 'L'
        ,label = 'Version'+str(Card.CardVersion_dontChangeAtRuntime)+"/"
        ,coresAllowed=7 
        ,deckSeeds=None
        ,basisType="None"#"Combos"#"CombosSubset"#"DecksCombosSubset" #"DecksSubset"#"Decks"#"DecksCombos"#
        ):
        
        #manage major objects to backup
        self.baseLocation=baseLocation
        self.ramLocation=ramLocation
        
        #todo: resets okay for debug, but are cluttering code now; consider removing them
        self.resetDB= resetDB
        self.resetRawCardMatch = resetRawCardMatch if resetRawCardMatch else self.resetDB
        self.resetIcons = resetIcons if resetIcons else self.resetRawCardMatch
        self.resetInputs = resetInputs if resetInputs else self.resetIcons
        self.resetModel = resetModel if resetModel else self.resetInputs
        self.resetTrainedCardMatch = resetTrainedCardMatch if resetTrainedCardMatch else self.resetModel
        self.resetTrainedCardMatchUse = resetTrainedCardMatchUse if resetTrainedCardMatchUse else self.resetTrainedCardMatch
        
        
        self.namedCards = namedCards#pass in names list or integer for debug cases

        #options
        self.MatchType=MatchType
        self.preProcSize=preProcSize
        self.BasisSize = BasisSize
        self.basisType=basisType
        self.trainingWeight=trainingWeight
        self.fine = fine
        self.costType = costType
        self.label = label
        self.coresAllowed=coresAllowed

        if deckSeeds:
            self.deckSeeds=deckSeeds
        else:
            #A note on Inferno of the Star Mounts, Other dragons like Lathliss can capture
            #  the firebreathers as a set, so I am manually seeding them to him
            fiveColorBaseLands=[\
                'Plains','Snow-Covered Plains',\
                'Island','Snow-Covered Island',\
                'Swamp','Snow-Covered Swamp',\
                'Mountain','Snow-Covered Mountain',\
                'Forest','Snow-Covered Forest']
            RedBaseLands=[]
            for land in range(25):# leave room for other interesting lands
                RedBaseLands=RedBaseLands+['Mountain']
            self.deckSeeds = [
            ['Garth One-Eye',"Volrath's Laboratory", 'Riptide Replicator', 'Mimic Vat']\
                +fiveColorBaseLands \
            , ['Morophon, the Boundless']+fiveColorBaseLands\
            , ['Reaper King', "Sylvia Brightspear", 'Khorvath Brightflame']\
                +fiveColorBaseLands\
            , ['Niv-Mizzet Reborn']+fiveColorBaseLands\
            , ['O-Kagachi, Vengeful Kami']+fiveColorBaseLands\
            , ['Ramos, Dragon Engine']+fiveColorBaseLands\
            , ['Scion of the Ur-Dragon']+fiveColorBaseLands\
            , ['The Ur-Dragon']+fiveColorBaseLands\
            , ['Kyodai, Soul of Kamigawa']+fiveColorBaseLands\
            , ['Tiamat']+fiveColorBaseLands\
            , ['Gadrak, the Crown-Scourge']+RedBaseLands\
            , ['Lathliss, Dragon Queen']+RedBaseLands\
            , ['Inferno of the Star Mounts', \
                'Shivan Dragon','Furnace Whelp', \
                'Hellkite Punisher','Dragon Hatchling', \
                'Rakdos Pit Dragon','Arcbound Whelp',\
                'Pardic Dragon',\
                'Mana Flare','Caged Sun',\
                'Gauntlet of Might','Gauntlet of Power',\
                'Extraplanar Lens',\
                'Dragon Tyrant','Nalathni Dragon',\
                'Dragon Whelp','Lightning Dragon',\
                'Chaos Moon'\
                ]+RedBaseLands\
            ]
        self.cardTypeBalance=[45, 35, 0, 11, 9, 1];
        #core deck, land, 1 or less, 2 or less, 3 or less, 4 or less

        self.cards=None
        self.BasisIndexes=None
        self.CardMatch=None
        self.updatedBelonging=None
        self.deckNames=None
        self.PCAscore=None

    def debugCost(self,numCards=-1,simType=-1):
        if(simType>-1):
            fname0 = self.label + 'CardInfo.' + str(numCards) + str(self.fine) 
            fname= fname0+ '.SimType'+str(simType)+'.pkl'
            synergyLoc0 = self.ramLocation+ fname
            #ideally this should be done after similarity 
            with open(synergyLoc0, 'rb') as file:
                cardMatch = dill.load(file)
                file.close()
        else:
            cardMatch=self.CardMatch 
        cards=self.cards
        fig, (ax1) = plt.subplots(nrows=1, figsize=(4, 4))
        h = ax1.imshow(cardMatch, extent=[.5, cardMatch.shape[1] + .5, .5, cardMatch.shape[0] + .5], 
                     aspect='auto',origin='lower')#vmin=-1.001,vmax=0.001,
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
                if simType==0 or simType==-1:
                    cards.internalSet[x].synergy(cards.internalSet[y],showTable=True, printInfo=True,synSimType=0)
                    cards.internalSet[y].synergy(cards.internalSet[x],showTable=True, printInfo=True,synSimType=0)
                if simType==1 or simType==-1:
                    cards.internalSet[x].synergy(cards.internalSet[y],showTable=True, printInfo=True,synSimType=1)
                if simType==2 or simType==-1:
                    cards.internalSet[x].synergy(cards.internalSet[y],showTable=True, printInfo=True,synSimType=2)


        plt.connect('button_press_event', on_click)
        plt.show(block=False)


    def createOrLoadData(self):
    
        t = time()
        MtgDbHelper.saveLocation=self.baseLocation+self.label
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

        baseLocation=self.baseLocation+self.label
        if(not os.path.isdir(baseLocation)):
            os.mkdir(baseLocation)
        ramLocation=self.ramLocation+self.label
        if(not os.path.isdir(ramLocation)):
            os.mkdir(ramLocation)

        fname0 = 'CardInfo.' + str(numCards) + str(self.fine) + self.costType
        
        fname = fname0 + '.Merged.pkl'
        vectorLoc = baseLocation+ fname
        vectorLoc0 = vectorLoc
        #vectorLoc0 = ramLocation+ fname 
        #if exists(vectorLoc) and not exists(vectorLoc0):
        #    shutil.copyfile(vectorLoc, vectorLoc0)
        if not resetRawCardMatch and exists(vectorLoc0):
            with open(vectorLoc0, 'rb') as file:
                rawCardVector = dill.load(file)
                file.close()
        else:
            synergies=[]
            for simType in range(3):
                fname= fname0+ '.SimType'+str(simType)+'.pkl'
                synergyLoc = baseLocation+fname
                synergyLoc0 = ramLocation+ fname
                if exists(synergyLoc):
                    shutil.copyfile(synergyLoc, synergyLoc0)
                if not resetRawCardMatch and exists(synergyLoc0):
                    #ideally this should be done after similarity 
                    with open(synergyLoc0, 'rb') as file:
                        synergy = dill.load(file)
                        file.close()
                else:
                    t = time()
                    cards.fine = self.fine
                    cards.synSimType = simType
                    cards.mxPrcs = self.coresAllowed
                    cards.costType = self.costType
                    synergy = cards.synergy()
                    elapsed2 = time() - t
                    full = len(MtgDbHelper.cards.internalSet) ** 2 / len(cards.internalSet) ** 2 / 60 / 60
                    print(f"rawCardVector for {len(cards.internalSet)}^2 {elapsed2} s expect {elapsed2 * full} hours")
                    with open(synergyLoc, "wb") as f:
                        dill.dump(synergy, f)
                        f.close()
                    gc.collect()
                synergies.append(synergy)
                del synergy 
            
            rawCardVector=np.concatenate((synergies[0],synergies[1],synergies[2]))
            del synergies
            with open(vectorLoc, "wb") as f:
                dill.dump(rawCardVector, f)
                f.close()
            
            gc.collect()
        
        # looking for a distance function... rawCardVector as the base so I don't need to use Levenstein on raw text again
        distLoc = vectorLoc.replace('.pkl',  '.dist.pkl')
        iconLocList = vectorLoc.replace('.pkl',  '.'+self.basisType+'Icons.txt')
        iconLoc = vectorLoc.replace('.pkl',  '.IS' + str(self.BasisSize)+'.'+self.basisType+'.pkl')
        if self.MatchType==0:
            TrainedCardMatchLoc = iconLoc.replace('.pkl', '.HeuristicMatch.pkl')
        else:
            P=self.trainingWeight
            if self.MatchType>1:
                preProcLoc = iconLoc.replace('.pkl', '.preProc'+str(self.MatchType)+'.'+str(self.preProcSize)+'.pkl')
            else:
                preProcLoc = iconLoc;
            modelCardMatchLoc = preProcLoc.replace('.pkl', '.'+str(P)+'.TrainedCardMatch.model/')
            TrainedCardMatchLoc = preProcLoc.replace('.pkl', '.'+str(P)+'.TrainedCardMatch.pkl')
        pcaCardMatchLoc = TrainedCardMatchLoc.replace('.pkl', '.pca.pkl')
        distCardMatchLoc = TrainedCardMatchLoc.replace('.pkl', '.dist.pkl')
        deckBase=TrainedCardMatchLoc.replace('.pkl','.Deck.')
            

        iconLoc0=iconLoc
        if not self.resetIcons and exists(iconLoc0):
            with open(iconLoc0, 'rb') as file:
                iconInfo = dill.load(file)
                file.close()
            iconicCards=iconInfo[0]
        else:
            if not self.resetRawCardMatch and exists(distLoc):
                with open(distLoc, 'rb') as file:
                    cardDist = dill.load(file)
                    file.close()
            else:
                cardDist = L2dist(rawCardVector)
                with open(distLoc, "wb") as f:
                    dill.dump(cardDist, f)
                    f.close()
            
            basisSeeds=[]
            if("Combos" in self.basisType):
                location = '/media/VMShare/TrainingInfo/Combos/'
                from os import listdir
                from os.path import isfile, join
                onlyfiles = [f for f in listdir(location) if isfile(join(location, f))]
                for file in onlyfiles:
                    CD=CockatriceDeck()
                    CD.loadText(location + file)
                    for card in CD.cardSetIndexes:
                        if not card in basisSeeds:
                            basisSeeds.append(card)
            if("Decks" in self.basisType):
                location = '/media/VMShare/TrainingInfo/Decks/'
                from os import listdir
                from os.path import isfile, join
                onlyfiles = [f for f in listdir(location) if isfile(join(location, f))]
                for file in onlyfiles:
                    CD=CockatriceDeck()
                    CD.load(location + file)
                    for card in CD.cardSetIndexes:
                        if not card in basisSeeds:
                            basisSeeds.append(card)
            basisType=0
            if("Subset" in self.basisType):
                basisType=1
            info = findBasis4(cardDist, basisSeeds,basisType)
            iconicCards=info[0]
            iconicCardsNames=MtgDbHelper.cards.namesByInds(iconicCards)
            iconInfo=[iconicCards,iconicCardsNames]
            with open(iconLoc, "wb") as f:
                dill.dump(iconInfo, f)
                f.close()
            CD=CockatriceDeck()
            CD.setByInds(iconInfo[0])
            CD.saveText(iconLocList)

        self.BasisIndexes=iconicCards[0:self.BasisSize]

        if numCards == -1:#helpful debug routines but skip the training
            R=rawCardVector.shape[1]
            tmp=np.maximum(rawCardVector[0:R,:],rawCardVector[0:R,:].transpose())
            tmp=np.maximum(tmp,np.maximum(rawCardVector[R:2*R,:],rawCardVector[2*R:3*R,:]))
            self.CardMatch=tmp;
            #self.debugCost(-1,0)
            #self.debugCost(-1,1)
            #self.debugCost(-1,2)
            self.debugCost(-1,-1)
            plt.show(block=True)
            self.updatedBelonging=None

            location = '/media/VMShare/OldDecks/Dragons/'
            from os import listdir
            from os.path import isfile, join
            self.deckNames=[f for f in listdir(location) if isfile(join(location, f))]
            return

        if self.MatchType==0:
            R=rawCardVector.shape[1]
            cardMatch=np.maximum(rawCardVector[0:R,:],rawCardVector[0:R,:].transpose())
            cardMatch=np.maximum(cardMatch,np.maximum(rawCardVector[R:2*R,:],rawCardVector[2*R:3*R,:]))
            del iconInfo
            del rawCardVector
            deckBase=vectorLoc.replace('.pkl','.Deck.')
        else:    
            if self.MatchType==2: #
                if not self.resetTrainedCardMatch and exists(preProcLoc):
                    with open(preProcLoc, 'rb') as file:
                        preWeights = dill.load(file)
                        file.close()
                else:
                    #todo: cosider finding v from basis for reusability and speed
                    t0=time()
                    print('started eig pre')
                    temp = rawCardVector[self.BasisIndexes,:]
                    temp = np.matmul(temp,temp.transpose())
                    w, preWeights = np.linalg.eig(temp)
                    del w
                    del temp
                    with open(preProcLoc, "wb") as f:
                        dill.dump(preWeights, f)
                        f.close()
                    print('eig pre done after '+str((time()-t0)/60) + ' minutes')


            #training strategy notes:
            # card matching heuristic is used to build decks from a pairwise matrix
            #  I want to influence scores with my own decks and any of my own combos
            #  Scores should reflect three? states:
            #  1) synergistic combos - typically infinite game enders
            #  2) similar - ideally they add redundancy to combos
            #  3) unrelated - cards that should not be included
            # 1 - synergy to be manually identified combos
            # 0.1 - similarity to be identified by existing decks
            # 0 - likely want to find several hundered awful cards; pick them from the basis
            # synergy is a set measure measurment, not a card measurment
            # training data likely to include ~2k  cards to be compared against itself
            # Use basis to prune vector to length of 700*3
            # training input~ 2k x 2k pairs * 2 vectors of 2k * 8bytes
            # 128GB training data; (used to bae <1/3 of this with other plans)
            # need to train with chunks of data 


            if not self.resetTrainedCardMatch and exists(modelCardMatchLoc):
                print('Model Exists')
            else:
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

                location = '/media/VMShare/TrainingInfo/Chaff/'
                from os import listdir
                from os.path import isfile, join
                onlyfiles = [f for f in listdir(location) if isfile(join(location, f))]
                chaff = []
                for file in onlyfiles:
                    CD=CockatriceDeck()
                    CD.loadText(location + file)
                    inds=MtgDbHelper.cards.findCards( CD.cardSet.getNames())
                    for ind in inds:
                        if not ind in deckAndCombos:
                            chaff.append(ind)

                
                if self.MatchType==2: #
                    N=self.preProcSize
                    if(N<1):
                        N=len(self.BasisIndexes)
                    reducedVector=np.matmul(preWeights[range(0,N),:],rawCardVector[self.BasisIndexes,:]);
                else:
                    N=rawCardVector.shape[1]
                    reducedVector=np.concatenate(
                        (rawCardVector[self.BasisIndexes,:],
                        rawCardVector[[s+N for s in self.BasisIndexes],:],
                        rawCardVector[[s+2*N for s in self.BasisIndexes],:]),axis=0)

                LS=LearnedSynergy(modelCardMatchLoc,TrainedCardMatchLoc)
                
                t0=time()
                e4=LS.trainModel2(reducedVector,[],[],combos,256*16,16,True,P,showPlots=0)
                errCheck=[]
                overEpochs=32;
                for lcv in range(overEpochs): 
                    e2=-1#LS.trainModel2(reducedVector,[],[],combos,32,False,P,showPlots=0)
                    e1=-1#LS.trainModel2(reducedVector,[],decks,combos,2,False,??,showPlots=0)
                    e0=LS.trainModel2(reducedVector,chaff,decks,combos,16,16,False,P,showPlots=0)
                    timeTaken=(time()-t0)/60
                    errCheck.append([lcv, e0, e1, e2])
                    summary=str(lcv)+', '+str(e0)+', '+str(e1)+', '+str(e2)+', '+str(timeTaken)+'\r\n'
                    with open('repOfTrippleReps.txt','a') as f:
                        f.write(summary)
                        f.close()
                del reducedVector
                
            if not self.resetTrainedCardMatchUse and exists(TrainedCardMatchLoc):
                with open(TrainedCardMatchLoc, 'rb') as file:
                    trainedCardMatch = dill.load(file)
                    file.close()
            else:
                LS=LearnedSynergy(modelCardMatchLoc,TrainedCardMatchLoc)
                N=rawCardVector.shape[1]
                if self.MatchType==2: #                    
                    N=self.preProcSize
                    if(N<1):
                        N=len(self.BasisIndexes)
                    reducedVector=np.matmul(preWeights[range(0,N),:],rawCardVector[self.BasisIndexes,:]);
                else:
                    reducedVector=np.concatenate(
                        (rawCardVector[self.BasisIndexes,:],
                        rawCardVector[[s+N for s in self.BasisIndexes],:],
                        rawCardVector[[s+2*N for s in self.BasisIndexes],:]),axis=0)
                trainedCardMatch = LS.useModel2(reducedVector,True,showPlots=1)
                plt.show(block=True)

            cardMatch = (trainedCardMatch + trainedCardMatch.transpose())/2-1
            del trainedCardMatch

        self.CardMatch=cardMatch

        if False:
            fig, ax = plt.subplots(nrows=1, figsize=(4, 4), num=2)
            h = ax.imshow(cardMatch, vmin=-1,
                vmax=0, aspect='auto')
            plt.show(block=False)

        if not self.resetTrainedCardMatch and exists(pcaCardMatchLoc):
            with open(pcaCardMatchLoc, 'rb') as file:
                PCAscore = dill.load(file)
                file.close()
        else:
            #todo: cosider finding v from basis for reusability and speed
            t0=time()
            print('started eig')
            w, v = np.linalg.eig(self.CardMatch)
            PCAscore=self.CardMatch*v
            del v
            del w
            with open(pcaCardMatchLoc, "wb") as f:
                dill.dump(PCAscore, f)
                f.close()
            print('eig done after '+str((time()-t0)/60) + ' minutes')
        self.PCAscore=PCAscore

        #distance should not be neeeded for the matching based deck builder
        #also when distance was used, it was used with a negaive
        #not maybe prior bugs in deck building made -dist better than match
        # if not self.resetTrainedCardMatch and exists(distCardMatchLoc):
        #     with open(distCardMatchLoc, 'rb') as file:
        #         distCardMatch = dill.load(file)
        #         file.close()
        # else:
        #     distCardMatch=0*cardMatch;
        #     N=cardMatch.shape[0]
        #     for c in range(N):#candidate for parallelization
        #         if c % 32 == 0:
        #             print('dist '+str(c/N*100) + '% of '+str(N))
        #         vs=cardMatch-cardMatch[:,c];
        #         vs=vs**2
        #         distCardMatch[c,:]=vs.sum(axis=1).reshape(1,N)
        #     for r in range(N):
        #         for c in range(r,N):
        #             distCardMatch[r,c]=distCardMatch[c,r]            
        #     with open(distCardMatchLoc, "wb") as f:
        #         dill.dump(distCardMatch, f)
        #         f.close()

        commanders=[];
        for dk in self.deckSeeds:
            commanders.append(dk[0])

        commanderIndexes = cards.findCards(commanders)
        commanderPoolsByIdentity=cards.CardPoolByCommander(commanders)
        sourceInfo=cards.sources()
        
        deckSeeding=[self.cards.findCards(self.deckSeeds[i]) for i in range(len(self.deckSeeds))]

        classes=cards.classes()
        comanderClasses=classes[commanderIndexes]
        updatedBelonging = findNetworks2(classes,comanderClasses,commanderPoolsByIdentity,\
            cardMatch, deckSeeding, sourceInfo, self.cardTypeBalance )

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
        , 'Lathliss, Dragon Queen', 'Draco', 'Plains']
    names0 = ['The Mirari Conjecture', 'Power Conduit', 'Time Stretch']
    names0 = ['Scion of the Ur-Dragon', 'Teneb, the Harvester']
    cp=CardProject(namedCards=None,MatchType = 2,preProcSize=768,fine=False,costType='J',resetTrainedCardMatchUse=True)
    cp.createOrLoadData()
