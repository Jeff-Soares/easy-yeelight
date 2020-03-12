from tkinter import *
from yeelight import Bulb

tela = Tk()
tela.title("Controle da Yeelight")
tela.geometry("250x100+200+100")
Bulb = Bulb("192.168.15.6")

on = Button (tela, text = "Ligar", width = 10, command = Bulb.turn_on)
on.pack(side = "left", padx = 10, pady = 10)

off = Button (tela, text = "Desligar", width = 10, command = Bulb.turn_off)
off.pack(side = "left", padx = 10, pady = 10)

tela.mainloop()
