from tkinter import Tk, Frame, LabelFrame, Label, Button, Listbox, Radiobutton, Scale, messagebox, simpledialog, END
from tkinter.ttk import Separator
from PIL import ImageTk, Image
from yeelight import Bulb, discover_bulbs
from scapy.layers.inet import IP, ICMP
from scapy.layers.l2 import ARP, getmacbyip
from scapy.sendrecv import sr1
import pickle
import sys
import os
import re


main = Tk()
main.title("Easy Yeelight")
main.iconbitmap("img/icon.ico")
main.geometry("500x400+400+300")
main.resizable(False, False)

bg_color = "#696969"


# Using resize method while the size is not defined.
imgOff = ImageTk.PhotoImage(Image.open(
    'img/bulb_off.png').resize((60, 120), Image.ANTIALIAS))
imgOn = ImageTk.PhotoImage(Image.open(
    'img/bulb_on.png').resize((60, 120), Image.ANTIALIAS))
imgRgb = ImageTk.PhotoImage(Image.open(
    'img/rgb_scale.png').resize((250, 10), Image.ANTIALIAS))


def discoverIp():
    infos = discover_bulbs()
    devs = []
    if infos:
        for d in infos:
            dev = {d['capabilities']['id']: d['ip']}
            devs.append(dev)
        return devs
    else:
        return None


def saveBulbs(**kwargs):
    try:
        if not kwargs:
            with (open("yee.pkl", "rb")) as data:
                bulbPopulate(pickle.load(data))
        else:
            name = simpledialog.askstring(
                "Add Device", "Type the name of the Bulb")
            if name == None:
                return
            elif name == "" or len(name) > 20:
                messagebox.showerror("Add Device", "Invalid Name")
                return
            idt = {kwargs["id"]: kwargs["ip"]}
            newData = {}
            try:
                with (open('yee.pkl', 'rb')) as saveData:
                    saved = pickle.load(saveData)
                    saved[name] = idt
                    newData = saved
                with (open('yee.pkl', 'wb')) as saveData:
                    pickle.dump(newData, saveData)
                bulbPopulate(newData)
            except (FileNotFoundError, EOFError):
                newData[name] = idt
                with (open('yee.pkl', 'wb')) as saveData:
                    pickle.dump(newData, saveData)
                bulbPopulate(newData)
    except FileNotFoundError:
        pass
    except EOFError:
        os.remove('yee.pkl')


def verifyState(b):
    return True if b.get_properties()["power"] == 'on' else False


def ipConfirm(ip):
    ping = sr1(IP(dst=ip)/ICMP(), timeout=1)
    if ping == None:
        return False
    else:
        return True


def ipPopulate(devs):
    ip_list.delete(0, END)
    if devs:
        for d in devs:
            for id, ip in d.items():
                bulb_id = id
                bulb_ip = ip
                ip_list.insert(END, bulb_ip + "  -  " + bulb_id)
        add_button["state"] = "active"
    else:
        ip_list.insert(END, "No devices found")
        ip_list.insert(END, "Try power on and off")
        ip_list.insert(END, "Or restart local network")


def addDevice():
    sel = ip_list.curselection()
    if sel:
        x = re.sub(r"\s+", "", ip_list.get(sel))
        x = x.split("-")
        ip = x[0]
        id = x[1]
        saveBulbs(id=id, ip=ip)
    else:
        messagebox.showerror("Add Device", "Please, select one IP first")


def bulbPopulate(bulbs):
    i = 0
    for b, v in bulbs.items():
        ip = (list(v.values())[0])
        bulb = Bulb(ip)
        dev_op = Radiobutton(devices_frame, text=b, bg=bg_color, width=20,
                             activebackground=bg_color, indicatoron=0, variable="bulbsOp", value=b,
                             command=lambda: activateBulb(bulb))
        dev_op.grid(column=0, row=i, padx=5, pady=5)
        i += 1


