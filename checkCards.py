from MtgDbHelper import MtgDbHelper
from CardSet import CardSet
from Card import Card
import matplotlib.pyplot as plt
import numpy as np

helper=MtgDbHelper()
helper.initDb(False)
Card.ParseTextEnabled = False
K=100
words=dict()
c=0
cs=len(helper.cards.internalSet)
for card in helper.cards.internalSet:
    c=c+1
    if c%32==0:
        print(str(c)+' of '+str(cs))
    noPunc=card.text \
        .replace('\n•',' ') \
        .replace('\n',' ') \
        .replace('.',' ') \
        .replace(',',' ') \
        .lower()
    parsed=noPunc.split(' ')
    for word in parsed:
        if word in words.keys():
            words[word]=words[word]+1
        else:
            words[word]=1
vals=np.array(list(words.values()))
order = np.argsort(vals)
vals.sort()
vals=vals[::-1]
fig, (ax1) = plt.subplots(nrows=1, figsize=(4, 4))
plt.plot(np.log10(vals))
ax1.set_title('word frequency')
plt.show(block=False)
names=list(words.keys())
for ind in range(K):
    element=order[len(names)-1-ind]
    print(names[element])
print(np.sum(vals))
Card.ParseTextEnabled = True