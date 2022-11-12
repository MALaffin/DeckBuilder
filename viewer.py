from tkinter import *

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)

mainWindow= Tk()
mainWindow.geometry("1200x800")

decks = Listbox(mainWindow)
decks.place(relx=.05, rely=0.05,relwidth=0.2, relheight=0.4)
decks.insert(1,'test1')


cards = Listbox(mainWindow)
cards.place(relx=0.05, rely=0.55,relwidth=0.2, relheight=0.4)
cards.insert(1,'test2')

button = Button(mainWindow, "Load", functionName)
#button.config(state=DISABLED) #while running disable it
button.place(relx=0.05, rely=0.55,relwidth=0.2, relheight=0.4)


# txt = Text(mainWindow)
# txt.place(relx=0.55, rely=0.05,relwidth=0.2, relheight=0.1)
# txt.insert(END,"text")
# txt.delete("1.0",END)
# txt.insert(END," text")

fig=Figure()
plt1 = fig.add_subplot(111)
plt1.plot([0, 1, 2, 3],[1, 2, 4, 16])
plt1.set_title("test3")
canvas = FigureCanvasTkAgg(fig,master = mainWindow)  
canvas.get_tk_widget().place(relx=0.45, rely=0.30,relwidth=0.5, relheight=0.5)
toolbar = NavigationToolbar2Tk(canvas, mainWindow, pack_toolbar=False)
toolbar.update()
toolbar.place(relx=0.45, rely=0.20,relwidth=0.5, relheight=0.1)
canvas.draw()


mainWindow.mainloop()