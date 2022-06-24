# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 12:18:54 2022

@author: pnmat
"""

import tkinter as tkt 

window = tkt.Tk()
window.title('Client')
messages_frame = tkt.Frame(window)
my_msg = tkt.StringVar()
my_msg.set('Enter operation here...')
scrollbar = tkt.Scrollbar(messages_frame)


lbl = tkt.Label(window, text = "Choose one from the above")
lbl.pack()

operations = ("Get files stored on server", "Download file from the server", "Upload file onto the server", "Close connection with the server")
def setup_menu():
    for i in range(0, 4):
        msg_list.insert(i, operations[i])    

msg_list = tkt.Listbox(messages_frame, heigh = 15, width = 50, yscrollcommand = scrollbar.set, selectmode = "browse")
setup_menu()


    
    
    
def print_selected_item():
    if msg_list.get(msg_list.curselection()) == operations[0]:
        print("1")
    elif msg_list.get(msg_list.curselection()) == operations[1]:
        print("2")
    elif msg_list.get(msg_list.curselection()) == operations[2]:
        print("3")
    elif msg_list.get(msg_list.curselection()) == operations[3]:
        print("4")    
    
    
scrollbar.pack(side = tkt.RIGHT, fill = tkt.Y)
msg_list.pack(side = tkt.LEFT, fill = tkt.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkt.Entry(window, textvariable = my_msg)
entry_field.pack()

    
    
send_button = tkt.Button(window, text = "Send",  command = print_selected_item)
send_button.pack()

tkt.mainloop()
                 