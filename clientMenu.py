import tkinter as tk
import tkinter.font as tkFont
import threading 

class Ui(tk.Tk):
    
    def __init__(self, client):
        #setting title
        super().__init__()
        self.title("Client")
        #setting window size
        self.width=883
        self.height=566
        self.client=client
        self.screenwidth = self.winfo_screenwidth()
        self.screenheight = self.winfo_screenheight()
        self.alignstr = '%dx%d+%d+%d' % (self.width, self.height, (self.screenwidth - self.width) / 2, (self.screenheight - self.height) / 2)
        self.geometry(self.alignstr)
        self.resizable(width=False, height=False)
        
        self.operations = ("Download file from the server", "Upload file onto the server","start client", "Close connection with the server")
        
        self.LabelFileServer=self.setup_label(0, 10, 150, 30, "File presenti sul server")
        self.BoxServerFiles=self.setup_box(10, 40, 282, 225)
        
        self.LabelOp=self.setup_label(300, 10, 135, 30, "Seleziona l'operazione")            
        self.OperationBox=self.setup_box(300, 40, 282, 225)
        self.box_setArguments(self.OperationBox, self.operations)
        
        self.LabelFileClient=self.setup_label(590, 10, 120, 30, "File presenti sul pc")
        self.BoxClientFiles=self.setup_box(590, 40, 282, 225)
        
        #self.EseguiBtn=self.setup_btn(400, 390, 70, 25, "Esegui", lambda: self.Esegui_command(client))
        self.EseguiBtn=self.setup_btn(350, 390, 70, 25, "Esegui", lambda: self.run_threaded_command())
        self.RefreshBtn=self.setup_btn(450, 390, 70, 25, "Aggiorna", lambda: self.refresh_boxes())
        #threading.Thread(target=self.update, args = (client, )).start()
        
        self.Labelstatus=self.setup_label(350, 350, 70, 25, 'stato 0% completato')  
        self.Labelstatus.after(100, self.update_label_status)
        self.mainloop()
        
        
    def setup_box(self, xPlacement, yPlacement, boxWidth, boxHeight):
        Box = tk.Listbox(self, exportselection = 0)
        Box["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        Box["font"] = ft
        Box["fg"] = "#333333"
        Box["justify"] = "center"
        Box.place(x=xPlacement, y=yPlacement, width=boxWidth, height=boxHeight)
        return Box
    
    def setup_label(self, xPlacement, yPlacement, labelWidth, labelHeight, text):
        lbl=tk.Label(self)
        ft = tkFont.Font(family='Times',size=10)
        lbl["font"] = ft
        lbl["fg"] = "#333333"
        lbl["justify"] = "center"
        lbl["text"] = text
        lbl.place(x=xPlacement,y=yPlacement)
        return lbl
    
    def setup_btn(self, xPlacement, yPlacement, btnWidth, btnHeight, text, command):
        Btn=tk.Button(self)
        Btn["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        Btn["font"] = ft
        Btn["fg"] = "#000000"
        Btn["justify"] = "center"
        Btn["text"] = text
        Btn.place(x=xPlacement,y=yPlacement)
        Btn["command"] = command
        return Btn
    
    def run_threaded_command(self):
        threading.Thread(target=self.exec_command).start()
           
    def box_setArguments(self, box, elementsList):
        box.delete(0, tk.END)
        for el in elementsList:
            box.insert(tk.END, el) 
    
    def clear_boxes_selections(self):
        self.OperationBox.selection_clear(0, tk.END)
        self.BoxServerFiles.selection_clear(0, tk.END)
        self.BoxClientFiles.selection_clear(0, tk.END)
    
    def error_dialog_open(self):
        errDialog = tk.Tk()
        errDialog.title("Error")
        errDialog.geometry("200x100")
        errDialog.resizable(width=False, height=False)
        tk.Label(errDialog, text = "Errore, seleziona un'operazione").pack()
        tk.Button(errDialog, text = "Chiudi", command = errDialog.destroy).pack()
        
    def refresh_boxes(self):
        self.box_setArguments(self.BoxServerFiles, list(self.client.get_files_from_server().split("\n")))
        self.box_setArguments(self.BoxClientFiles, list(self.client.get_self_files().split("\n")))
    
    def exec_command(self):
        if self.OperationBox.curselection():
            if self.OperationBox.get(self.OperationBox.curselection()) == self.operations[0] and self.BoxServerFiles.curselection():
                self.client.download(self.BoxServerFiles.get(self.BoxServerFiles.curselection()))
            elif self.OperationBox.get(self.OperationBox.curselection()) == self.operations[1] and self.BoxClientFiles.curselection():
                self.client.upload(self.BoxClientFiles.get(self.BoxClientFiles.curselection()))
            elif self.OperationBox.get(self.OperationBox.curselection()) == self.operations[2]:
                self.client.start_client()
            elif self.OperationBox.get(self.OperationBox.curselection()) == self.operations[3]:
                self.client.close_client()
               #self.root.destroy()
            self.clear_boxes_selections()
        else:
            self.error_dialog_open()

    def update_label_status(self):
        self.Labelstatus.configure(text='stato '+str(self.client.status())+'% completato')
        self.Labelstatus.after(100, self.update_label_status)
        

    
        
        