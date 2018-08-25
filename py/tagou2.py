#! /usr/bin/python env
import sys
from socket import *
import serial
from struct import *
import binascii
from binascii import hexlify
import MySQLdb
import threading
import RPi.GPIO as GPIO
import time
from threading import Timer
from sshtunnel import SSHTunnelForwarder

#**********************************
#tell the GPIO module tha we want to use the
#chip's pin numbrering scheme
GPIO.setmode(GPIO.BCM)

#---OUTPUT---
GPIO.setup(18,GPIO.OUT) #CMD_MOTOR
GPIO.setup(23,GPIO.OUT) #CMD_EMERG
GPIO.setup(24,GPIO.OUT) #HEARTbeat
#GPIO.setup(25,GPIO.OUT) #RESERVA
#GPIO.setup(8,GPIO.OUT)  #RESERVA
#---INPUT---
GPIO.setup(4,GPIO.IN,pull_up_down=GPIO.PUD_DOWN) #S_FECHADO
GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_ABERTO
GPIO.setup(27,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_INFRA
GPIO.setup(22,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_LACO1
GPIO.setup(10,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_LACO2
GPIO.setup(9,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)   #RESERVA
#GPIO.setup(11,GPIO.IN)  #RESERVA
#GPIO.setup(7,GPIO.IN)   #RESERVA
#**********************************

server =  SSHTunnelForwarder(
    ("192.168.15.6",22),
    ssh_username="pi",
    ssh_password="t4fnd2608",
    remote_bind_address=("localhost",3306))
server.start()
print server.local_bind_port
#server.stop()
db=MySQLdb.connect(host="192.168.15.7",
                       port=server.local_bind_port,
                       user="root",
                       passwd="toor",
                       db="wordpress")
cur=db.cursor()
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#handle the emerg event
def EmergEvent(pin):
    print"----->>>> EMERGENCIA <<<<-----"
    x=0
    while x<10:
        GPIO.output(23,True)
        time.sleep(0.5)
        GPIO.output(23,False)
        time.sleep(0.5)
        x=x+1
    evento("EMERGENCIAAAAAAAA")
#declare event
GPIO.add_event_detect(27,GPIO.FALLING)
GPIO.add_event_callback(27,EmergEvent)
#**********************************
def cmd():
            
            GPIO.output(18,True)
            time.sleep(0.80)
            GPIO.output(18,False)
            print "CMD ACIONADO"
def heart():
            
            for i in range (0,3):
                GPIO.output(24,True)
                time.sleep(0.20)
                GPIO.output(24,False)
                time.sleep(0.20)
            
def log(tag,desc):
    try:
        if tag == "":
            cur.execute("INSERT INTO log (tag,descr) VALUES (%s,%s)",(tag,desc))
            print"LOG inserido sem tag"
            db.commit()
        else:                   
            cur.execute("SELECT tag FROM log WHERE tag != ''  ORDER BY id_log DESC LIMIT 1")
            for row in cur.fetchall():
                #print row[0]
                if row[0]!=tag:
                    cur.execute("INSERT INTO log (tag,descr) VALUES (%s,%s)",(tag,desc))
                    print"LOG inserido c/ tag"
                    db.commit()
                else:
                    print"esse tag ja eh o ultimo q entrou no LOG"            
    except:
         print"LOG NAO inserido"
         db.rollback()        
def read_tag():
    sp=0
    sp = serial.Serial(port="/dev/ttyAMA0",baudrate=9600,timeout=0.1)
    #print "teste antena: BaudRate = 9600"
    x=0
    y=0
    tagg=b''
    ant=b''
    print sp.bytesize  
    
    
    while x<17 and not y:
        #print"while",x,y,hexlify(ant).decode('ascii'),hexlify(tagg).decode('ascii')
        ant = sp.read()
        if ant != b'':
            x=x+1
            tagg=ant+tagg
        else:
            y=1        
        if x==17:            
            tagg=hexlify(tagg).decode('ascii')
            print"tag----->", tagg            
            cur.execute("SELECT tag FROM usuario WHERE tag=%s ",tagg)
            for row in cur.fetchall():
                if row[0]==tagg:
                    log(tagg,"Tag Valido")
                    return 1
                         
                else:
                    log(tagg,"Tag NAO Valido")
                    return 0
def cmd_manual_reset():
    try:
        #reset do comando manual
        cur.execute("INSERT INTO acesso (cmd_manual) VALUES 0")
        print"cmd manual resetado"
        db.commit()
    except:
         print"NAO inserido"
         db.rollback()
def evento(msg):
    try:
        #msg do evento
        cur.execute("UPDATE config  SET novo_evento=1,txt_evento=%s WHERE id_config=1",msg)
        db.commit()
    except:
         print"NAO modificado"
         db.rollback()
         
def atualiza_valores(id_portao):
    db=MySQLdb.connect(host="192.168.15.7",
                       port=server.local_bind_port,
                       user="root",
                       passwd="toor",
                       db="wordpress")
    cur=db.cursor()
    #valor do cmd manual
    print "atualizando"
    val=['','','','','']
    cur.execute("SELECT * FROM acesso WHERE id_acesso=%s ",id_portao)
    for row in cur.fetchall():
                val[0]=row[7]#cmd manual
                val[1]=row[8]#tempo abertura
                val[2]=row[9]#chave_fila
                print row[7],row[8],row[9]
                print val[0],val[1],val[2]
    return val



#------logica para repeticao a cada 10s       
threading.Timer(1,heart).start()
    

#*****************************************************************    
def main():
    print"SISTEMA DE ACESSO - TAGOUT"
    GPIO.output(18,False)
    GPIO.output(23,False)
    GPIO.output(24,False)
    cmd_a=0
    cmd_f=0
    abrindo=0
    fechando=0
    emerg=0
    laco2=0
    falha=0
    #run=raw_input("START? > ")
    
 #---------------------------------   
    while True:
        
        print atualiza_valores(14)
        tag=0
        #tag= read_tag()
        #print"aguardando tag", tag
        
        #CICLO DE ABERTURA
        #comando abrir tem o s_fechado e laço1
        #print"primeiro if", cmd_a,tag,GPIO.input(4),GPIO.input(22),falha
        if not cmd_a and tag and GPIO.input(4) and GPIO.input(22) and not falha:
            #comando motor 1 segundo
            cmd()
            tag=0
            print "CMD ABRIR"
            cmd_a = True
            #delay para esperar o portao descolar do sensor
            print "conta 10 segundos para descolar"
            time.sleep(10)
         #msg falha na abertura   
        if cmd_a and GPIO.input(4) and not falha:
            falha=1
            print "FALHA NO ACIONAMENTO"
         #var abrindo e timer de 30s   
        if cmd_a and not GPIO.input(4) and not falha:
            abrindo=1
            print "conta 30 segundos P/CHEGAR NO FIM"
            time.sleep(20)

        if abrindo and not GPIO.input(17) and not falha:
            print "PASSOU 30S E NAO ABRIU"
            falha=1
        #caso o portao abra completamente sao zerados os status
        if abrindo and GPIO.input(17) and not falha:
            abrindo=0
            cmd_a=0
            print "CONFIRMADO ABERTO"
        
        #----- ciclo fechamento
            
        if GPIO.input(10) and not laco2:
            laco2=1
            print "LACO 2 ATIVADO"
        #CASO O LAÇO JA TENHA SIDO ATIVDADO/s_aberto/infra ok
        if not cmd_f and laco2 and GPIO.input(17) and GPIO.input(27) and not falha:
            #comando motor 1 segundo
            cmd()
            print "CMD FECHAR"
            cmd_f=1
            print "conta 10 segundos para descolar"
            time.sleep(10)
        #falha no fechamento
        if cmd_f and GPIO.input(17) and not falha:
            print "falha no fechamento"
            falha =1
        if cmd_f and not GPIO.input(17) and not falha:
            fechando =1
            print "conta 30 segundos ENCOSTAR NO FIM DE CURSO"
            time.sleep(30)
        if cmd_f and not GPIO.input(4) and not falha:
            falha=1
            print "falha no fechamento sensor "

        if cmd_f and GPIO.input(4):
            print "portao fechado com sucesso "
            fechando=0
            cmd_f=0

        if falha and GPIO.input(9):
            print "RESET FALHAS "
            falha =0
            reset=0
            cmd_a=0
            cmd_f=0
            abrindo=0
            fechando=0
            
            

            
            
                
        #print "button pushed"

        #GPIO.cleanup()

        #time.sleep(5.80)
        #db.close
        time.sleep(3)



if __name__=="__main__":
    main()
