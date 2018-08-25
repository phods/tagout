"""from Tkinter import Tk, ttk, Frame, Button, Label, Entry, Text, Checkbutton, \
    Scale, Listbox, Menu, BOTH, RIGHT, RAISED, N, E, S, W, \
    HORIZONTAL, END, FALSE, IntVar, StringVar, messagebox as box
"""
from Usuarios import Usuarios
from Tkinter import *
from Banco import Banco
#import sqlite3
import datetime
#----
import MySQLdb
from socket import *
import tkMessageBox
import threading
import time

    
################################
# Classe Tagout versão Beta    #
################################

class TagoutBeta(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent, background="black")
        self.parent = parent
        self.parent.title("TAGOUT")
     #   self.style = ttk.Style()
        self.style.theme_use("default")
        self.centreWindow()
        self.pack(fill=BOTH, expand=1)
        

# Barra de Menu

        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)
        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=fileMenu)

        
#Campos de exibição
        
        datetime.datetime.now()
    
        self.lbltimeVar = StringVar()
        self.lbltimeVar.set(datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H-%M-%S'))
        Label(self, textvariable=self.lbltimeVar).grid(
            row=1, column=2, sticky=W)   # a reference to the label is not retained

        self.lblnomeVar = StringVar()
        self.lblnomeVar.set("NOME")
        Label(self, textvariable=self.lblnomeVar).grid(
            row=2, column=5, sticky=N)   # a reference to the label is not retained

        self.nomeVar = StringVar()
        self.nomeVar.set("joão bosco da silva")
        Label(self, textvariable=self.nomeVar).grid(
            row=3, column=5, sticky=W+E)   # a reference to the label is not retained

        self.lbltagVar = StringVar()
        self.lbltagVar.set("TAG")
        Label(self, textvariable=self.lbltagVar).grid(
            row=4, column=5, sticky=N)   # a reference to the label is not retained

        self.tagVar = StringVar()
        self.tagVar.set("189.186.63.44.20")
        Label(self, textvariable=self.tagVar).grid(
            row=5, column=5, sticky=W+E)   # a reference to the label is not retained
        
        self.lblendereco = StringVar()
        self.lblendereco.set("Endereço")
        Label(self, textvariable=self.lblendereco).grid(
            row=6, column=5, sticky=N)   # a reference to the label is not retained

        self.enderecoVar = StringVar()
        self.enderecoVar.set("apt 202 bloco 13")
        Label(self, textvariable=self.enderecoVar).grid(
            row=7, column=5, sticky=W+E)   # a reference to the label is not retained
        
#Botões de ação        

        manBtn = Button(self, text="MANUT.", width=10, command=self.maintenance)
        manBtn.grid(row=8, column=2, padx=5, pady=3, sticky=W+E)
        listBtn = Button(self, text="Lista", width=10, command=self.quit)
        listBtn.grid(row=8, column=6, padx=5, pady=3, sticky=W+E)

#Centraliza a janela   

    def centreWindow(self):
        w = 300
        h = 300
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

#Instancia que inicia a tela de manutenção


    def maintenance(self, master=None):
        
        
        self.fonte = ("Verdana", "8")
        self.container1 = Frame(master)
        self.container1["pady"] = 10
        self.container1.pack()
        self.container2 = Frame(master)
        self.container2["padx"] = 20
        self.container2["pady"] = 5
        self.container2.pack()
        self.container3 = Frame(master)
        self.container3["padx"] = 20
        self.container3["pady"] = 5
        self.container3.pack()
        self.container4 = Frame(master)
        self.container4["padx"] = 20
        self.container4["pady"] = 5
        self.container4.pack()
        self.container5 = Frame(master)
        self.container5["padx"] = 20
        self.container5["pady"] = 5
        self.container5.pack()
        self.container6 = Frame(master)
        self.container6["padx"] = 20
        self.container6["pady"] = 5
        self.container6.pack()
        self.container7 = Frame(master)
        self.container7["padx"] = 30
        self.container7["pady"] = 5
        self.container7.pack()
        self.container8 = Frame(master)
        self.container8["padx"] = 20
        self.container8["pady"] = 10
        self.container8.pack()
        self.container9 = Frame(master)
        self.container9["pady"] = 15
        self.container9.pack()
        self.container10 = Frame(master)
        self.container10["padx"] = 30
        self.container10["pady"] = 20
        self.container10.pack()
        self.container11 = Frame(master)
        self.container11["padx"] = 30
        self.container11["pady"] = 30
        self.container11.pack()

        self.titulo = Label(self.container1, text="TAGOUT SYSTEMS")
        self.titulo["font"] = ("Arial", "9", "bold")
        self.titulo.pack()

        self.lblidusuario = Label(self.container2, text="idusuario:", font=self.fonte, width=10)
        self.lblidusuario.pack(side=LEFT)

        self.txtidusuario = Entry(self.container2)
        self.txtidusuario["width"] = 10
        self.txtidusuario["font"] = self.fonte
        self.txtidusuario.pack(side=LEFT)

        self.btnBuscarid = Button(self.container2, text="Buscar", font=self.fonte, width=10)
        self.btnBuscarid["command"] = self.buscarUsuario
        self.btnBuscarid.pack(side=RIGHT)

        self.lblnome = Label(self.container3, text="Nome:", font=self.fonte, width=10)
        self.lblnome.pack(side=LEFT)

        self.txtnome = Entry(self.container3)
        self.txtnome["width"] = 25
        self.txtnome["font"] = self.fonte
        self.txtnome.pack(side=LEFT)

        self.btnBuscarnm = Button(self.container3, text="Buscarnome", font=self.fonte, width=10)
        self.btnBuscarnm["command"] = self.buscarUsuarionome
        self.btnBuscarnm.pack(side=RIGHT)

        self.lbltag = Label(self.container4,text="tag:", font=self.fonte, width=10)
        self.lbltag.pack(side=LEFT)

        self.txttag = Entry(self.container4)
        self.txttag["width"] = 25
        self.txttag["font"] = self.fonte
        self.txttag.pack(side=LEFT)

        self.btnBuscartg = Button(self.container4, text="Buscar", font=self.fonte, width=10)
        self.btnBuscartg["command"] = self.buscarUsuariotag
        self.btnBuscartg.pack(side=RIGHT)


        
       

        self.lblendereco = Label(self.container5, text="Endereço:", font=self.fonte, width=10)
        self.lblendereco.pack(side=LEFT)

        self.txtendereco = Entry(self.container5)
        self.txtendereco["width"] = 25
        self.txtendereco["font"] = self.fonte
        self.txtendereco.pack(side=LEFT)

        
        self.bntInsert = Button(self.container7, text="Inserir", font=self.fonte, width=12)
        self.bntInsert["command"] = self.verTag
        self.bntInsert.pack(side=LEFT)

        self.bntAlterar = Button(self.container7, text="Alterar", font=self.fonte, width=12)
        self.bntAlterar["command"] = self.Alterarokcancel
        self.bntAlterar.pack(side=LEFT)

        self.bntExcluir = Button(self.container7, text="Excluir", font=self.fonte, width=12)
        self.bntExcluir["command"] = self.Deleteyesno
        self.bntExcluir.pack(side=LEFT)

        self.lblmsg = Label(self.container8, text="")
        self.lblmsg["font"] = ("Verdana", "9", "italic")
        self.lblmsg.pack()

        self.bntVertag = Button(self.container10, text="VERTAG")
        self.bntVertag["command"] = self.verTag
        self.bntVertag.pack(side=LEFT)

        
        
        self.txtVertag = Entry(self.container10)
        self.txtVertag["width"] = 30
        self.txtVertag["font"] = self.fonte
        self.txtVertag.pack()

        


 
        
#Instancia para inserção de usuario, utiliza o modulo Usuarios()

    def inserirUsuario(self):
        user = Usuarios()

        user.nome = self.txtnome.get()
        user.tag = self.txttag.get()
        user.endereco = self.txtendereco.get()
        
        self.lblmsg["text"] = user.insertUser()

        self.txtidusuario.delete(0, END)
        self.txtnome.delete(0, END)
        self.txttag.delete(0, END)
        self.txtendereco.delete(0, END)
        

#Instancia para alterar dados, utiliza o modulo Usuarios()

    def alterarUsuario(self):
        user = Usuarios()

        user.idusuario = self.txtidusuario.get()
        user.nome = self.txtnome.get()
        user.tag = self.txttag.get()
        user.endereco = self.txtendereco.get()
        

        self.lblmsg["text"] = user.updateUser()

        self.txtidusuario.delete(0, END)
        self.txtnome.delete(0, END)
        self.txttag.delete(0, END)
        self.txtendereco.delete(0, END)

#Instancia para excluir dados, utiliza o modulo Usuarios()        

    def excluirUsuario(self):
        user = Usuarios()

        user.idusuario = self.txtidusuario.get()

        self.lblmsg["text"] = user.deleteUser()

        self.txtidusuario.delete(0, END)
        self.txtnome.delete(0, END)
        self.txttag.delete(0, END)
        self.txtendereco.delete(0, END)
        
#Instancia para busca de usuario, utiliza o modulo Usuarios()

    def buscarUsuario(self):
        user = Usuarios()


        idusuario = self.txtidusuario.get()

        self.lblmsg["text"] = user.selectUser(idusuario)


        self.txtidusuario.delete(0, END)
        self.txtidusuario.insert(INSERT, user.idusuario)

        self.txtnome.delete(0, END)
        self.txtnome.insert(INSERT, user.nome)
        
        self.txttag.delete(0, END)
        self.txttag.insert(INSERT, user.tag)

        self.txtendereco.delete(0, END)
        self.txtendereco.insert(INSERT, user.endereco)

    def buscarUsuarionome(self):
        user = Usuarios()


        nome = self.txtnome.get()

        self.lblmsg["text"] = user.selectUsernm(nome)
        

        self.txtidusuario.delete(0, END)
        self.txtidusuario.insert(INSERT, user.idusuario)

        self.txtnome.delete(0, END)
        self.txtnome.insert(INSERT, user.nome)
        
        self.txttag.delete(0, END)
        self.txttag.insert(INSERT, user.tag)

        self.txtendereco.delete(0, END)
        self.txtendereco.insert(INSERT, user.endereco)

    def buscarUsuariotag(self):
        user = Usuarios()


        tag = self.txttag.get()

        self.lblmsg["text"] = user.selectUsertg(tag)


        self.txtidusuario.delete(0, END)
        self.txtidusuario.insert(INSERT, user.idusuario)

        self.txtnome.delete(0, END)
        self.txtnome.insert(INSERT, user.nome)
        
        self.txttag.delete(0, END)
        self.txttag.insert(INSERT, user.tag)

        self.txtendereco.delete(0, END)
        self.txtendereco.insert(INSERT, user.endereco)

    
#Comparação de tag lidos no RFID com os da Base de Dados

    def verTag(self):
        user = Usuarios()
        banco = Banco()
        
        ID = self.txtnome.get()
        
        
              

        conn = sqlite3.connect("bank.db")
        cursor = conn.cursor()

        sql = "SELECT * FROM usuarios WHERE nome=?"
        cursor.execute(sql, [(ID)])
        print (cursor.fetchone())
        if cursor.fetchone() == None :
            self.inserirUsuario()

        else:
            print("Tag já Exixstente")
            self.txttag.delete(0, END)
            self.txttag.insert(INSERT, "Tente novamente")
            
            self.lblmsg["text"] = "Tag existente"

        self.txtVertag.delete(0, END)

        self.txtVertag.insert(INSERT, ID)
    

    

        

    def onExit(self):
        print("ok")

    def Listatag(self):
        # Lista de tags * em fase de teste
                        
        title = ['189.186.63.44.20','123.145.584.55.5', '','','']
        titleList = Listbox(self, height=5)
        for t in title:
            titleList.insert(END, t)
        titleList.grid(row=7, column=2, columnspan=2, pady=5, sticky=W+E)
        titleList.bind("<<ListboxSelect>>", self.newTitle)


        
    def newTitle(self, val):
        sender = val.widget
        idx = sender.curselection()
        value = sender.get(idx)
        self.tagVar.set(value)

    
    def Alterarokcancel(self):
        if box.askokcancel('Alterar','Você tem certeza que deseja fazer as alterações?'):
            self.alterarUsuario()

    def Deleteyesno(self):
        if box.askyesno('Deletar',' Isso Vai Apagar Permanentemente da Base\n Você tem certeza que deseja deletar?'):
            self.excluirUsuario()   
      
def main():
    root = Tk()
    root.geometry("250x150+300+300")    # width x height + x + y
    # we will use centreWindow instead

    #root.resizable(width=FALSE, height=FALSE)# descomentar para manter o tamnho da janela
    
    # .. not resizable
    app = TagoutBeta(root)
    root.mainloop()

if __name__ == '__main__':
    main()

   

    



