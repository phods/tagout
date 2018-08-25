from Tkinter import *
import MySQLdb
from socket import *
import tkMessageBox
import threading
import time
#**********************************
#configuracao socket udp
address=('192.168.25.56',5000)
client_socket = socket(AF_INET,SOCK_DGRAM)
client_socket.settimeout(1)
#**********************************

db = MySQLdb.connect(host="localhost", user="root", passwd="toor",db="arduino")
cur = db.cursor()
var=0
var1=0
global varopen
varopen=0
data=0
varnome=0
vartag=0
varend=0

#**********************************
#    FUNCOES
#**********************************
def f():
#do something here
#call f() again in 60 seconds
    print"chamada da verificacaode tag"
    #threading.Timer(10,f).start()
    
def bt_inserir():
    try:
        cur.execute("INSERT INTO tabelarfid (tag,nome,end) VALUES (%s,%s,%s)",(ed_tag.get(), \
        ed_nome.get(),ed_end.get()))
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
        print "feedback cmd:",rec_data
    except:
        pass
def msg_box():
    tkMessageBox.showinfo("HI PYTHON","CAMPO EM BRANCO")
    lb2_tag["text"]="agura"
def list_all():
    cur.execute("SELECT * FROM tabelarfid WHERE 1")
    for row in cur.fetchall():       
        print row[0]
        
def comparar():
    db = MySQLdb.connect(host="localhost", user="root", passwd="toor",db="arduino")
    cur = db.cursor()
    #le o tag temporario
    
    var1=0
    var=0
   
    cur.execute("SELECT temp_tag FROM rfid_temp order by ID desc limit 1")
    for row in cur.fetchall():
        var=row[0]
        print"var",var
        #pesquisa no banco se existe o tag 
    cur.execute("SELECT tag FROM tabelarfid WHERE tag=%s ",var)
    for row in cur.fetchall():
        var1=row[0]
        print"var1",var1
        
    if(var==var1 and var!=" " and var1!=varopen):
        cur.execute("SELECT * FROM tabelarfid WHERE tag=%s ",var1)
        for row in cur.fetchall():
            row[0]
            row[1]
            vartag=row[2]
            varnome=row[3]
            varend=row[4]
            
        lb2_tag["text"]=vartag
        lb2_nome["text"]=varnome
        lb2_end["text"]=varend   
        print"encontrou"
        #para o portao nao abrir 2 vezes seguidas para o mesmo tag
        
      #  varopen=var1
        #comando para abrir o portao
        cmd_ard()
      
    else:
        print"NAO encontou"
        lb2_tag["text"]="TAG:"
        lb2_nome["text"]="NOME:"
        lb2_end["text"]="ENDERECO:"
        
#------logica para repeticao a cada 10s       
    threading.Timer(10,comparar).start()
   
#*****************************************************************    





#db.close

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
ed_tag=Entry(janela,width=60)
ed_tag.place(x=0,y=80)
lb_nome=Label(janela,text="NOME:")
lb_nome.place(x=0,y=100)
ed_nome=Entry(janela,width=60)
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
bt6.place(x=210,y=300)
bt7=Button(janela,width=5,text="LIST ALL",command=list_all)
bt7.place(x=210,y=330)
bt8=Button(janela,width=10,text="BUSCA NA BASE",command=comparar)
bt8.place(x=210,y=360)


comparar()


#------------------------
#CRIANDO JANELA PRINCIPAL
janela.geometry("400x400+100+100")
janela.mainloop()


