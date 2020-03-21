from tkinter import Tk, PhotoImage, Label, Button
from PIL import ImageTk, Image
from yeelight import Bulb, discover_bulbs

main = Tk()
main.title("Easy Yeelight")
main.geometry("300x400+400+300")
main.resizable(False, False)

# Using resize method while the size is not defined.
imgOff = ImageTk.PhotoImage(Image.open(
    'img/bulb_off.png').resize((60, 120), Image.ANTIALIAS))
imgOn = ImageTk.PhotoImage(Image.open(
    'img/bulb_on.png').resize((60, 120), Image.ANTIALIAS))

# Standard value, will be changed to "" later
bulb = Bulb("192.168.15.2")


def verifyState(b):
    return True if b.get_properties()["power"] == 'on' else False


def bulb_on():
    bulb.turn_on()
    bulbImg.configure(image=imgOn)


def bulb_off():
    bulb.turn_off()
    bulbImg.configure(image=imgOff)


bulbImg = Label(main, image=imgOn if verifyState(bulb) else imgOff)
on = Button(main, text="ON", width=8, command=bulb_on)
off = Button(main, text="OFF", width=8, command=bulb_off)

bulbImg.grid(column=0, row=0, columnspan=2, pady=5, padx=5)
on.grid(column=0, row=1)
off.grid(column=1, row=1)

main.mainloop()
