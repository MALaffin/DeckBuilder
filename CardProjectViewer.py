from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

from CardProject import *
from GetImage import getImageLocByMultiverseId
from PIL import ImageTk, Image

class CardProjectViewer:
    def __init__(self) -> None:

        self.mainWindow= Tk()
        self.mainWindow.geometry("700x500")
        self.mainWindow.wm_aspect(7, 5, 7, 5)

        #load decks
        self.button = Button(self.mainWindow, text="Load", command=self.SetupCardProject)
        self.button.place(relx=0.05, rely=0.05,relwidth=0.09, relheight=0.05)
        #load deck
        self.adddeck = Button(self.mainWindow, text="Load Deck", command=self.setupdeck)
        self.adddeck.place(relx=0.16, rely=0.05,relwidth=0.09, relheight=0.05)
        #select decks
        self.decks = Listbox(self.mainWindow)#,justify="right")
        self.decks.place(relx=.05, rely=0.15,relwidth=0.2, relheight=0.2)
        #select card
        self.cards = Listbox(self.mainWindow)
        self.cards.place(relx=0.05, rely=0.4,relwidth=0.2, relheight=0.55)
        #a card
        self.card = Canvas(self.mainWindow) 
        self.card.place(relx=0.3, rely=0.65, relwidth=0.15, relheight=0.3)
        self.imTk=None
        self.cardIm=self.card.create_image(0,0, anchor=NW)
        #another card
        self.card2 = Canvas(self.mainWindow) 
        self.card2.place(relx=0.5, rely=0.65, relwidth=0.15, relheight=0.3)
        self.imTk2=None
        self.cardIm2=self.card2.create_image(0,0, anchor=NW)


        # txt = Text(mainWindow)
        # txt.place(relx=0.55, rely=0.05,relwidth=0.2, relheight=0.1)
        # txt.insert(END,"text")
        # txt.delete("1.0",END)
        # txt.insert(END," text")
        
        self.dims=[]
        self.dimsInds=[]
        #select X
        self.dimX = ttk.Combobox(self.mainWindow)
        self.dimX.place(relx=0.7, rely=0.65,relwidth=0.2, relheight=0.05)
        #select Y
        self.dimY = ttk.Combobox(self.mainWindow)
        self.dimY.place(relx=0.7, rely=0.75,relwidth=0.2, relheight=0.05)
        self.dimsVarX=None
        self.dimsVarY=None

        fig=Figure()
        self.plt1 = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig,master = self.mainWindow)  
        self.canvas.get_tk_widget().place(relx=0.40, rely=0.05,relwidth=0.45, relheight=0.45)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.mainWindow, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.place(relx=0.40, rely=0.50,relwidth=0.45, relheight=0.1)
        self.canvas.draw()

        self.CP=None
        self.mainWindow.mainloop()

    def updateCards(self):
        dn=self.decks.curselection()
        if len(dn) == 0:
            return
        self.decks.selection_get()
        if(dn==0):
            decks=self.CP.deckNames
        else:
            decks=[self.decks.selection_get()]
        self.cards.delete(0,END)
        for dn in decks:
            if not (".cod" in dn):
                with open(dn, "r") as f:
                    name=f.readline().replace('\n',"")
                    while name:
                        self.cards.insert(END,name)
                        name=f.readline().replace('\n',"")
                f.close()
            else:
                print("TODO: read cocatrice deck")

    def updateCard(self):
        cs=self.cards.curselection()
        if len(cs) == 0:
            return

        self.imTk2=self.imTk
        
        cn=self.cards.selection_get()
        cardInd=self.CP.cards.findCards([cn])
        card=self.CP.cards.internalSet[cardInd[0]]
        imLoc=getImageLocByMultiverseId(card.multiverseid)
        x=self.card.winfo_width()
        y=self.card.winfo_height()
        im=Image.open(imLoc)
        im2=im.resize((x,y))
        self.imTk=ImageTk.PhotoImage(im2)
        self.card.itemconfig(self.cardIm, image=self.imTk)

        self.card2.itemconfig(self.cardIm2, image=self.imTk2)

    def plotHelper(self,xPCA,yPCA,dimX,dimY,SelectedDeck,color,marker):
        if(xPCA):
            X3=self.CP.PCAscore[SelectedDeck,int(self.dimsInds[dimX])]
        else:
            X3=self.CP.CardMatch[SelectedDeck,int(self.dimsInds[dimX])]
        if(yPCA):
            Y3=self.CP.PCAscore[SelectedDeck,int(self.dimsInds[dimY])]
        else:
            Y3=self.CP.CardMatch[SelectedDeck,int(self.dimsInds[dimY])]
        self.plt1.plot(X3,Y3,color=color,marker=marker,linestyle = 'None')

    def updateScatter(self):
        
        dimX=self.dimX.current()
        if dimX < 0:
            return
        dimY=self.dimY.current()
        if dimY < 0:
            return

        xPCA=self.dims[dimX].find('PCA')==0
        yPCA=self.dims[dimY].find('PCA')==0

        cardX=self.CP.cards.internalSet[int(self.dimsInds[dimX])]
        cardY=self.CP.cards.internalSet[int(self.dimsInds[dimY])]
        self.plt1.cla()
        dn=self.decks.curselection()
        if len(dn) != 0:
            SelectedDeck=self.CP.updatedBelonging[dn[0]-1]
            self.plotHelper(xPCA,yPCA,dimX,dimY,SelectedDeck,(1,0,0),'o')
        AllDecks=[]
        for d in self.CP.updatedBelonging:
            if len(d)>0:
                AllDecks=AllDecks+d
        self.plotHelper(xPCA,yPCA,dimX,dimY,AllDecks,(0,1,0),'.')
        allcards=range(len(self.CP.cards.internalSet))
        self.plotHelper(xPCA,yPCA,dimX,dimY,allcards,(0,0,0),',')
        self.plt1.set_title("test3")
        self.plt1.set_xlabel(cardX.name)
        self.plt1.set_ylabel(cardY.name)
        self.canvas.draw()

    def setupdeck(self): 
        #file dialog and add to decks
        names=fd.askopenfilenames(initialdir="/media/VMShare/")
        for dn in names:
            self.decks.insert(END,dn)

    def SetupCardProject(self): 
        self.button.config(state=DISABLED) #while running disable it
        names = ['The Mirari Conjecture', 'Power Conduit', 'Time Stretch'
            , 'Scion of the Ur-Dragon', 'Teneb, the Harvester'
            , 'Dragonsoul Knight', 'Bogardan Dragonheart'
            , 'Lathliss, Dragon Queen']
        names0 = ['The Mirari Conjecture', 'Power Conduit', 'Time Stretch']
        names0 = ['Scion of the Ur-Dragon', 'Teneb, the Harvester']
        self.CP=CardProject(namedCards=None
            ,MatchType = 1
            ,fine = False)
        self.CP.createOrLoadData()
        self.button.config(state=ACTIVE) #while running disable it

        self.decks.insert(END,"All")
        for dn in self.CP.deckNames:
            self.decks.insert(END,dn)
        
        def deckCallback(event):
            self.updateCards()
            self.updateScatter()
        self.decks.bind("<<ListboxSelect>>", deckCallback)

        def cardCallback(event):
            self.updateCard()
        self.cards.bind("<<ListboxSelect>>", cardCallback)
        
        def updateCallback(event):
            self.updateScatter()
        for ind in range(5):
            self.dims.append('PCA'+str(ind+1))
            self.dimsInds.append(ind)
        for names in self.CP.deckSeeds:
            self.dims.append(names[0])
            inds=self.CP.cards.findCards(names)
            self.dimsInds.append(inds[0])
        for BI in self.CP.BasisIndexes:
            self.dimsInds.append(BI)
            card=self.CP.cards.internalSet[BI]
            self.dims.append(card.name)
        self.dimX['values']=self.dims
        self.dimY['values']=self.dims
        self.dimX.bind("<<ComboboxSelected>>", updateCallback)
        self.dimY.bind("<<ComboboxSelected>>", updateCallback)
        
        




if __name__ == '__main__':

    CPV=CardProjectViewer()