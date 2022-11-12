from time import *
from Card import *
from concurrent.futures import ProcessPoolExecutor
import gc
import re

class CardSet:
    # meant to be a list of cards
    def __init__(self, cards):
        if isinstance(cards, CardSet):
            self.internalSet = [c for c in cards.internalSet]
        elif all(isinstance(val, Card) for val in cards):
            self.internalSet = cards
        else:
            raise ValueError("invalid cards")
        self.lastMessage="0%"

    def subsetByNames(self, names):
        cards = []
        for name in names:
            found = False
            for card in self.internalSet:
                names = card.name.split(' // ')
                if name in names or name == card.name:
                    cards.append(card)
                    found = True
            if not found:
                print("did not find " + name)
        return cards

    def add(self, cards):
        if isinstance(cards, CardSet):
            self.internalSet = self.internalSet + cards.internalSet
        elif all(isinstance(val, Card) for val in cards):
            self.internalSet = self.internalSet + cards
        else:
            raise ValueError("invalid cards")

    def synergy(self):
        N = len(self.internalSet)
        synergy = [[0] * N for i in range(N)]
        for r in range(N):
            cardR = self.internalSet[r]
            t = time()
            for c in range(N):
                cardC = self.internalSet[c]
                # t = time()
                synergy[c][r] = cardR.synergy(cardC)
                # elapsed = time() - t
                # print(f"{r} {c} {d[c][r]} {elapsed} s")
            elapsed = time() - t
            print(f"{r} {synergy[0][r]} {elapsed} s")
        return synergy

    def synergy2(self):
        N = len(self.internalSet)
        synergy = np.zeros([N, N])
        for r in range(N):
            cardR = self.internalSet[r]
            t = time()
            for c in range(N):
                cardC = self.internalSet[c]
                # t = time()
                synergy[c, r] = cardR.synergy(cardC)
                # elapsed = time() - t
                # print(f"{r} {c} {d[c][r]} {elapsed} s")
            elapsed = time() - t
            print(f"{r} {synergy[0][r]} {elapsed} s")
        return synergy

    synNotSim =True
    fine = False
    showTable = False
    printInfo = False
    mxPrcs = 3    

    def subSynergy3(self, r):
        N = len(self.internalSet)
        cardR = self.internalSet[r]
        t = time()
        synergy = np.zeros([N, 1])
        for c in range(N):
            cardC = self.internalSet[c]
            # t = time()
            synergy[c, 0] = cardR.synergy(cardC, syn = self.synNotSim, fine=self.fine, showTable=self.showTable, printInfo=self.printInfo)
            # elapsed = time() - t
            # print(f"{r} {c} {d[c][r]} {elapsed} s")
        elapsed = time() - t
        # print(f"{r} {synergy[0]} {elapsed} s")
        res = [synergy, r]
        return res

    def synergy3(self):
        N = len(self.internalSet)
        synergy = np.zeros([N, N])
        total_error = 0
        self.lastMessage="0%"
        t0=time()
        print('starting batch of '+ str(N))
        with ProcessPoolExecutor(max_workers=self.mxPrcs) as pool:
            for res in pool.map(self.subSynergy3, range(N)):
                synergy[:, res[1]] = res[0][:, 0]
                if res[1] % 32 == 0:
                    gc.collect()
                    ind=res[1]+1
                    remainingTime=(time()-t0)/ind*(N-ind)
                    self.lastMessage=str(res[1]/N*100) + "% remaining time =" +str(remainingTime/3600)+" hours"
                    print('gc row '+str(res[1]) +' '+self.lastMessage)
        return synergy

    def subset(self, names):
        cards = []
        for card in self.internalSet:
            # print(card.name)
            for name in names:
                # if card.LevenshteinDistance(name, card.name, False, False) < 0.2:
                if name == card.name:
                    cards = cards + [card]
                    print(card.name)
        return CardSet(cards)

    def subsetByInds(self, inds):
        cards = []
        for ind in inds:
            cards = cards + [self.internalSet[ind]]
        return CardSet(cards)

    def sortCardsByType(self, types):
        groups = self.partitionCardsByType(types)
        inds = [];
        for group in groups:
            inds = inds + group
        self.internalSet = [self.internalSet[ind] for ind in inds]
        return inds

    def partitionCardsByType(self, types):
        inds = []
        inds1 = range(len(self.internalSet))
        for t in range(len(types)):
            type = types[t]
            text = types[t].split(' ')
            inds0 = []
            inds2 = []
            for i in inds1:
                if len(text) < 2:
                    check = (type in self.internalSet[i].types.lower()) or (
                            type in self.internalSet[i].subtypes.lower())
                else:
                    check = (text[0]=="any"
                             or (text[0] in self.internalSet[i].types.lower())
                             or (text[0] in self.internalSet[i].subtypes.lower())) \
                            and (text[1] in self.internalSet[i].text.lower())
                if check:
                    inds0.append(i)
                else:
                    inds2.append(i)
            inds1 = inds2
            inds = inds + [inds0]
        inds = inds + [inds1]
        return inds

    def mergeTransforms(self):
        inds = []
        for ind in range(len(self.internalSet)):
            found = False
            if self.internalSet[ind].side:
                if self.internalSet[ind].side == 'a':
                    for ind2 in range(len(self.internalSet)):
                        if self.internalSet[ind].name == self.internalSet[ind2].name \
                                and not ind == ind2:
                            self.internalSet[ind].mergeWith(self.internalSet[ind2])
                            print('merge on ' + self.internalSet[ind].name)
                    inds.append(ind)
            else:
                inds.append(ind)
        self.internalSet = [self.internalSet[ind] for ind in inds]

    def findCards(self, names, equalsNotLike = True):
        cards = []
        for name in names:
            found = -1
            for card in range(len(self.internalSet)):
                if equalsNotLike:
                    if name == self.internalSet[card].name:
                        found = card
                else:
                    if name in self.internalSet[card].name:
                        found = card
            cards = cards + [found]
        return cards

    def findCards2(self, name, equalsNotLike = True):
        cards = []
        for card in range(len(self.internalSet)):
            if equalsNotLike:
                if name == self.internalSet[card].name:
                    cards = cards + [self.internalSet[card]]
            else:
                if name in self.internalSet[card].name:
                    cards = cards + [self.internalSet[card]]
        return cards

    def get(self,tribal,sypathizer):
        cards = []
        for card in range(len(self.internalSet)):
            if tribal==self.internalSet[card].isTribal \
                and sypathizer==self.internalSet[card].isNearTribal:
                cards = cards + [card]
                print(self.internalSet[card].name)
        return cards

    def ColorIdentity(self):
        ids = []
        for card in range(len(self.internalSet)):
            id=self.internalSet[card].ColorID()
            ids=ids+[id];
        return ids

    def CardPoolByCommander(self, commanders):
        cmdrInds=self.findCards(commanders)
        colorIDs=self.ColorIdentity()
        cardPool= np.empty((len(commanders),len(colorIDs)))
        for deck in range(len(commanders)):
            cmdID=colorIDs[cmdrInds[deck]]
            for card in range(len(self.internalSet)): 
                if( (colorIDs[card] & cmdID) == colorIDs[card]):
                    cardPool[deck,card]=0
                else:
                    cardPool[deck,card]=-float('inf')
        return cardPool
        
    def sources(self):
        makesFor= np.empty((len(self.internalSet),2))
        for card in range(len(self.internalSet)): 
            current=self.internalSet[card]
            makesFor[card,0]=0
            if "Add" in current.text:
                for ind in range(len(current.Events)):
                    e=current.Events[ind];
                    t=current.Triggers[ind];
                    found=0;
                    for s in e:
                        if '{' in s:
                            found=found+1
                    for s in t:
                        if '{' in s:
                            found=found-1
                    makesFor[card,0]=max(found,makesFor[card,0])
            if "Land" in current.types and makesFor[card,0]==0:
                print('weird land: '+current.name)
            makesFor[card,1]=float(self.internalSet[card].manavalue)
        return makesFor

    def classes(self):
        types = np.empty((len(self.internalSet),1)).flatten()
        for card in range(len(self.internalSet)): 
            types[card]=0
            if(self.internalSet[card].isTribal):
                types[card]=types[card]+1
            if(self.internalSet[card].isNearTribal):
                types[card]=types[card]+2
            if(self.internalSet[card].isChangeling):
                types[card]=types[card]+4
        return types
        