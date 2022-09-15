from MtgDbHelper import MtgDbHelper
from CardSet import CardSet

helper=MtgDbHelper()
helper.initDb(False)
check1=CardSet(helper.cards.findCards2(name="Ancient",equalsNotLike=False))
check2=check1.findCards2(name="Dragon",equalsNotLike=False)
Core=helper.cards.get(True,False)
CS=helper.cards.get(True,True)
print("CORE:"+str(len(Core)+len(CS)))
Symp=helper.cards.get(False,True)
print("Sympathetic:"+str(len(Symp)))
Util=helper.cards.get(False,False)
print("Util:"+str(len(Util)))
print("Sympathetic:"+str(len(Symp)))
print("CORE:"+str(len(Core)+len(CS)))