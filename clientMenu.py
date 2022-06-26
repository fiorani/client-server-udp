import tkinter as tk
import tkinter.font as tkFont
from client import Client
from server import Server
import threading 

class Ui:
    
    def __init__(self, client):
        #setting title
        self.root=tk.Tk()
        self.root.title("Client")
        #setting window size
        self.width=883
        self.height=566
        self.screenwidth = self.root.winfo_screenwidth()
        self.screenheight = self.root.winfo_screenheight()
        self.alignstr = '%dx%d+%d+%d' % (self.width, self.height, (self.screenwidth - self.width) / 2, (self.screenheight - self.height) / 2)
        self.root.geometry(self.alignstr)
        self.root.resizable(width=False, height=False)

        self.LabelFileServer=self.setup_label(0, 10, 150, 30, "File presenti su server")
        self.BoxServerFiles=self.setup_box(10, 40, 282, 225)
        self.box_setArguments(self.BoxServerFiles, list(client.get_files_from_server().split("\n")))
        
        self.LabelOp=self.setup_label(300, 10, 135, 30, "Seleziona l'operazione")            
        self.OperationBox=self.setup_box(300, 40, 282, 225)
        self.box_setArguments(self.OperationBox, ("Download file from the server", "Upload file onto the server", "Close connection with the server"))
        
        self.LabelFileClient=self.setup_label(590, 10, 120, 30, "File presenti sul pc")
        self.BoxClientFiles=self.setup_box(590, 40, 282, 225)
        self.box_setArguments(self.BoxClientFiles, list(client.get_self_files().split("\n")))
        
        
        self.EseguiBtn=self.setup_btn(400, 390, 70, 25, "Esegui", self.Esegui_command)
        self.root.mainloop()
        
    def setup_box(self, xPlacement, yPlacement, boxWidth, boxHeight):
        Box = tk.Listbox(self.root)
        Box["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        Box["font"] = ft
        Box["fg"] = "#333333"
        Box["justify"] = "center"
        Box.place(x=xPlacement, y=yPlacement, width=boxWidth, height=boxHeight)
        return Box
    
    def setup_label(self, xPlacement, yPlacement, labelWidth, labelHeight, text):
        lbl=tk.Label(self.root)
        ft = tkFont.Font(family='Times',size=10)
        lbl["font"] = ft
        lbl["fg"] = "#333333"
        lbl["justify"] = "center"
        lbl["text"] = text
        lbl.place(x=xPlacement,y=yPlacement,width=labelWidth,height=labelHeight)
        return lbl
    
    def setup_btn(self, xPlacement, yPlacement, btnWidth, btnHeight, text, command):
        Btn=tk.Button(self.root)
        Btn["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        Btn["font"] = ft
        Btn["fg"] = "#000000"
        Btn["justify"] = "center"
        Btn["text"] = text
        Btn.place(x=xPlacement,y=yPlacement,width=btnWidth,height=btnHeight)
        Btn["command"] = command
        return Btn
        
        
    def box_setArguments(self, box, elementsList):
        box.delete(0, tk.END)
        for i in range(0, len(elementsList)):
            box.insert(i, elementsList[i]) 
    
    def Esegui_command(self):
        print("esegui")

if __name__ == "__main__":
    t = threading.Thread(target=Server, args=('localhost', 10000))
    t.start()
    ui = Ui(Client('localhost', 10000))
