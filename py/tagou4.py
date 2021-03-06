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
#SAIDA RELE
GPIO.setup(18,GPIO.OUT) #CMD_MOTOR1
GPIO.setup(23,GPIO.OUT) #CMD_EMERG1
GPIO.setup(24,GPIO.OUT) #CMD_MOTOR2
GPIO.setup(25,GPIO.OUT) #CMD_EMERG2
GPIO.setup(8,GPIO.OUT)  #HEARTbeat
#SAIDA DIRETA
#GPIO.setup(8,GPIO.OUT)  #RESERVA
#---INPUT---
GPIO.setup(4,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  #S1_FECHADO
GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S1_ABERTO
GPIO.setup(27,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S1_INFRA
GPIO.setup(22,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S1_LACO1
GPIO.setup(10,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S1_LACO2
GPIO.setup(9,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  #S2_FECHADO
GPIO.setup(11,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #S2_ABERTO
GPIO.setup(7,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  #S2_INFRA
GPIO.setup(12,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #S2_LACO1
GPIO.setup(16,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #RESERVA
GPIO.setup(20,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #RESERVA

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
        
    log("","EMERGENCIA")
    evento("================>>>>>>EMERGENCIAAAAAAAA<<<<<================")
#declare event
GPIO.add_event_detect(27,GPIO.FALLING)
GPIO.add_event_callback(27,EmergEvent)
#**********************************
def cmd():
    try:
        GPIO.output(18,True)
        time.sleep(0.80)
        GPIO.output(18,False)
        print "CMD ACIONADO"
        log("","Comando Acionado")
    except:
        print "CMD NAO EXECUTADO"
        log ("","Comando Nao Executado")
def heart():
             for i in range (0,3):
                GPIO.output(8,True)
                time.sleep(0.20)
                GPIO.output(8,False)
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
        val[3]=row[9]#modo de operacao do portao 		
        val[4]=row[9]#cmd bypass
    return val    

#------logica para repeticao a cada 10s       
threading.Timer(1,heart).start()    
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
    
        
    
#*****************************************************************    
def main():
    print"SISTEMA DE CONTROLE DE ACESSO - TAGOUT"
    GPIO.output(18,False)
    GPIO.output(23,False)
    GPIO.output(24,False)
    tag=0
    cmd_a=0
    cmd_f=0
    cmd_ff=0
    abrindo=0
    fechando=0
    laco2=0
    falha=0
    id_portao=14
    #run=raw_input("START? > ")
    
 #---------------------------------   
    while True:
        
        var=atualiza_valores(id_portao)
        tag= read_tag()
        
        #---COMANDO MANUAL
        if var[0]==1:            
            log("","Comando Manual Acionado")
            cmd()
            #id do portao
            cmd_manual_reset(id_portao)
        
	#verificacao de modo de operacao do portao
	#1=entrada simples(c/ antena)
	#2=saida laço (apenas laço)
	#3=saida antena
	#4=
        if var[3]==2:
            saida_laco(id_portao);
			
        #CICLO DE ABERTURA
        #tag laco1 e portao fechado
        #print "T,CA,CF,SA,SF,I,L1,L2,F"
        #print tag,",",cmd_a,",",cmd_f,",",GPIO.input(4),",",GPIO.input(17),",",GPIO.input(27),",",GPIO.input(22),",",GPIO.input(10),",",falha
        if not cmd_a and tag and GPIO.input(4) and GPIO.input(22) and not falha:
            #comando motor 1 segundo
            print "Comando Abrir"
            log("","Comando Abrir Portao")
            cmd()
            
            cmd_a = 1
            #delay para esperar o portao descolar do sensor
            print "Aguarda 10 segundos para descolar"
            time.sleep(10)
         #msg falha na abertura   
        if cmd_a and GPIO.input(4) and not falha:
            falha=1
            print "Falha no Acionamento - Aguardou 10s o Sensor de Fechado Continua Acionado "
            log("","Falha no Acionamento - Aguardou 10s o Sensor de Fechado Continua Acionado")
            evento("Falha de Acionamento - Favor verifique o motor, caso tudo normal limpe a falha")
         #var abrindo e timer de 30s   
        if cmd_a and not GPIO.input(4) and not falha:
            abrindo=1
            print "Aguarda",var[1],"s P/CHEGAR NO FIM"
            log("","Abrindo - Aguardando Fim de Curso")
            time.sleep(var[1])

        if abrindo and not GPIO.input(17) and not falha:
            print "FALHA NA ABERTURA ",var[1],"s E NAO ABRIU"
            log("","Falha na Abertura - Nao Acionou o Sensor de Fim de Curso ")
            evento("Falha de Abertura- Favor verifique o motor, caso tudo normal limpe a falha")
            falha=1
        #caso o portao abra completamente sao zerados os status
        if abrindo and GPIO.input(17) and not falha:
            abrindo=0
            cmd_a=0
            print "CONFIRMADO ABERTO"
            log("","Portao Aberto com Sucesso")
        
        #----- CICLO DE FECHAMENTO
            
        if GPIO.input(10) and not laco2 and not falha:
            laco2=1
            print "LACO 2 ATIVADO"
            log("","Laço 2 - Ativado")
        #CASO O LAÇO JA TENHA SIDO ATIVDADO/s_aberto/infra ok
        if not cmd_f and laco2 and GPIO.input(17) and GPIO.input(27) and not falha and not var[2]:
            #comando motor 1 segundo
            log("","Comando Fechar")           
            print "CMD FECHAR"
            cmd()
            cmd_f=1
            laco2=0
            print "Aguarda 10 segundos para descolar"
            time.sleep(10)
         #falha no fechamento
        if cmd_f and GPIO.input(17) and not falha:
            print "Falha no Acionamento - Aguardou 10s o Sensor de Aberto Continua Acionado "
            log("","Falha no Acionamento - Aguardou 10s o Sensor de Aberto Continua Acionado")
            evento("Falha de Acionamento- Favor verifique o motor, caso tudo normal limpe a falha")
            falha =1    
        
        #fechando aguarda tempo para confirmar fechado
        if cmd_f and not GPIO.input(17) and not var[2] and not falha:
            fechando =1
            print "Fechando",var[1],"s P/CHEGAR NO FIM"
            log("","Fechando - Aguardando Fim de Curso")
            time.sleep(var[1])
        #falha no fechamento
        if fechando and not GPIO.input(4) and not var[2] and not falha:
            falha=1
            print "FALHA NO FECHAMENTO ",var[1],"s E NAO FECHOU"
            log("","Falha no Fechamento - Nao Acionou o Sensor de Fim de Curso ")
            evento("Falha de Fechamento - Favor verifique o motor, caso tudo normal limpe a falha")

            
        #fechamento por fila
        
        if not tag and not cmd_ff  and not GPIO.input(22) and not GPIO.input(10)and GPIO.input(17) and GPIO.input(27) and not falha and var[2]:
            
            print "aguarda 5 segundo depois as condicoes sao atendidas para verificar se chegou mais algum carro"
            time.sleep(5)
           
            if not tag and not cmd_ff  and not GPIO.input(22) and not GPIO.input(10)and GPIO.input(17) and GPIO.input(27) and not falha and var[2]:
           #comando motor 1 segundo          
                log("","Comando Fechar Fila")           
                print "CMD FECHAR FILA"
                cmd()
                cmd_ff=1
                
                print "Aguarda 10 segundos para descolar"
                time.sleep(10)
        if cmd_ff and GPIO.input(17) and var[2] and not falha:
            print "Falha no Acionamento Fila - Aguardou 10s o Sensor de Aberto Continua Acionado "
            log("","Falha no Acionamento Fila - Aguardou 10s o Sensor de Aberto Continua Acionado")
            evento("Falha de Acionamento Fila - Favor verifique o motor, caso tudo normal limpe a falha")
            falha =1   
            
        if cmd_ff and tag and GPIO.input(22) and var[2]:
            print "CMD PARA REABRIR O PORTAO FILA"
            log("","Comando para parar o portao fila")
            cmd()
            time.sleep(2)
            log("","Comando para reabrir o portao fila")
            cmd()
            cmd_ff=0
            cmd_a=1
            
          
        #confirmado fechado
        if (cmd_ff or cmd_f) and GPIO.input(4):            
            fechando=0
            cmd_f=0
            cmd_ff=0
            print "CONFIRMADO FECHADO"
            log("","Portao Fechado com Sucesso")
        #reset de falhas
        if falha and GPIO.input(9):
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
