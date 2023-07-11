from tkinter import Y
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
import numpy as np


class Card:

    ParseTextEnabled=True
    CardVersion_dontChangeAtRuntime=17


    def RemoveReminders(self,text):
        text2=text
        loc1=text.find("(")
        while loc1>-1:
            loc2=text2.find(")")
            text2=text2[0:loc1] + text2[loc2+1:len(text2)]
            loc1=text2.find("(")
        return text2

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
        if ('instant' in self.types.lower()) or ('sorcery' in self.types.lower()):
            castMod = 'graveyard '
        else:
            allTypes = allTypes + ' permanent'
        if self.subtypes:
            allTypes = allTypes + ' ' + self.subtypes.lower()
            allTypes = allTypes.replace('[]', '') #weird [] for empty subtypes
        
        MCnoRep=MC
        lastsize=-1
        while not lastsize == len(MCnoRep):
            lastsize=len(MCnoRep)
            MCnoRep = MCnoRep.replace("} {","}{")\
                .replace("{w}{w}","{w}")\
                .replace("{u}{u}","{u}")\
                .replace("{b}{b}","{b}")\
                .replace("{r}{r}","{r}")\
                .replace("{g}{g}","{g}")\
                .replace("{c}{c}","{c}")\
                .replace("{1}{1}","{1}") 

        #Casting gets a something
        castText = MC + ' ' + allTypes + ' : cast ' + castMod + ' ' + allTypes \
            + MCnoRep.replace('{w}', ' white ').replace('{u}', ' blue ') \
            .replace('{b}', ' black ').replace('{r}', ' red ')\
            .replace('{g}', ' green ').replace('{c}', ' colorless ') \
            .replace('{1}', '')+ '\n'
        #for m in range(1,self.biggestMannaNumber):
        #    castText=castText.replace('{'+str(m)+'}', '')
        
        # keep high information words
        text = self.convertManaCosts(self.text)
        if isCreature:#creature somethings can attack
            text = text + 'attack unblock : damage \n' #merged conditions despite it hurting synergy measures
        subNames = self.name.lower().split(' // ')
        for name in subNames:
            #text = text.replace(name, allTypes)
            text = text.replace(name, "cardname")
        
        text=self.RemoveReminders(text)#keywords should be enough

        #basic land types have abilities in reminders (not good enough)
        if self.subtypes.find("Plains")>-1:
            text=text+"\r\n{t}:{w}"
        if self.subtypes.find("Island")>-1:
            text=text+"\r\n{t}:{u}"
        if self.subtypes.find("Swamp")>-1:
            text=text+"\r\n{t}:{b}"
        if self.subtypes.find("Mountain")>-1:
            text=text+"\r\n{t}:{r}"
        if self.subtypes.find("Forest")>-1:
            text=text+"\r\n{t}:{g}"

        text = text.replace('end of turn', 'endOfTurn') \
            .replace('this turn', 'thisTurn') \
            .replace('\ni ', '\nturn counter: ') \
            .replace('\nii ', '\nturn counter: ') \
            .replace('\niii ', '\nturn counter: ') \
            .replace('\niv ', '\nturn counter: ') \
            .replace('turn', 'untap draw attack') \
            .replace('if able', 'if_able') \
            .replace('only if', 'if_only') \
            .replace('when able', 'if_able') \
            .replace('only when', 'if_only') \
            .replace('proliferate', 'counter') \
            .replace('counter target', 'cast to graveyard') \
            .replace('\n•', ' ') \
            .replace('combat', 'attack') \
            .replace('is every creature type', 'changeling') \
            .replace('.', '') \
            .replace('{t}', 'tap untap') \
            .replace('sacrifice', 'sacrifice graveyard') \
            .replace('for each basic land type among lands you control', 'domain {w} {u} {b} {r} {g}')
        #use checkCards.py to check for some less useful words
        #roughly 300000 words;
        # #1/3 in top 100 but only ~10000 per biggest
        #most seem to be keywords
        #probably not worth keeping these:
        text = text.replace(' the ', ' ') \
            .replace(' a ', ' ') \
            .replace(' you ', ' ') \
            .replace(' of ', ' ') \
            .replace(' to ', ' ') \
            .replace(' your ', ' ') \
            .replace(' card ', ' ') \
            .replace(' this ', ' ') \
            .replace(' it ', ' ') \
            .replace(' that ', ' ') \
            .replace(' on ', ' ') \
            .replace(' its ', ' ') \
            .replace(' as ', ' ') \
            .replace(' an ', ' ') \
            .replace(' at ', ' ') \
            .replace(' is ', ' ') \
            .replace(' in ', ' ') \
            .replace(' has ', ' ') \
            .replace(' be ', ' ')
        #todo: figure out how to add cast info without making matching trivial
        # ... maybe another cast of trigger/events?
        withMana = castText + text
        if verbose:
            print(withMana)
        blocks = withMana.split('\n')
        # blocks = text.split('\n')
        for block in blocks:
            if(block.find("when")>-1): #activated
                block2=block
            else:
                block2=block.replace(',','')
            activated = block2.split(':', 1)            
            if len(activated) == 2:
                if(activated[1].find('when')>-1):
                    triggered = activated[1].split(',', 1)
                    if len(triggered) == 2:
                        trigger = activated[0] + ' ' + triggered[0]
                        event = triggered[1]
                    else:
                        trigger = activated[0]
                        event = activated[1]
                else:
                    trigger = activated[0]
                    event = activated[1]
            else:
                triggered = block2.split(',', 1)
                if len(triggered) == 2:
                    trigger = triggered[0]
                    event = triggered[1]
                else:
                    trigger = ''#'STATIC' #want something for weighted matching
                    event = block
            #consider error checking here for empty trigger/event
            trigger=self.parseManaForTrigger(trigger)
            event=self.parseManaForEvent(event)
            #played right, triggers are events...
            #{t}->untap already... event = event.replace('untap', '{t}')  # using untap(effect) and {t}(cost) as a synergy pair
            if(block.find("sacrifice")>-1):
                event=event + "graveyard"
            trigger = trigger.replace(',', '')
            event = event.replace(',', '')
            # sacrifice adds to the events
            trigger = list(filter(None, trigger.split(' ')))
            trigger.sort()  # mtg does not seem to care too much about order target red creature vs if red target
            event = list(filter(None, event.split(' ')))
            event.sort()
            self.Triggers = self.Triggers + [trigger]
            self.Events = self.Events + [event]
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
        if Card.ParseTextEnabled:
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
        d0 = tCost + sCost
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
    def LevenshteinDistance1(s, t, fine, showTable, sCost=1, tCost=1):
        m = len(s)
        n = len(t)
        if n == 0:
            return 1
        if m == 0:
            return 1
        scale = 1 / (n * tCost + m * sCost)

        v0 = np.zeros(n + 1)
        v1 = np.zeros(n + 1)
        for i in range(n + 1):
            v0[i] = i * tCost

        d0 = tCost + sCost
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

    def bestCornerToCorner(self,cost):
        rs=cost.shape[0]
        if(rs==0):
            return 1
        cs=cost.shape[1]
        if(cs==0):
            return 1
        total=cost*0
        total[0,0]=cost[0,0]
        for row in range(1,rs):
            total[row,0]=cost[row,0]+total[row-1,0]
        for col in range(1,cs):
            total[0,col]=cost[0,col]+total[0,col-1]
        for row in range(1,rs):            
            for col in range(1,cs):
                total[row,col]=cost[row,col]+np.min([total[row-1,col],total[row,col-1],total[row-1,col-1]])
        return total[rs-1,cs-1]

    def synergyL(self, card:'Card', synSimType = 0, fine=False, showTable=False, printInfo=False):
        #meanCost = 0        
        if synSimType==0 :
            tmp = np.ones([len(self.Triggers), len(card.Events)])*float('inf')
            for t in range(len(self.Triggers)):
                for e in range(len(card.Events)):
                    tmp[t, e] = Card.LevenshteinDistance1(self.Triggers[t], card.Events[e], fine, False, 1, 1)
        elif synSimType==1 :
            tmp = np.ones([len(self.Events), len(card.Events)])*float('inf')
            for t in range(len(self.Events)):
                for e in range(len(card.Events)):
                    tmp[t, e] =  Card.LevenshteinDistance1(self.Events[t], card.Events[e], fine, False, 1, 1)
        else :
            tmp = np.ones([len(self.Triggers), len(card.Triggers)])*float('inf')
            for t in range(len(self.Triggers)):
                for e in range(len(card.Triggers)):
                    tmp[t, e] = Card.LevenshteinDistance1(self.Triggers[t], card.Triggers[e], fine, False, 1, 1)        
        if synSimType > 0:
            bestCost=-self.bestCornerToCorner(tmp)/self.bestCornerToCorner(-tmp)
        else:
            bestCost=tmp.min()
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
                    x=max(0,min(x,tmp.shape[1]-1))
                    y=max(0,min(y,tmp.shape[0]-1))
                    #breakpoint()
                    if synSimType == 0:
                        Card.LevenshteinDistance1(self.Triggers[y], card.Events[x], fine, True, 1, 1)
                    elif synSimType == 1:
                        Card.LevenshteinDistance1(self.Events[y], card.Events[x], fine, True, 1, 1)                        
                    else: 
                        Card.LevenshteinDistance1(self.Triggers[y], card.Triggers[x], fine, True, 1, 1)
            plt.connect('button_press_event', on_click)
            plt.show()
        return -bestCost

    @staticmethod
    def Jaro(s, t, fine, showTable, radius=0.5):
        if fine or showTable:
            print("fine and showTable not supproted")
            return 1/0;
        #https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance
        R=int(max(len(s),len(t))*radius-1)
        M=0
        T=0
        LS=len(s)
        LT=len(t)
        lastOffset=0
        okay=dict()
        Lm=max(LS,LT)
        for indT in range(-R,R+Lm):
            if 0<=indT and indT<LT:
                okay[indT]=True
            else:
                okay[indT]=False
        for indS in range(LS):
            indT=indS+lastOffset;
            if okay[indT]:
                if s[indS]==t[indT]:
                    M=M+1
                    okay[indT]=False
                    continue;
            for offset in range(-R,R+1):
                indT=indS+offset
                if okay[indT]:
                    if s[indS]==t[indT]:
                        if M>0:
                            #if fine:#partial penalization; this costs ~10% of the time, may want to disable fine
                            #    dT=Card.Jaro(s[indS],t[indT],False,showTable)
                            #else:
                            #    dT=1
                            #T=T+dT
                            T=T+1
                        M=M+1
                        okay[indT]=False
                        lastOffset=offset
                        break;
        if M==0:
            return 1#-0 cost
        T=np.floor(T/2)
        J=(M/LS+M/LT+(M-T)/M)/3
        return 1-J;#cost



    
    def synergyJ(self, card:'Card', synSimType = 0, fine=False, showTable=False, printInfo=False):
        # Levenshtein is slow...
        # awsome comparison of string matching techniques on a name data set:
        # http://users.cecs.anu.edu.au/~Peter.Christen/publications/tr-cs-06-02.pdf
        # looks like Jaro is pretty good
        if synSimType==0 :
            tmp = np.ones([len(self.Triggers), len(card.Events)])*float('inf')
            for t in range(len(self.Triggers)):
                for e in range(len(card.Events)):
                    tmp[t, e] = Card.Jaro(self.Triggers[t], card.Events[e], fine, False)
        elif synSimType==1 :
            tmp = np.ones([len(self.Events), len(card.Events)])*float('inf')
            for t in range(len(self.Events)):
                for e in range(len(card.Events)):
                    tmp[t, e] =  Card.Jaro(self.Events[t], card.Events[e], fine, False)
        else :
            tmp = np.ones([len(self.Triggers), len(card.Triggers)])*float('inf')
            for t in range(len(self.Triggers)):
                for e in range(len(card.Triggers)):
                    tmp[t, e] = Card.Jaro(self.Triggers[t], card.Triggers[e], fine, False)        
        if synSimType > 0:
            bestCost=-self.bestCornerToCorner(tmp)/self.bestCornerToCorner(-tmp)
        else:
            bestCost=tmp.min()
        if printInfo:
            print(self.name + '\n' + str(self.Triggers) + '\n'
                  + card.name + '\n' + str(card.Events) + '\n'
                  + str(tmp))

        if showTable:
            print("visualization not supported")
        return -bestCost


    def ColorID(self):
        #ment for typical dragons... cards like wildfires will be improperly marked
        if self.manacost :
            MC=self.manacost
        else:
            MC=""
        w="{W" in self.text or "W}" in self.text or "W" in MC or 'Plains' in self.text or 'Domain' in self.text
        u="{U" in self.text or "U}" in self.text or "U" in MC or 'Island' in self.text or 'Domain' in self.text
        b="{B" in self.text or "B}" in self.text or "B" in MC or 'Swamp' in self.text or 'Domain' in self.text
        r="{R" in self.text or "R}" in self.text or "R" in MC or 'Mountain' in self.text or 'Domain' in self.text
        g="{G" in self.text or "G}" in self.text or "G" in MC or 'Forest' in self.text or 'Domain' in self.text
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



