from tkinter import (Tk, Frame, PhotoImage, LabelFrame, Label, Button, Listbox, Canvas,
                     Radiobutton, Scale, colorchooser, messagebox, simpledialog, StringVar, IntVar, END)
from tkinter.ttk import Separator, Scrollbar, Style
from yeelight import Bulb, discover_bulbs, BulbException
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
imgOff = PhotoImage(file='img/bulb_off.png')
imgOn = PhotoImage(file='img/bulb_on.png')
imgRgb = PhotoImage(file='img/hsv_bar.png')
bulbsOp = StringVar()


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


def startSavedDevices():
    try:
        with (open("yee.pkl", "rb")) as data:
            bulbPopulate(pickle.load(data))
    except FileNotFoundError:
        return
    except EOFError:
        os.remove('yee.pkl')


def addDevice():
    sel = ip_list.curselection()
    if sel:
        x = re.sub(r"\s+", "", ip_list.get(sel))
        x = x.split("-")
        ip = x[0]
        id = x[1]
        saveDevice(id=id, ip=ip)
    else:
        messagebox.showerror("Add Device", "Please, select one IP first")


def saveDevice(id, ip):
    file = "yee.pkl"
    idt = {id: ip}
    name = simpledialog.askstring("Add Device", "Type the name of the Bulb")
    if name == None:
        return
    elif name == "" or len(name) > 20:
        messagebox.showerror("Add Device", "Invalid Name")
        return
    try:
        with (open(file, 'rb')) as savedData:
            data = pickle.load(savedData)
            for v in data.values():
                if v == idt:
                    messagebox.showerror(
                        "Add Device", "This device is already registred.")
                    return
            data[name] = idt
            with (open(file, 'wb')) as savedData:
                pickle.dump(data, savedData)
            bulbPopulate(data)
    except FileNotFoundError:
        newData = {name: idt}
        with (open(file, 'wb')) as savedData:
            pickle.dump(newData, savedData)
        bulbPopulate(newData)
    except EOFError:
        os.remove(file)


def deleteDevice(name):
    op = messagebox.askyesno(
        "Delete device", "Are you sure you want to delete: "+name)
    if op:
        with (open('yee.pkl', 'rb')) as saveData:
            newData = pickle.load(saveData)
            del newData[name]
            with (open('yee.pkl', 'wb')) as saveData:
                pickle.dump(newData, saveData)
        disableControls()
        bulbsOp.set("")
        bulbPopulate(newData)


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


def bulbPopulate(bulbs):
    if len(devices.children) > 0:
        for widgets in devices.winfo_children():
            widgets.destroy()
    i = 0
    for name, v in bulbs.items():
        ip = (list(v.values())[0])
        bulb = Bulb(ip)
        dev_op = Radiobutton(devices, text=name, bg=bg_color, selectcolor=bg_color,
                             width=24, offrelief="flat", overrelief="ridge", indicatoron=0,
                             variable=bulbsOp, value=name, padx=1,
                             command=lambda name=name, bulb=bulb: activateBulb(name, bulb))
        dev_op.grid(column=0, row=i, pady=1)
        i += 1


def activateBulb(name, b):
    on.configure(command=lambda: bulb_on(b), state="active")
    off.configure(command=lambda: bulb_off(b), state="active")
    rgb.configure(command=lambda: change_color_RGB(b), state="active")
    delete.configure(
        command=lambda: deleteDevice(name), state="active")
    brightness.configure(state="active")
    temp.configure(state="active")
    color.configure(state="active")
    brightness.bind("<ButtonRelease-1>", lambda event,
                    b=b: change_brightness(event, b))
    temp.bind("<ButtonRelease-1>", lambda event,
              b=b: change_temp(event, b))
    color.bind("<ButtonRelease-1>", lambda event,
               b=b: change_color(event, b))
    ip_label.configure(text=b._ip)
    model_label.configure(text=re.sub(r"BulbType\.", "", str(b.bulb_type)))
    refreshState(b)


