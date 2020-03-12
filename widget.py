from tkinter import *
from yeelight import Bulb

main = Tk()
main.title("Easy Yeelight")
main.geometry("200x300+200+100")

Bulb = Bulb("192.168.15.6")
imgOff = PhotoImage(file='img/bulb_off.png')
imgOn = PhotoImage(file='img/bulb_on.png')

def bulb_on():
    Bulb.turn_on()
    bulbImg.configure(image=imgOn)

def bulb_off():
    Bulb.turn_off()
    bulbImg.configure(image=imgOff)

bulbImg = Label(main, image=imgOff)
bulbImg.pack(side="top", padx=10, pady=10)

on = Button(main, text="ON", width=10, command=bulb_on)
on.pack(side="left", padx=10, pady=10)

off = Button(main, text="OFF", width=10, command=bulb_off)
off.pack(side="right", padx=10, pady=10)

main.mainloop()
