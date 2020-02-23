
from ui.Interface import *

fenetre = Tk()
interface = Interface(fenetre)
fenetre.title("Meilleures cotes")
fenetre.tk.call('wm', 'iconphoto', fenetre._w, PhotoImage(file='resources/icon.png'))
interface.mainloop()
interface.destroy()