def activateBulb(b):
    refreshImgState(b)
    on.configure(command=lambda: bulb_on(b), state="active")
    off.configure(command=lambda: bulb_off(b), state="active")
    ip_label.configure(text=b._ip)
    model_label.configure(text=re.sub(r"BulbType\.", "", str(b.bulb_type)))


def refreshImgState(b):
    bulbImg.configure(image=imgOn if verifyState(b) else imgOff)


def bulb_on(b):
    b.turn_on()
    bulbImg.configure(image=imgOn)


def bulb_off(b):
    b.turn_off()
    bulbImg.configure(image=imgOff)


search_frame = Frame(main, bg=bg_color, width=200, height=400)
control_frame = Frame(main, width=300, height=400)
devices_frame = Frame(search_frame, bg=bg_color, width=180)

search_button = Button(search_frame, text="SEARCH", width=8,
                       command=lambda: ipPopulate(discoverIp()))
add_button = Button(search_frame, text="ADD", width=8,
                    state="disable", command=addDevice)
ip_list = Listbox(search_frame, width=29, height=6, relief="flat")
ip_list.insert(END, "Active LAN CONTROL first")
sep = Separator(search_frame, orient="horizontal")
devices_title = Label(search_frame, bg=bg_color,
                      text="DEVICES", font=('Sans-serif', '15', 'bold'))

info_lframe = LabelFrame(control_frame, text="Details", width=280, height=35)
ip_info_label = Label(info_lframe, text="IP Address:")
ip_label = Label(info_lframe, text="")
model_info_label = Label(info_lframe, text="Model:")
model_label = Label(info_lframe, text="")
bulbImg = Label(control_frame, image=imgOff)
on = Button(control_frame, text="ON", width=6, state="disable")
off = Button(control_frame, text="OFF", width=6, state="disable")
delete = Button(control_frame, text="Delete", width=6, state="disable")
brightness = Scale(control_frame, label="Brightness",
                   orient="horizontal", length=250, from_=1.0, to=100)
temp = Scale(control_frame, label="Temp", orient="horizontal",
             length=250, from_=1700, to=6500)
color = Scale(control_frame, label="Color",
              orient="horizontal", length=250, showvalue=0)
rgb_scale = Label(control_frame, image=imgRgb)

search_frame.grid(column=0, row=0, sticky="e")
search_frame.grid_propagate(0)
search_frame.columnconfigure(0, minsize=100)
search_frame.columnconfigure(1, minsize=100)
control_frame.grid(column=1, row=0, sticky="n")
control_frame.columnconfigure(0, minsize=150)
control_frame.columnconfigure(1, minsize=150)
devices_frame.grid(column=0, row=4, columnspan=2, pady=10)

search_button.grid(column=0, row=0, pady=10)
add_button.grid(column=1, row=0, pady=10)
ip_list.grid(column=0, row=1, columnspan=2, padx=5)
sep.grid(column=0, row=2, columnspan=2, pady=10, padx=10, sticky="ew")

devices_title.grid(column=0, row=3, columnspan=2)

info_lframe.grid(column=0, row=0, columnspan=4,
                 pady=5, padx=5, ipady=5, ipadx=5)
info_lframe.grid_propagate(0)
info_lframe.columnconfigure(1, minsize=100)
info_lframe.columnconfigure(3, minsize=50)
ip_info_label.grid(column=0, row=0)
ip_label.grid(column=1, row=0)
model_info_label.grid(column=2, row=0)
model_label.grid(column=3, row=0)
bulbImg.grid(column=0, row=1, rowspan=3, pady=5, padx=5)
on.grid(column=1, row=1)
off.grid(column=1, row=2)
delete.grid(column=1, row=3)
brightness.grid(column=0, row=4, columnspan=4)
temp.grid(column=0, row=5, columnspan=4)
color.grid(column=0, row=6, columnspan=4)
rgb_scale.grid(column=0, row=7, columnspan=4)

saveBulbs()
main.mainloop()
