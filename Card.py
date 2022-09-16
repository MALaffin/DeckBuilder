from tkinter import Y
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
import numpy as np


class Card:

    def ParseText(self, verbose=False):
        self.Triggers = []
        self.Events = []
        isCreature = 'Creature' in self.types;
        # THIS_CARD can have costs dependent on its types
        # allTypes = self.name.lower() + ' ' + self.types.lower()
        allTypes = self.types.lower()
        if self.manacost:
            MC=self.convertManaCosts(self.manacost)
        else:
            MC = '???' #maybe some suspend cards...
        castMod = ''
        if (not 'instant' in self.types.lower()) and (not 'sorcery' in self.types.lower()):
            allTypes = allTypes + ' permanent'
        else:
            castMod = 'graveyard '
        if self.subtypes:
            allTypes = allTypes + ' ' + self.subtypes.lower()
        
        #Casting gets a something
        castText = MC + ' : cast ' + castMod + allTypes \
            + MC.replace('{w}', ' white ').replace('{u}', ' blue ') \
            .replace('{b}', ' black ').replace('{r}', ' red ')\
            .replace('{g}', ' green ').replace('{c}', ' colorless ') \
            + '\n'
        #for m in range(1,self.biggestMannaNumber):
        #    castText=castText.replace('{'+str(m)+'}', '')
        #creature somethings can attack
        if isCreature:
            castText = castText + 'unblock : damage \n' + 'attack : damage \n'
        
        # keep high information words
        text = self.convertManaCosts(self.text)
        subNames = self.name.lower().split(' // ')
        for name in subNames:
            text = text.replace(name, allTypes)
        text = text.replace('end of turn', '') \
            .replace('this turn', 'thisturn') \
            .replace(' turn', ' untap draw attack creature artifact land') \
            .replace('if ', 'when ') \
            .replace('proliferate ', 'counter ') \
            .replace('\ni ', '\ncounter: ') \
            .replace('\nii ', '\ncounter: ') \
            .replace('\niii ', '\ncounter: ') \
            .replace('\niv ', '\ncounter: ') \
            .replace('counter target', 'cancel') \
            .replace('{t}', 'untap') \
            .replace('combat', 'attack') \
            .replace('is every creature type', 'changeling') \
            .replace('sacrifice', 'graveyard') \
            .replace('targets', 'target')
        types = ['creature', 'artifact', 'land', 'planeswalker', 'instant', 'sorcery', 'enchantment'
            , 'white', 'blue', 'black', 'red', 'green'] #todo consider devoid
        for t in types:
            text.replace(t + 's', t)
        punctuation = [' ', ':', ',', '\n']
        keyGameWords = ['untap', 'upkeep', 'draw', 'attack', 'endofturn'
                           , 'when', 'sacrifice', 'graveyard', 'return', 'hand', 'library'
                           , 'battlefield', '+1/+1', 'gets', '+1/+0', 'exile'
                           , 'target', 'counter', 'token'
                           , 'prevent', 'damage', 'lose', 'life'
                           , 'search', 'thisturn', 'all', 'cast', 'spell', 'main', 'player', 'opponent'
                           , 'manaOfAnyType', 'could', 'unblock'
                           , 'cancel'
                           , 'changeling'
                        ] + punctuation + types + self.getManaKeywords()
        withMana = castText + text
        blocks = [withMana]  # [text]#
        if verbose:
            print(blocks[0])
        for p in punctuation:
            tmp = []
            for block in blocks:
                words = block.split(p)
                tmp = tmp + [words[0]]
                for w in range(1, len(words)):
                    tmp = tmp + [p, words[w]]
            blocks = tmp
        # filter text by chosen words
        text = ''
        for word in blocks:
            for keyword in keyGameWords:
                if keyword in word:
                    text = text + keyword
                    continue
        blocks = text.split('\n')
        for block in blocks:
            activated = block.split(':', 1)
            triggered = block.split(',', 1)
            if len(activated) == 2:
                trigger = activated[0]
                event = activated[1]
            elif len(triggered) == 2:
                trigger = triggered[0]
                event = triggered[1]
            else:
                trigger = ''
                event = block
            trigger=self.parseManaForTrigger(trigger)
            event=self.parseManaForEvent(event)
            trigger = trigger.replace(',', '')
            event = event.replace(',', '')
            # sacrifice adds to the events
            trigger = list(filter(None, trigger.split(' ')))
            trigger.sort()  # mtg does not seem to care too much about order target red creature vs if red target
            event = event.replace('untap', '{t}')  # using untap(effect) and {t}(cost) as a synergy pair
            #played right, triggers are events...
            repTrigger='graveyard' in trigger \
                    or 'counter' in trigger;
            event = list(filter(None, event.split(' ')))
            event.sort()
            self.Triggers = self.Triggers + [trigger]
            self.Events = self.Events + [event]
            if repTrigger:
                self.Triggers = self.Triggers + [trigger]
                self.Events = self.Events + [ ['repTrigger'] + trigger]

        if verbose:
            print(str(self.Triggers))
            print(str(self.Events))


    #the various types of mana are effectively directional
    #instead of codding the directions and conditions into the synergy methods
    #the mana will be split and converted to conform to a basic levenstien cost
    # keywords control what is kept
    # parse-for methods will control what the symbols can match to
    #{a} is my own construct it will have properties similar {1} in the a parse-for
    biggestMannaNumber=20#fifteen? just make it bigger
    def convertManaCosts(self,textWithCost):
        textWithCost = textWithCost.replace('}{', '} {').lower()
        #turn some common text into a new mana symbol
        textWithCost=textWithCost \
            .replace('one mana of any',   '{a}') \
            .replace('two mana of any',   '{a} {a}') \
            .replace('three mana of any', '{a} {a} {a}') \
            .replace('four mana of any',  '{a} {a} {a} {a}') \
            .replace('five mana of any',  '{a} {a} {a} {a} {a}') \
        #ignoring reaper king, half, and phyrexian mana types
        textWithCost=textWithCost \
            .replace('{2/',  '{') \
            .replace('{h/',  '{') \
            .replace('/p}',  '}')
        #Simplifying the multi-mana types
        types=['w', 'u', 'b', 'r', 'g']
        for r in types:
            for l in types:
                extWithCost=textWithCost.replace('{'+l+'/'+r+'}', '{'+l+'} ManaOr {'+r+'}')
        #make the numbered mana (up to twenty) into single mana elements
        for n in range(self.biggestMannaNumber,1,-1):
            nm1=n-1;
            textWithCost=textWithCost.replace("{"+str(n)+"}", "{"+str(nm1)+"} {1}")
        return textWithCost
    def getManaKeywords(self):
        withMana=['{w}', '{u}', '{b}', '{r}', '{g}', 
                  '{c}', '{a}', '{1}' ]
        #reaper king {2\ is so special it likely does not need to be addressed        
        return withMana
    def parseManaForTrigger(self,text):
        #text=text.replace('{1}','{c} {1} {w} {u} {b} {r} {g}')
        #the matching of {1} should result in a weak match to each color
        #{a} as input implies a parsing error - for now let them pass
        #casting cost of four would lead to 21 symbols... 
        # so really should have dynamic costs... 
        text=text.replace('{1}','{a}')
        return text
    def parseManaForEvent(self,text):
        #text=text.replace('{a}','{1} {w} {u} {b} {r} {g}')
        #the matching of {1} should result in a weak match to each color
        return text

    def __init__(self, name, manacost, manavalue, loyalty, types, subtypes, text, multiverseid, side, isTribal, isNearTribal,isChangeling):
        self.name = name
        self.manacost = manacost
        self.manavalue = manavalue
        self.loyalty = loyalty
        self.types = types
        self.subtypes = subtypes
        self.text = text
        self.multiverseid = multiverseid
        self.side = side
        self.isTribal=isTribal
        self.isNearTribal=isNearTribal
        self.isChangeling=isChangeling        
        self.ParseText()

    def mergeWith(self, otherCard):
        self.types = self.types + ' ' + otherCard.types
        self.subtypes = self.subtypes + ' ' + otherCard.subtypes
        self.text = self.text + '\n' + otherCard.text
        self.ParseText()

    # https://en.wikipedia.org/wiki/Levenshtein_distance
    # modicied 'Iterative with full matrix' for lists of strings & strings
    @staticmethod
    def __LevenshteinDistance0(s, t, fine, showTable, sCost=1, tCost=1):
        m = len(s)
        n = len(t)
        if (n + m) == 0:
            return 1
        if n == 0:
            return 1
        if m == 0:
            return 1
        scale = 1 / (n * tCost + m * sCost)
        d = [[0] * (m + 1) for i in range(n + 1)]
        for i in range(1, m + 1, 1):
            d[0][i] = i * sCost
        for j in range(1, n + 1, 1):
            d[j][0] = j * tCost
        d0 = max(tCost, sCost)
        for j in range(1, n + 1, 1):
            for i in range(1, m + 1, 1):
                if isinstance(s, str):
                    unitCost = d0
                    if s[i - 1] == t[j - 1]:
                        substitutionCost = 0
                    else:
                        substitutionCost = unitCost
                else:
                    unitCost = 1
                    if fine:
                        substitutionCost = d0 * Card.__LevenshteinDistance0(s[i - 1], t[j - 1], fine, showTable)
                    else:
                        if (s[i - 1] == t[j - 1]):
                            substitutionCost = 0
                        else:
                            substitutionCost = d0
                            if s[i - 1]=='{a}':
                                if '{' in t[j - 1] or '}' in t[j - 1]:
                                    substitutionCost=0;
                            if t[j - 1]=='{a}':
                                if '{' in s[i - 1] or '}' in s[i - 1]:
                                    substitutionCost=0;
                d[j][i] = min([d[j][i - 1] + tCost,  # deletion
                               d[j - 1][i] + sCost,  # insertion
                               d[j - 1][i - 1] + substitutionCost]  # substitution
                              )
        if showTable:
            synergyF = [(item* scale*-1) for sublist in d for item in sublist]
            grid = np.array(synergyF).reshape(len(d), len(d[0]))
            fig, (ax1) = plt.subplots(nrows=1, figsize=(4, 4))
            h=ax1.imshow(grid, 
                        extent=[0 + .5, len(d[0]) + .5, 0 + .5, len(d) + .5], 
                        vmin=-1.001, vmax=0.001, 
                       aspect='auto',origin='lower')
            plt.colorbar(h)
            
            if isinstance(s, str):
                ttl = s + ' vs ' + t
            else:
                ttl = ' '.join(s) + ' vs ' + ' '.join(t)
            ttl= ttl+' end:' + str(-1* d[n][m] * scale)
            ax1.set_title(ttl)
            plt.tight_layout()
            plt.show()
        return d[n][m] * scale

    @staticmethod
    def __LevenshteinDistance1(s, t, fine, showTable, sCost=1, tCost=1):
        m = len(s)
        n = len(t)
        if (n + m) == 0:
            return 1
        if n == 0:
            return 1
        if m == 0:
            return 1
        scale = 1 / (n * tCost + m * sCost)

        v0 = np.zeros(n + 1)
        v1 = np.zeros(n + 1)
        for i in range(n + 1):
            v0[i] = i * tCost

        d0 = max(tCost, sCost)
        for i in range(m):
            v1[0] = i + sCost
            for j in range(n):
                deletionCost = v0[j + 1] + tCost
                insertionCost = v1[j] + sCost
                if s[i] == t[j]:
                    substitutionCost = v0[j]
                else:
                    d = d0
                    if s[i]=='{a}':
                        if '{' in t[j] or '}' in t[j]:
                            d=0;
                    if t[j]=='{a}':
                        if '{' in s[i] or '}' in s[i]:
                            d=0;
                    if fine:
                        d = d0 * Card.__LevenshteinDistance1(s[i], t[j], False, showTable)
                    substitutionCost = v0[j] + d
                v1[j + 1] = min(min(deletionCost, insertionCost), substitutionCost)
            v2 = v0
            v0 = v1
            v1 = v2

        if showTable:
            d0 = Card.__LevenshteinDistance0(s, t, fine, showTable, sCost, tCost)
            print(str(d0))
            print(str(scale * v0[n]))
            if (scale * v0[n] != d0):
                print('L0 L1 mismatch')
        d = scale * v0[n]
        return d

    def synergy(self, card, fine=False, showTable=False, printInfo=False):
        bestCost = float('inf')
        tmp = np.zeros([len(self.Triggers), len(card.Events)])
        meanCost = 0
        sim = 0.0
        syn = 1 - sim * 2
        for t in range(len(self.Triggers)):
            for e in range(len(card.Events)):
                cost = syn * Card.__LevenshteinDistance1(self.Triggers[t], card.Events[e], fine, False, 1, 1)
                if sim > 0:
                    cost = cost + \
                           + sim * Card.__LevenshteinDistance1(self.Events[t], card.Events[e], fine, showTable) \
                           + sim * Card.__LevenshteinDistance1(self.Triggers[t], card.Triggers[e], fine, showTable)
                bestCost = min(bestCost, cost)
                meanCost = meanCost + cost
                tmp[t, e] = cost
                if np.isnan(cost):
                    print(self.name + ' error with ' + card.name)
        meanCost = meanCost / len(self.Triggers) / len(card.Events)
        if printInfo:
            print(self.name + '\n' + str(self.Triggers) + '\n'
                  + card.name + '\n' + str(card.Events) + '\n'
                  + str(tmp))

        if showTable:
            tmp=-tmp;
            fig, (ax1) = plt.subplots(nrows=1, figsize=(4, 4))
            h = ax1.imshow(tmp, extent=[.5, tmp.shape[1] + .5, .5, tmp.shape[0] + .5], vmin=-1.001,
                        vmax=0.001, aspect='auto',origin='lower')
            plt.colorbar(h)
            ax1.set_title('event by trigger' \
                +' mean:'+str(np.mean(np.mean(tmp))) \
                + ' max:'+str(np.max(np.max(tmp))) \
            )
            plt.tight_layout()
            def on_click(event):
                if event.button is MouseButton.LEFT:
                    point = ax1.transData.inverted().transform([event.x, event.y])
                    print('x=' + str(point[0]) + ' y=' + str(point[1]))
                    x = round(point[0]) - 1
                    y = round(point[1]) - 1
                    x=max(0,min(x,len(card.Events)-1))
                    y=max(0,min(y,len(self.Triggers)-1))
                    #breakpoint()
                    Card.__LevenshteinDistance1(self.Triggers[y], card.Events[x], fine, True, 1, 1)
                    if sim > 0:
                        Card.__LevenshteinDistance1(self.Events[y], card.Triggers[x], fine, True, 1, 1)
            plt.connect('button_press_event', on_click)
            plt.show()
        return -bestCost

    def ColorID(self):
        if self.manacost :
            MC=self.manacost
        else:
            MC=""
        w="{W" in self.text or "W}" in self.text or "W" in MC
        u="{U" in self.text or "U}" in self.text or "U" in MC
        b="{B" in self.text or "B}" in self.text or "B" in MC
        r="{R" in self.text or "R}" in self.text or "R" in MC
        g="{G" in self.text or "G}" in self.text or "G" in MC
        id=0;
        if w:
            id=id+1
        if u:
            id=id+2
        if b:
            id=id+4
        if r:
            id=id+8
        if g:
            id=id+16
        return id