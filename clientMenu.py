# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 12:18:54 2022

@author: pnmat
"""

import tkinter as tkt 
from server import server
from client import client
import threading

class ui:
   
    def __init__(self, client):
        self.window = tkt.Tk()
        self.window.title('Client')
        self.messages_frame = tkt.Frame(self.window)
        self.my_msg = tkt.StringVar()
        self.my_msg.set('Enter operation here...')
        self.scrollbar = tkt.Scrollbar(self.messages_frame)
        self.lbl = tkt.Label(self.window, text = "Choose one from the above")
        self.lbl.pack()
        self.operations = ("Get files stored on server", "Download file from the server", "Upload file onto the server", "Close connection with the server")
        self.msg_list = tkt.Listbox(self.messages_frame, heigh = 15, width = 50, yscrollcommand = self.scrollbar.set, selectmode = "browse")
        for i in range(0, len(self.operations)):
            self.msg_list.insert(i, self.operations[i]) 
        self.scrollbar.pack(side = tkt.RIGHT, fill = tkt.Y)
        self.msg_list.pack(side = tkt.LEFT, fill = tkt.BOTH)
        self.msg_list.pack()
        self.messages_frame.pack()
        self.entry_field = tkt.Entry(self.window, textvariable = self.my_msg)
        self.entry_field.pack()
        self.send_button = tkt.Button(self.window, text = "Send",  command = lambda: self.choose_operation(client))
        self.send_button.pack()
        tkt.mainloop()

    def choose_operation(self, client):
        if self.msg_list.get(self.msg_list.curselection()) == self.operations[0]:
            self.msg_list.insert(0, client.get_files_from_server())
        elif self.msg_list.get(self.msg_list.curselection()) == self.operations[1]:
            print("2")
        elif self.msg_list.get(self.msg_list.curselection()) == self.operations[2]:
            print("3")
        elif self.msg_list.get(self.msg_list.curselection()) == self.operations[3]:
            print("4")    
    
    
    

if __name__ == '__main__':
    t = threading.Thread(target=server, args=('localhost', 10000))
    t.start()
    client = client('localhost', 10000)
    ui = ui(client)
                 