if __name__ == '__main__':
    #https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance
    print(str(Card.Jaro('FAREMVIEL','FARMVILLE',False,False)))#.88
    print(str(Card.Jaro('FARMVILLE','FAREMVIEL',False,False)))
    print(str(Card.LevenshteinDistance1('FAREMVIEL','FARMVILLE',False,False)))
    print(str(Card.LevenshteinDistance1('FARMVILLE','FAREMVIEL',False,False)))
    #https://www.geeksforgeeks.org/jaro-and-jaro-winkler-similarity/
    print(str(Card.Jaro('arnab','raanb',False,False)))#.8667
    print(str(Card.LevenshteinDistance1('arnab','raanb',False,False)))
    print(str(Card.Jaro('box','car',False,False)))
    print(str(Card.LevenshteinDistance1('box','car',False,False)))
    from time import *
    t0=time()
    for trial in range(10):
        Card.Jaro('arnab','raanb',False,False)
        Card.Jaro('FARMVILLE','FAREMVIEL',False,False)
    t1=time()
    print("Jaro: "+str(t1-t0)+"s")
    t0=time()
    for trial in range(10):
        Card.LevenshteinDistance1('arnab','raanb',False,False)
        Card.LevenshteinDistance1('FARMVILLE','FAREMVIEL',False,False)
    t1=time()    
    print("Levenshtein: "+str(t1-t0)+"s")
