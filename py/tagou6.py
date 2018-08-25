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
CMD_MOT1=18
CMD_EMERG1=23
CMD_MOT2=18
CMD_EMERG2=23
C_HRT=8
#SAIDA RELE
GPIO.setup(18,GPIO.OUT) #CMD_MOTOR1
GPIO.setup(23,GPIO.OUT) #CMD_EMERG1
GPIO.setup(24,GPIO.OUT) #CMD_MOTOR2
GPIO.setup(25,GPIO.OUT) #CMD_EMERG2
#GPIO.setup(8,GPIO.OUT)  #HEARTBEAT
#SAIDA SIMPLES
GPIO.setup(8,GPIO.OUT)  #HEARTBEAT
#---INPUT---
S1_FEC=4
S1_ABE=17
S1_INF=27
S1_LAC1=22
S1_LAC2=10
S2_FEC=9
S2_ABE=11
S2_INF=7
S2_LAC1=12
GPIO.setup(S1_FEC,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   #S_FECHADO
GPIO.setup(S1_ABE,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_ABERTO
GPIO.setup(S1_INF,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_INFRA
GPIO.setup(S1_LAC1,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_LACO1
GPIO.setup(S1_LAC2,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_LACO2
GPIO.setup(S2_FEC,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   #S_FECHADO
GPIO.setup(S2_ABE,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_ABERTO
GPIO.setup(S2_INF,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_INFRA
GPIO.setup(S2_LAC1,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_LACO1
GPIO.setup(2,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   #RESERVA
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
        GPIO.output(CMD_EMERG1,True)
        time.sleep(0.5)
        GPIO.output(CMD_EMERG1,False)
        time.sleep(0.5)
        x=x+1
    evento("================>>>>>>EMERGENCIAAAAAAAA<<<<<================")
#declare event
GPIO.add_event_detect(S1_INF,GPIO.FALLING)
GPIO.add_event_callback(S1_INF,EmergEvent)
#**********************************
def tempo(t):
    x=0
    while x < t:
        time.sleep(1)
        print"tempo espera",t,x
        x=x+1
        
def cmd():
    try:
        GPIO.output(CMD_MOT1,True)
        time.sleep(0.80)
        GPIO.output(CMD_MOT1,False)
        print "CMD ACIONADO"
        log("","Comando Acionado")
    except:
        print "CMD NAO EXECUTADO"
        log ("","Comando Nao Executado")
def heart():
    for i in range (0,3):
        GPIO.output(C_HRT,True)
        time.sleep(0.20)
        GPIO.output(C_HRT,False)
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
    sp = serial.Serial(port="/dev/ttyAMA0",baudrate=9600,timeout=0.1)
    #print "teste antena: BaudRate = 9600"
    x=0
    y=0
    tagg=b''
    ant=b''
    sp.flush()        
    
    while x<17 and not y:
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
def cmd_manual_reset(id_portao):
    db=MySQLdb.connect(host="192.168.15.7",
                               port=server.local_bind_port,
                               user="root",
                               passwd="toor",
                               db="wordpress")
    cur=db.cursor()
    try:
        #reset do comando manual
        cur.execute("UPDATE acesso  SET cmd_manual=0 WHERE id_acesso=%s",id_portao)
        print"cmd manual resetado"
        db.commit()
    except:
         print"NAO modificado"
         db.rollback()
def evento(msg):
    db=MySQLdb.connect(host="192.168.15.7",
                               port=server.local_bind_port,
                               user="root",
                               passwd="toor",
                               db="wordpress")
    cur=db.cursor()
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
    
    #valores da tabela acesso, caso necessario aumente a lista val
    val=['','','','','','','']
    cur.execute("SELECT * FROM acesso WHERE id_acesso=%s ",id_portao)
    for row in cur.fetchall():
        val[0]=row[7]#cmd manual
        val[1]=row[8]#tempo abertura
        val[2]=row[9]#chave_fila
        val[3]=row[9]#modo de operacao
        val[4]=row[9]#bypass portao
    return val    
def saida_laco(id_portao):
    var=atualiza_valores(id_portao)
    #se tiver o laco 3 ativo abrir
    if laco3 and S_fechado and not falha:
        cmd(id_portao)
        time.sleep(5)
        cmd=1
    if cmd and S_fechado:
        print "falha na acionamento"
    else:
        time.sleep(30)
    if cmd and not S_aberto:
        print"falha na abertura"
    else:
        print"portao aberto"
    if s_aberto and not laco3 and not falha:
        time.sleep(10)
        if s_aberto and not laco3 and not falha:
            cmd(id_portao)          
    
#------logica para repeticao a cada 10s       
threading.Timer(5,heart).start()    

#*****************************************************************    
def main():
    print"SISTEMA DE CONTROLE DE ACESSO - TAGOUT"
    GPIO.output(CMD_MOT1,False)
    GPIO.output(CMD_EMERG1,False)
    GPIO.output(C_HRT,False)
    tag=0
    cmd_a=0
    cmd_f=0
    cmd_ff=0
    abrindo=0
    fechando=0
    laco2=0
    falha=0
    id_portao=13
    #run=raw_input("START? > ")
    
 #---------------------------------   
    while True:
        #teste5
        var=atualiza_valores(id_portao)
        tag= read_tag()
        
        #---COMANDO MANUAL
        if var[0]==1:
            print"comando manual"
            log("","Comando Manual Acionado")
            cmd()
            #id do portao
            cmd_manual_reset(id_portao)
            
        #CICLO DE ABERTURA
        #tag laco1 e portao fechado
        #print "T,CA,CF,SA,SF,I,L1,L2,F"
        #print tag,",",cmd_a,",",cmd_f,",",GPIO.input(S1_FEC),",",GPIO.input(S1_ABE),",",GPIO.input(S1_INF),",",GPIO.input(S1_LAC1),",",GPIO.input(S1_LAC2),",",falha
        if not cmd_a and tag and GPIO.input(S1_FEC) and GPIO.input(S1_LAC1) and not falha:
            #comando motor 1 segundo
            print "Comando Abrir"
            log("","Comando Abrir Portao")
            cmd()
            
            cmd_a = 1
            #delay para esperar o portao descolar do sensor
            print "Aguarda 10 segundos para descolar"
            tempo(10)
         #msg falha na abertura   
        if cmd_a and GPIO.input(S1_FEC) and not falha:
            falha=1
            print "Falha no Acionamento - Aguardou 10s o Sensor de Fechado Continua Acionado "
            log("","Falha no Acionamento - Aguardou 10s o Sensor de Fechado Continua Acionado")
            evento("Falha de Acionamento - Favor verifique o motor, caso tudo normal limpe a falha")
         #var abrindo e timer de 30s   
        if cmd_a and not GPIO.input(S1_FEC) and not falha:
            abrindo=1
            print "Aguarda",var[1],"s P/CHEGAR NO FIM"
            log("","Abrindo - Aguardando Fim de Curso")
            tempo(var[1])

        if abrindo and not GPIO.input(S1_ABE) and not falha:
            print "FALHA NA ABERTURA ",var[1],"s E NAO ABRIU"
            log("","Falha na Abertura - Nao Acionou o Sensor de Fim de Curso ")
            evento("Falha de Abertura- Favor verifique o motor, caso tudo normal limpe a falha")
            falha=1
        #caso o portao abra completamente sao zerados os status
        if abrindo and GPIO.input(S1_ABE) and not falha:
            abrindo=0
            cmd_a=0
            print "CONFIRMADO ABERTO"
            log("","Portao Aberto com Sucesso")
        
        #----- CICLO DE FECHAMENTO
            
        if GPIO.input(S1_LAC2) and not laco2 and not falha:
            laco2=1
            print "LACO 2 ATIVADO"
            log("","Laço 2 - Ativado")
        #CASO O LAÇO JA TENHA SIDO ATIVDADO/s_aberto/infra ok
        if not cmd_f and laco2 and GPIO.input(S1_ABE) and GPIO.input(S1_INF) and not falha and not var[2]:
            #comando motor 1 segundo
            log("","Comando Fechar")           
            print "CMD FECHAR"
            cmd()
            cmd_f=1
            laco2=0
            print "Aguarda 10 segundos para descolar"
            time.sleep(10)
         #falha no fechamento
        if cmd_f and GPIO.input(S1_ABE) and not falha:
            print "Falha no Acionamento - Aguardou 10s o Sensor de Aberto Continua Acionado "
            log("","Falha no Acionamento - Aguardou 10s o Sensor de Aberto Continua Acionado")
            evento("Falha de Acionamento- Favor verifique o motor, caso tudo normal limpe a falha")
            falha =1    
        
        #fechando aguarda tempo para confirmar fechado
        if cmd_f and not GPIO.input(S1_ABE) and not var[2] and not falha:
            fechando =1
            print "Fechando",var[1],"s P/CHEGAR NO FIM"
            log("","Fechando - Aguardando Fim de Curso")
            time.sleep(var[1])
        #falha no fechamento
        if fechando and not GPIO.input(S1_FEC) and not var[2] and not falha:
            falha=1
            print "FALHA NO FECHAMENTO ",var[1],"s E NAO FECHOU"
            log("","Falha no Fechamento - Nao Acionou o Sensor de Fim de Curso ")
            evento("Falha de Fechamento - Favor verifique o motor, caso tudo normal limpe a falha")

            
        #fechamento por fila
        
        if not tag and not cmd_ff  and not GPIO.input(S1_LAC1) and not GPIO.input(S1_LAC2)and GPIO.input(S1_ABE) and GPIO.input(S1_INF) and not falha and var[2]:
            
            print "aguarda 5 segundo depois as condicoes sao atendidas para verificar se chegou mais algum carro"
            time.sleep(5)
           
            if not tag and not cmd_ff  and not GPIO.input(S1_LAC1) and not GPIO.input(S1_LAC2)and GPIO.input(S1_ABE) and GPIO.input(S1_INF) and not falha and var[2]:
           #comando motor 1 segundo          
                log("","Comando Fechar Fila")           
                print "CMD FECHAR FILA"
                cmd()
                cmd_ff=1
                
                print "Aguarda 10 segundos para descolar"
                time.sleep(10)
        if cmd_ff and GPIO.input(S1_ABE) and var[2] and not falha:
            print "Falha no Acionamento Fila - Aguardou 10s o Sensor de Aberto Continua Acionado "
            log("","Falha no Acionamento Fila - Aguardou 10s o Sensor de Aberto Continua Acionado")
            evento("Falha de Acionamento Fila - Favor verifique o motor, caso tudo normal limpe a falha")
            falha =1   
            
        if cmd_ff and tag and GPIO.input(S1_LAC1) and var[2]:
            print "CMD PARA REABRIR O PORTAO FILA"
            log("","Comando para parar o portao fila")
            cmd()
            time.sleep(2)
            log("","Comando para reabrir o portao fila")
            cmd()
            cmd_ff=0
            cmd_a=1
            
          
        #confirmado fechado
        if (cmd_ff or cmd_f) and GPIO.input(S1_FEC):            
            fechando=0
            cmd_f=0
            cmd_ff=0
            print "CONFIRMADO FECHADO"
            log("","Portao Fechado com Sucesso")
        #reset de falhas
        if falha and GPIO.input(2):
            print "RESET FALHAS "
            log("","Reset De Falhas")
            falha =0
            reset=0
            cmd_a=0
            cmd_f=0
            cmd_ff=0
            abrindo=0
            fechando=0
            laco2=0
            
        #GPIO.cleanup()

        
if __name__=="__main__":
    main()