def refreshState(b):
    try:
        state = b.get_properties(["power", "bright", "ct", "hue"])
        bulbImg.configure(image=imgOn if state["power"] == "on" else imgOff)
        brightnessInt.set(state["bright"])
        tempInt.set(state["ct"])
        colorInt.set(state["hue"])
    except BulbException:
        if not ipConfirm(b._ip):
            messagebox.showerror(
                "Conection error", "IP: "+b._ip+" is not responding. Make sure the lamp is on.")
        else:
            messagebox.showerror(
                "Socket error", "A socket error has occurred or you have sent too many commands and exceeded the limit")
        disableControls()


def bulb_on(b):
    b.turn_on()
    bulbImg.configure(image=imgOn)


def bulb_off(b):
    b.turn_off()
    bulbImg.configure(image=imgOff)


def change_brightness(event, b):
    b.set_brightness(brightness.get())


def change_temp(event, b):
    b.set_color_temp(temp.get())


def change_color(event, b):
    b.set_hsv(color.get(), 100)


def change_color_RGB(b):
    currentColor = hex(int(b.get_properties(["rgb"])[
                       "rgb"])).split("x")[-1].zfill(6)
    result = colorchooser.askcolor("#"+currentColor)[0]
    if result:
        red = int(result[0])
        green = int(result[1])
        blue = int(result[2])
        b.set_rgb(red, green, blue)


def disableControls():
    on.configure(state="disable")
    off.configure(state="disable")
    rgb.configure(state="disable")
    brightness.configure(state="disable")
    temp.configure(state="disable")
    color.configure(state="disable")
    brightness.unbind("<ButtonRelease-1>")
    temp.unbind("<ButtonRelease-1>")
    color.unbind("<ButtonRelease-1>")


search_frame = Frame(main, bg=bg_color, width=200, height=400)
control_frame = Frame(main, width=300, height=400)
devices_frame = Frame(search_frame, bg=bg_color, width=180)
devices_canvas = Canvas(devices_frame, bg=bg_color, bd=0, highlightthickness=0, width=180, height=188)
s = Style()
s.configure('Vertical.TScrollbar', background="green")
devices_scrollbar = Scrollbar(devices_frame, style="Vertical.TScrollbar", orient="vertical", command=devices_canvas.yview)
devices = Frame(devices_canvas, bg=bg_color, width=160)
devices.bind(
    "<Configure>",
    lambda e: devices_canvas.configure(
        scrollregion=devices_canvas.bbox("all")
    )
)
devices_canvas.create_window((0,0), window=devices, anchor="nw")
devices_canvas.configure(yscrollcommand=devices_scrollbar.set)

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
rgb = Button(control_frame, text="RGB", width=6, state="disable")
delete = Button(control_frame, text="Delete", width=6, state="disable")
brightnessInt = IntVar()
brightness = Scale(control_frame, label="Brightness", variable=brightnessInt, repeatinterval=10, repeatdelay=150,
                   orient="horizontal", length=250, from_=1.0, to=100, sliderlength=20, state="disable")
tempInt = IntVar()
temp = Scale(control_frame, label="Temp", variable=tempInt, orient="horizontal", resolution=100,
             length=250, from_=1700, to=6500, sliderlength=20, state="disable")
colorInt = IntVar()
color = Scale(control_frame, label="Color", variable=colorInt, sliderlength=20, from_=0, to=360,
              orient="horizontal", length=250, showvalue=0, state="disable")
rgb_scale = Label(control_frame, image=imgRgb)

search_frame.grid(column=0, row=0, sticky="e")
search_frame.grid_propagate(0)
search_frame.columnconfigure(0, minsize=100)
search_frame.columnconfigure(1, minsize=100)
control_frame.grid(column=1, row=0, sticky="n")
control_frame.columnconfigure(0, minsize=150)
control_frame.columnconfigure(1, minsize=150)
devices_frame.grid(column=0, row=4, columnspan=2, pady=10)
devices_canvas.pack(side="left", fill="both", expand=True)
devices_scrollbar.pack(side="right", fill="y")

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
bulbImg.grid(column=0, row=1, rowspan=4, pady=15, padx=5)
on.grid(column=1, row=1)
off.grid(column=1, row=2)
rgb.grid(column=1, row=3)
delete.grid(column=1, row=4)
brightness.grid(column=0, row=5, columnspan=4)
temp.grid(column=0, row=6, columnspan=4)
color.grid(column=0, row=7, columnspan=4)
rgb_scale.grid(column=0, row=8, columnspan=4)


startSavedDevices()
main.mainloop()
