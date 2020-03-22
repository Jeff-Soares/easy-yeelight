from tkinter import Tk, Frame, Label, Button, Listbox, END, StringVar
from PIL import ImageTk, Image
from yeelight import Bulb, discover_bulbs
from scapy.layers.inet import IP, ICMP
from scapy.layers.l2 import getmacbyip
from scapy.sendrecv import sr1
import pickle
import sys
import os


main = Tk()
main.title("Easy Yeelight")
main.geometry("500x400+400+300")
main.resizable(False, False)

# Using resize method while the size is not defined.
imgOff = ImageTk.PhotoImage(Image.open(
    'img/bulb_off.png').resize((60, 120), Image.ANTIALIAS))
imgOn = ImageTk.PhotoImage(Image.open(
    'img/bulb_on.png').resize((60, 120), Image.ANTIALIAS))


bulb = Bulb("192.168.15.2")


def discoverIp():
    infos = discover_bulbs()
    ips = []
    if infos:
        for b in infos:
            ips.append(b["ip"])
        return ips
    else:
        return


def saveBulbs():
    try:
        saveData = open('yee.pkl', 'rb')
        ip = pickle.load(saveData)
        if discoverIp() == ip:
            bulb = Bulb(ip)
        else:
            ip = None
    except FileNotFoundError:
        ip = discoverIp()
        if ip != None:
            saveData = open('yee.pkl', 'wb')
            pickle.dump(ip, saveData)
            bulb = Bulb(ip)
        else:
            print("discover fails")
    except EOFError:
        os.remove('yee.pkl')
    finally:
        if ip != None:
            saveData.close()
        else:
            print("system exit - try delete yee.pkl file")
            sys.exit(0)


def verifyState(b):
    return True if b.get_properties()["power"] == 'on' else False


def bulbIsOn(ip):
    ping = sr1(IP(dst=ip)/ICMP(), timeout=1)
    if ping == None:
        return False
    else:
        return True


def ipPopulate(ips):
    ip_list.delete(0, END)
    if ips != None:
        for ip in ips:
            ip_list.insert(END, ip + "   -   " + getmacbyip(ip))
    else:
        ip_list.insert(END, "No lamp found")
        ip_list.insert(END, "Try power on and off")


def bulb_on():
    bulb.turn_on()
    bulbImg.configure(image=imgOn)


def bulb_off():
    bulb.turn_off()
    bulbImg.configure(image=imgOff)


search_frame = Frame(main, bg="#696969", width=200, height=400)
control_frame = Frame(main, width=300, height=400)

ip_list = Listbox(search_frame, width=29, height=5, relief="flat")
bulbImg = Label(control_frame, image=imgOn if verifyState(bulb) else imgOff)
search_button = Button(search_frame, text="SEARCH", width=8,
                       command=lambda: ipPopulate(discoverIp()))
on = Button(control_frame, text="ON", width=8, command=bulb_on)
off = Button(control_frame, text="OFF", width=8, command=bulb_off)

search_frame.grid(column=0, row=0, sticky="e")
search_frame.grid_propagate(0)
search_frame.columnconfigure(0, minsize=100)
search_frame.columnconfigure(1, minsize=100)
control_frame.grid(column=1, row=0, sticky="n")
control_frame.columnconfigure(0, minsize=150)
control_frame.columnconfigure(1, minsize=150)

search_button.grid(column=0, row=0, columnspan=2, pady=5, padx=5)
ip_list.grid(column=0, row=1, columnspan=2, pady=5, padx=5)

bulbImg.grid(column=0, row=0, columnspan=2, pady=5, padx=5)
on.grid(column=0, row=1)
off.grid(column=1, row=1)

main.mainloop()
