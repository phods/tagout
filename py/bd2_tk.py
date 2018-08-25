from Tkinter import *
import MySQLdb
from socket import *
import tkMessageBox
import time
varx='tagtag'

#**********************************
#    FUNCOES

def bt_inserir():
    try:
        cur.execute("INSERT INTO tabelarfid (tag) VALUES (%s)",(ed_tag.get()))
     #     cur.execute("INSERT INTO rfid_temp (id,evento,temp_tag) VALUES (0,0,0)")#,(0,0,0))
        print"inserido"
        db.commit()
    except:
        print"NAO inserido"
        db.rollback()

def bt_deletar():
    try:
        cur.execute("DELETE FROM rfid_temp WHERE temp_tag=(%s)",(ed_tag.get()))
        print"deletado"
        db.commit()
    except:
        print"NAO deletado"
        db.rollback()
def bt_modificar():
    try:
        cur.execute("UPDATE rfid_temp SET temp_tag=(%s) WHERE id=11",(ed_tag.get()))
        print"modificado"
        db.commit()
    except:
        print"NAO modificado"
        db.rollback()
def bt_procurar():
    try:
        cur.execute("SELECT * FROM tabelarfid  WHERE tag=%s",(ed_tag.get()))
        print"encottrado"
        db.commit()
    except:
        print"NAO encontrado"
        db.rollback()
def cmd_ard():
    data="a"
    client_socket.sendto(data,address)
    try:
        rec_data,addr=client_socket.recvfrom(2048)
        print "feedback",rec_data
    except:
        pass
def msg_box():
    tkMessageBox.showinfo("HI PYTHON","CAMPO EM BRANCO")
def list_all():
    cur.execute("SELECT * FROM tabelarfid WHERE 1")
    for row in cur.fetchall():       
        print row[0]
        
def comparar():
    #cur.execute("SELECT temp_tag FROM rfid_temp WHERE id=1")
    #le o tag temporario 
    cur.execute("SELECT temp_tag FROM rfid_temp order by ID desc limit 1")
    for row in cur.fetchall():
        var=row[0]
        print"var", var
        #pesquisa no banco se existe o tag 
        cur.execute("SELECT tag FROM tabelarfid WHERE tag=%s ",var)
    for row in cur.fetchall():
        var1=row[0]
        print"var1", var1
        
    if(var==var1 and var!=" "):
        print"encontrou"
        cmd_ard()
      
    else:
        print"NAO encontou"
        #print "valor:%s"%var
       # print row[1]
       # print row[2]
       # print row[3]                         
   
#*****************************************************************    
#configuracao socket udp
address=('192.168.0.56',5000)
client_socket = socket(AF_INET,SOCK_DGRAM)
client_socket.settimeout(1)


db = MySQLdb.connect(host="localhost", user="root", passwd="toor",db="arduino")
cur = db.cursor()
var=0
var1=0
data=0
varnome=0
vartag=0
varend=0




db.close

#criando janela/botoes/labels
janela=Tk()
bt1=Button(janela,width=5,text="INSERIR",command=bt_inserir)
bt1.place(x=0,y=30)
bt2=Button(janela,width=5,text="DELETAR",command=bt_deletar)
bt2.place(x=70,y=30)
bt3=Button(janela,width=5,text="MODIFICAR",command=bt_modificar)
bt3.place(x=140,y=30)
bt4=Button(janela,width=5,text="PROCURAR",command=bt_procurar)
bt4.place(x=210,y=30)
bt5=Button(janela,width=1,text="CMD",command=cmd_ard)
bt5.place(x=250,y=250)
lb_tag=Label(janela,text="TAG:")
lb_tag.place(x=0,y=60)
ed_tag=Entry(janela)
ed_tag.place(x=0,y=80)
lb_nome=Label(janela,text="NOME:")
lb_nome.place(x=0,y=100)
ed_nome=Entry(janela)
ed_nome.place(x=0,y=120)
lb_end=Label(janela,text="END:")
lb_end.place(x=0,y=140)
ed_end=Entry(janela)
ed_end.place(x=0,y=160)
#-----------------
lb2_tag=Label(janela,text="TAG:")
lb2_tag.place(x=0,y=190)
lb2_nome=Label(janela,text="NOME:")
lb2_nome.place(x=0,y=210)
lb2_end=Label(janela,text="END:")
lb2_end.place(x=0,y=240)


bt6=Button(janela,width=5,text="messabox",command=msg_box)
bt6.place(x=210,y=210)
bt7=Button(janela,width=5,text="LIST ALL",command=list_all)
bt7.place(x=210,y=180)
bt8=Button(janela,width=5,text="BUSCA NA BASE",command=comparar)
bt8.place(x=210,y=180)

#------------------------
janela.geometry("300x300+100+100")
janela.mainloop()


