from tkinter import *
from tkinter import ttk

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
        self.button.place(relx=0.05, rely=0.05,relwidth=0.1, relheight=0.05)
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
        #select X
        self.dimX = ttk.Combobox(self.mainWindow)
        self.dimX.place(relx=0.7, rely=0.65,relwidth=0.2, relheight=0.05)
        #select Y
        self.dimY = ttk.Combobox(self.mainWindow)
        self.dimY.place(relx=0.7, rely=0.75,relwidth=0.2, relheight=0.05)
        self.dimsVarX=None
        self.dimsVarY=None

        fig=Figure()
        plt1 = fig.add_subplot(111)
        plt1.plot([0, 1, 2, 3],[1, 2, 4, 16])
        plt1.set_title("test3")
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
        if(dn==0):
            decks=self.CP.deckNames
        else:
            decks=[self.CP.deckNames[dn[0]-1]]
        self.cards.delete(0,END)
        for dn in decks:
            with open(dn, "r") as f:
                name=f.readline().replace('\n',"")
                while name:
                    self.cards.insert(END,name)
                    name=f.readline().replace('\n',"")
            f.close()

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


    def SetupCardProject(self):
        self.button.config(state=DISABLED) #while running disable it
        names = ['The Mirari Conjecture', 'Power Conduit', 'Time Stretch'
            , 'Scion of the Ur-Dragon', 'Teneb, the Harvester'
            , 'Dragonsoul Knight', 'Bogardan Dragonheart'
            , 'Lathliss, Dragon Queen']
        names0 = ['The Mirari Conjecture', 'Power Conduit', 'Time Stretch']
        names0 = ['Scion of the Ur-Dragon', 'Teneb, the Harvester']
        self.CP=CardProject(namedCards=None)
        self.CP.createOrLoadData()
        self.button.config(state=ACTIVE) #while running disable it

        self.decks.insert(END,"All")
        for dn in self.CP.deckNames:
            self.decks.insert(END,dn)
        
        def deckCallback(event):
            self.updateCards()
        self.decks.bind("<<ListboxSelect>>", deckCallback)

        def cardCallback(event):
            self.updateCard()
        self.cards.bind("<<ListboxSelect>>", cardCallback)
        
        for BI in self.CP.BasisIndexes:
            self.dims.append(str(BI))
        self.dimX['values']=self.dims
        self.dimY['values']=self.dims
        # self.dimsVarX = StringVar(self.dims)
        # self.dimsVarX.set(self.dims[0]) # default value
        # self.dimsVarY = StringVar(self.dims)
        # self.dimsVarY.set(self.dims[0]) # default value
        
        




if __name__ == '__main__':

    CPV=CardProjectViewer()