import tkinter as tk
import tkinter.font as tkFont

class Ui(tk.Tk):
    
    def __init__(self,server):
        super().__init__()
        self.title("server")
        self.width=883
        self.height=566
        self.server=server
        self.screenwidth = self.winfo_screenwidth()
        self.screenheight = self.winfo_screenheight()
        self.alignstr = '%dx%d+%d+%d' % (self.width, self.height, (self.screenwidth - self.width) / 2, (self.screenheight - self.height) / 2)
        self.geometry(self.alignstr)
        self.resizable(width=False, height=False)
        self.operations = ("start server", "stop server")
        
        self.LabelFileServer=self.setup_label(10, 10, "Server files")
        self.BoxServerFiles=self.setup_box(10, 40, 282, 225)
        
        self.LabelOp=self.setup_label(300, 10, "Select the procedure")            
        self.OperationBox=self.setup_box(300, 40, 282, 225)
        self.box_setArguments(self.OperationBox, self.operations)
        
        self.RefreshBtn=self.setup_btn(450, 390, "Update", lambda: self.refresh_boxes())
        self.EseguiBtn=self.setup_btn(350, 390, "Exec", lambda: self.exec_command())
        
        self.Labelstatus=self.setup_label(350, 350, 'off')  
        
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
    
    def setup_label(self, xPlacement, yPlacement, text):
        lbl=tk.Label(self)
        ft = tkFont.Font(family='Times',size=10)
        lbl["font"] = ft
        lbl["fg"] = "#333333"
        lbl["justify"] = "center"
        lbl["text"] = text
        lbl.place(x=xPlacement,y=yPlacement)
        return lbl
    
    def setup_btn(self, xPlacement, yPlacement, text, command):
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
           
    def box_setArguments(self, box, elementsList):
        box.delete(0, tk.END)
        for el in elementsList:
            box.insert(tk.END, el) 
    
    def clear_boxes_selections(self):
        self.OperationBox.selection_clear(0, tk.END)
        self.BoxServerFiles.selection_clear(0, tk.END)
    
    def error_dialog_open(self):
        errDialog = tk.Tk()
        errDialog.title("Error")
        errDialog.geometry("200x100")
        errDialog.resizable(width=False, height=False)
        tk.Label(errDialog, text = "Error, Choose a procedure first").pack()
        tk.Button(errDialog, text = "Close", command = errDialog.destroy).pack()
    
    def refresh_boxes(self):
        self.box_setArguments(self.BoxServerFiles, list(self.server.get_self_files().split("\n")))
    
    def exec_command(self):
        if self.OperationBox.curselection():
            if self.OperationBox.get(self.OperationBox.curselection()) == self.operations[0]:
                self.Labelstatus.configure(text='on')
                self.server.start_server()
            elif self.OperationBox.get(self.OperationBox.curselection()) == self.operations[1] :
                self.Labelstatus.configure(text='off')
                self.server.close_server()
            self.clear_boxes_selections()
        else:
            self.error_dialog_open()
            