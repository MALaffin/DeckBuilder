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
        self.card1ind=-1
        self.imageXind=-1
        self.imageYind=-1
        def on_click1L(event):
            self.dimY.select_clear()
            self.imageYind=self.card1ind
            self.updateScatter()
        def on_click1R(event):
            self.dimX.select_clear()
            self.imageXind=self.card1ind
            self.updateScatter()
        self.card.bind('<ButtonRelease-1>', on_click1L)
        self.card.bind('<ButtonRelease-2>', on_click1R)
        self.card.bind('<ButtonRelease-3>', on_click1R)

        #another card
        self.card2 = Canvas(self.mainWindow) 
        self.card2.place(relx=0.5, rely=0.65, relwidth=0.15, relheight=0.3)
        self.imTk2=None
        self.cardIm2=self.card2.create_image(0,0, anchor=NW)
        self.card2ind=-1
        def on_click2L(event):
            self.dimY.select_clear()
            self.imageYind=self.card2ind
            self.updateScatter()
        def on_click2R(event):
            self.dimX.select_clear()
            self.imageXind=self.card2ind
            self.updateScatter()
        self.card2.bind('<ButtonRelease-1>', on_click2L)
        self.card2.bind('<ButtonRelease-2>', on_click2R)
        self.card2.bind('<ButtonRelease-3>', on_click2R)


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

        self.fig=Figure()
        self.plt1 = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig,master = self.mainWindow)  
        self.canvas.get_tk_widget().place(relx=0.40, rely=0.05,relwidth=0.45, relheight=0.45)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.mainWindow, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.place(relx=0.40, rely=0.50,relwidth=0.45, relheight=0.1)
        self.canvas.draw()
        def on_click(event):        
            ax1=self.fig.get_axes()[0]
            if event.button is MouseButton.LEFT:
                point = ax1.transData.inverted().transform([event.x, event.y])
                print('x=' + str(point[0]) + ' y=' + str(point[1]))
                self.updateCard2(point[0],point[1])
        self.canvas.mpl_connect('button_press_event', on_click)
        self.CP=None
        self.cardDist=None
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
        
        cn=self.cards.selection_get()
        cardInd=self.CP.cards.findCards([cn])
        self.card1ind=cardInd[0]
        card=self.CP.cards.internalSet[cardInd[0]]
        imLoc=getImageLocByMultiverseId(card.multiverseid)
        x=self.card.winfo_width()
        y=self.card.winfo_height()
        im=Image.open(imLoc)
        im2=im.resize((x,y))
        self.imTk=ImageTk.PhotoImage(im2)
        self.card.itemconfig(self.cardIm, image=self.imTk)

    def updateCard2(self,x,y):
        if(self.dimsVarX is None or self.dimsVarY is None):
            return
        dx=self.dimsVarX-x;
        dy=self.dimsVarY-y;
        dx2Pdy2=dx*dx+dy*dy
        cardInd=dx2Pdy2.argmin()
        self.card2ind=cardInd
        card=self.CP.cards.internalSet[cardInd]
        imLoc=getImageLocByMultiverseId(card.multiverseid)
        x=self.card2.winfo_width()
        y=self.card2.winfo_height()
        im=Image.open(imLoc)
        im2=im.resize((x,y))
        self.imTk2=ImageTk.PhotoImage(im2)
        self.card2.itemconfig(self.cardIm2, image=self.imTk2)


    def plotHelper(self,xPCA,yPCA,dimX,dimY,SelectedDeck,color,marker,setVars=False):
        makeDist=True
        if(makeDist and self.cardDist is None):
            #df=DiffHelper(self.CP.CardMatch)
            #self.cardDist = df.L2distPar()
            self.cardDist = L2dist(self.CP.CardMatch)
        if(xPCA == 'pca'):
            X3=self.CP.PCAscore[SelectedDeck,int(self.dimsInds[dimX])]
        elif(xPCA == 'card'):
            X3=self.CP.CardMatch[SelectedDeck,int(self.dimsInds[dimX])]
        else:
            if(makeDist):
                X3=self.cardDist[SelectedDeck,int(self.imageXind)]
            else:
                X3=self.CP.CardMatch[SelectedDeck,int(self.imageXind)]
        if(yPCA == 'pca'):
            Y3=self.CP.PCAscore[SelectedDeck,int(self.dimsInds[dimY])]
        elif(yPCA == 'card'):
            Y3=self.CP.CardMatch[SelectedDeck,int(self.dimsInds[dimY])]
        else:
            if makeDist:
                Y3=self.cardDist[SelectedDeck,int(self.imageYind)]
            else:
                Y3=self.CP.CardMatch[SelectedDeck,int(self.imageYind)]
        if(setVars):
            self.dimsVarX=X3
            self.dimsVarY=Y3
        self.plt1.plot(X3,Y3,color=color,marker=marker,linestyle = 'None')

    def updateScatter(self):
        
        dimX=self.dimX.current()
        if dimX < 0:
            return
        dimY=self.dimY.current()
        if dimY < 0:
            return

        if not (self.imageXind == -1):
            xPCA='image'
        elif(self.dims[dimX].find('PCA')==0):
            xPCA='pca'
        else:
            xPCA='card'
        if not (self.imageYind == -1):
            yPCA='image'
        elif(self.dims[dimY].find('PCA')==0):
            yPCA='pca'
        else:
            yPCA='card'

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
        self.plotHelper(xPCA,yPCA,dimX,dimY,allcards,(0,0,0),',',True)
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
            ,MatchType = 0
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
        
        def updateCallbackX(event):
            self.imageXind=-1
            self.updateScatter()
        def updateCallbackY(event):
            self.imageYind=-1
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
        self.dimX.bind("<<ComboboxSelected>>", updateCallbackX)
        self.dimY.bind("<<ComboboxSelected>>", updateCallbackY)
        
        




if __name__ == '__main__':

    CPV=CardProjectViewer()