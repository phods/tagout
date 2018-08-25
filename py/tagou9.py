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
CMD_MOT2=24
CMD_EMERG2=23
C_HRT=13
#SAIDA RELE
GPIO.setup(18,GPIO.OUT) #CMD_MOTOR1
GPIO.setup(23,GPIO.OUT) #CMD_EMERG1
GPIO.setup(24,GPIO.OUT) #CMD_MOTOR2
GPIO.setup(25,GPIO.OUT) #CMD_EMERG2
GPIO.setup(C_HRT,GPIO.OUT)  #HEARTBEAT
#SAIDA SIMPLES
#GPIO.setup(C_HRT,GPIO.OUT)  #HEARTBEAT
#---INPUT---
S1_FEC=4
S1_ABE=17
S1_INF=27
S1_LAC1=22
S1_LAC2=10
S2_FEC=9
S2_ABE=11
S2_INF=7
S2_LAC1=8
GPIO.setup(S1_FEC,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   #S_FECHADO
GPIO.setup(S1_ABE,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_ABERTO
GPIO.setup(S1_INF,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_INFRA
GPIO.setup(S1_LAC1,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_LACO1
GPIO.setup(S1_LAC2,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_LACO2
GPIO.setup(S2_FEC,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   #S_FECHADO
GPIO.setup(S2_ABE,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_ABERTO
GPIO.setup(S2_INF,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_INFRA
GPIO.setup(S2_LAC1,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  #S_LACO1
GPIO.setup(2,GPIO.IN)   #RESERVA
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
#pegar o mac
def getmac(interface):
    try:
        mac=open('/sys/class/net/'+interface+'/address').readline()
    except:
        mac="00:00:00:00:00:00"
    return mac[0:17]

print getmac("eth0")

#testar conexao com banco de dados
def dba():
    try:
        cur.execute("SELECT VERSION()")
        ver=cur.fetchone()
        print "ver",ver
        if ver:
            return True
        else:
            return False
    except MySQLdb.Error:
        print "ERROR %d IN CONNECTION: %s"% (e.args[0],e.args[1])
    return False
#db()

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#handle the emerg event
def emerg(pin):
    print"----->>>> EMERGENCIA <<<<-----"
    x=0
    while x<10:
        GPIO.output(pin,True)
        time.sleep(0.5)
        GPIO.output(pin,False)
        time.sleep(0.5)
        x=x+1
    evento("================>>>>>>EMERGENCIAAAAAAAA<<<<<================")
#declare event
#GPIO.add_event_detect(S1_INF,GPIO.FALLING)
#GPIO.add_event_callback(S1_INF,EmergEvent)
#-----
#------logica para repeticao a cada 10s
#threading.Timer(5,heart).start()
#**********************************
def cmd_p1():
    try:
        GPIO.output(CMD_MOT1,True)
        time.sleep(0.80)
        GPIO.output(CMD_MOT1,False)
        print "CMD_M1 ACIONADO"
        log("","Motor1 - Comando Acionado")
    except:
        print "CMD_M2 NAO EXECUTADO"
        log ("","Motor1 - Comando Nao Executado")
def cmd_p2():
    try:
        GPIO.output(CMD_MOT2,True)
        time.sleep(0.80)
        GPIO.output(CMD_MOT2,False)
        print "CMD_M2 ACIONADO"
        log("","Motor2 - Comando Acionado")
    except:
        print "CMD_M2 NAO EXECUTADO"
        log ("","Motor2 - Comando Nao Executado")
def heart():
    for i in range (0,3):
        GPIO.output(C_HRT,True)
        time.sleep(0.20)
        GPIO.output(C_HRT,False)
        time.sleep(0.20)
def log(tag,desc):
    try:
        if tag == "":
            cur.execute("INSERT INTO log (tag,descr) VALUES (%s,%s)",(tag,"PY - "+desc))
            print"LOG inserido sem tag"
            db.commit()
        else:
            cur.execute("SELECT tag FROM log WHERE tag != ''  ORDER BY id_log DESC LIMIT 1")
            for row in cur.fetchall():
                #print row[0]
                if row[0]!=tag:
                    cur.execute("INSERT INTO log (tag,descr) VALUES (%s,%s)",(tag,"PY - "+desc))
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
    val=[]
    cur.execute("SELECT * FROM acesso WHERE id_acesso=%s ",id_portao)
    for row in cur.fetchall():
        val=row        
    return val
#val[0]=id_acesso/3-id_tipo/4-id_modo/8-cmd_manual/9-rec_falha/10-bypass/
#11-tempo_abertura/12-chave_fila/13-mac
def temp(x,y,z):
    if x==1:
        y=time.time()
        return y
    if x==0:
        y=time.time()-y
        if y>z:
            return 1
        else:
            return 0


#*****************************************************************
def main():
    print"SISTEMA DE CONTROLE DE ACESSO - TAGOUT"

    tag=0
    cmd_a=0
    cmd_f=0
    cmd_ff=0
    abrindo=0
    fechando=0
    laco2=0
    falha=0
    #########
    cmd2_a=0
    cmd2_f=0
    cmd2_ff=0
    abrindo2=0
    fechando2=0
    laco3=0
    falha2=0

    id_portao1=13
    id_portao2=14
    #run=raw_input("START? > ")

 #---------------------------------
    while True:

        portao1=atualiza_valores(id_portao1)
        portao2=atualiza_valores(id_portao2)
        tag= read_tag()
       

        #---COMANDO MANUAL
        if portao1[9]==1:
            print"Portao1 - comando manual"
            log("","POrtao1 - Comando Manual Acionado")
            cmd_p1()
            #id do portao
            cmd_manual_reset(id_portao1)
        
        if portao2[9]==1:
            print"POrtao2 - comando manual"
            log("","POrtao2 -Comando Manual Acionado")
            cmd_p2()
            #id do portao
            cmd_manual_reset(id_portao2)
        #---EMERGENCIA
        if fechando and not GPIO.input(S1_INF) and not falha:
            emerg(CMD_EMERG1)
            falha=1
        if fechando2 and not GPIO.input(S2_INF) and not falha2:
            emerg(CMD_EMERG2)
            falha2=1
        #bypass ativo
        if not portao1[11]:
            ############################################
            #CICLO DE ABERTURA
            #tag laco1 e portao fechado
            #print "T,CA,CF,SA,SF,I,L1,L2,F"
            #print tag,",",cmd_a,",",cmd_f,",",GPIO.input(S1_FEC),",",GPIO.input(S1_ABE),",",GPIO.input(S1_INF),",",GPIO.input(S1_LAC1),",",GPIO.input(S1_LAC2),",",falha
            if not cmd_a and tag and GPIO.input(S1_FEC) and GPIO.input(S1_LAC1) and not falha:
                print "Portao 1 - Comando Abrir"
                log("","Portao 1 - Comando Abrir Portao")
                #comando motor 1 segundo
                cmd_p1()
                cmd_a=1
                #delay para esperar o portao descolar do sensor
                print "Aguarda 10 segundos para descolar"
                #habilita o timer apos o comando
                temp1=temp(1,0,0)
            #msg verifica se passaram 10 s
            if cmd_a and GPIO.input(S1_FEC)  and not falha and temp(0,temp1,10):
                falha=1
                print "Portao 1 - Falha no Acionamento - Aguardou 10s o Sensor de Fechado Continua Acionado "
                log("","Portao 1 - Falha no Acionamento - Aguardou 10s o Sensor de Fechado Continua Acionado")
                evento("Portao 1 - Falha de Acionamento - Favor verifique o motor, caso tudo normal limpe a falha")
            #var abrindo e timer de 30s
            if cmd_a and not GPIO.input(S1_FEC) and not falha :
                abrindo=1
                print "Portao 1 - Aguarda",portao1[12],"s P/CHEGAR NO FIM"
                log("","Portao 1 - Abrindo - Aguardando Fim de Curso")

            if abrindo and not GPIO.input(S1_ABE) and not falha and temp(0,temp1,portao1[12]):
                print "Portao 1 - FALHA NA ABERTURA ",portao1[12],"s E NAO ABRIU"
                log("","Portao 1 - Falha na Abertura - Nao Acionou o Sensor de Fim de Curso ")
                evento("Portao 1 - Falha de Abertura- Favor verifique o motor, caso tudo normal limpe a falha")
                falha=1
            #caso o portao abra completamente sao zerados os status
            if abrindo and GPIO.input(S1_ABE) and not falha:
                abrindo=0
                cmd_a=0
                temp1=0
                print "Portao 1 - CONFIRMADO ABERTO"
                log("","Portao1 Aberto com Sucesso")

            #----- CICLO DE FECHAMENTO

            if GPIO.input(S1_LAC2) and not laco2 and not falha:
                laco2=1
                print "Portao 1 - LACO 2 ATIVADO"
                log("","Portao 1 - Laço 2 - Ativado")
            #CASO O LAÇO JA TENHA SIDO ATIVDADO/s_aberto/infra ok
            if not cmd_f and laco2 and GPIO.input(S1_ABE) and GPIO.input(S1_INF) and not falha and not portao1[13]:
                #comando motor 1 segundo
                log("","Portao 1 - Comando Fechar")
                print "Portao 1 - CMD FECHAR"
                cmd_p1()
                cmd_f=1
                laco2=0
                print "Aguarda 10 segundos para descolar"
                #habilita o timer apos o comando
                temp1=temp(1,0,0)

            #falha no fechamento
            if (cmd_ff or cmd_f) and GPIO.input(S1_ABE) and not falha and temp(0,temp1,10):
                print "Portao 1 - Falha no Acionamento - Aguardou 10s o Sensor de Aberto Continua Acionado "
                log("","Portao 1 - Falha no Acionamento - Aguardou 10s o Sensor de Aberto Continua Acionado")
                evento("Portao 1 - Falha de Acionamento- Favor verifique o motor, caso tudo normal limpe a falha")
                falha =1

            #fechando aguarda tempo para confirmar fechado
            if (cmd_ff or cmd_f) and not GPIO.input(S1_ABE)  and not falha:
                fechando =1
                print "Portao 1 - Fechando",portao1[12],"s P/CHEGAR NO FIM"
                log("","Portao 1 - Fechando - Aguardando Fim de Curso")

            #falha no fechamento
            if fechando and not GPIO.input(S1_FEC) and not falha and temp(0,temp1,portao1[12]):
                    falha=1
                    print "Portao 1 - FALHA NO FECHAMENTO ",portao1[1],"s E NAO FECHOU"
                    log("","Portao 1 - Falha no Fechamento - Nao Acionou o Sensor de Fim de Curso ")
                    evento("Portao 1 - Falha de Fechamento - Favor verifique o motor, caso tudo normal limpe a falha")

            #fechamento por fila
            if not tag and not cmd_ff  and not GPIO.input(S1_LAC1) and not GPIO.input(S1_LAC2)and GPIO.input(S1_ABE) and GPIO.input(S1_INF) and not falha and portao1[13]:

                print "aguarda 5 segundo depois as condicoes sao atendidas para verificar se chegou mais algum carro"
                time.sleep(5)

                if not tag and not cmd_ff  and not GPIO.input(S1_LAC1) and not GPIO.input(S1_LAC2)and GPIO.input(S1_ABE) and GPIO.input(S1_INF) and not falha and portao1[13]:
                        #comando motor 1 segundo
                        log("","Portao 1 - Comando Fechar Fila")
                        print "Portao 1 - CMD FECHAR FILA"
                        cmd_p1()
                        cmd_ff=1
                        #inicia o timer
                        temp1=temp(1,0,0)

                        print "Aguarda 10 segundos para descolar"

            #caso tenho fila e a selecao habilitada o portao reabrira
            if cmd_ff and tag and GPIO.input(S1_LAC1) and portao1[13]:
                    print "Portao 1 - CMD PARA REABRIR O PORTAO FILA"
                    log("","Portao 1 - Comando para parar o portao fila")
                    cmd_p1()
                    time.sleep(2)
                    log("","Portao 1 - Comando para reabrir o portao fila")
                    cmd_p1()
                    cmd_ff=0
                    cmd_a=1

            #confirmado fechado
            if (cmd_ff or cmd_f) and GPIO.input(S1_FEC):
                    fechando=0
                    cmd_f=0
                    cmd_ff=0
                    temp1=0
                    print "Portao 1 - CONFIRMADO FECHADO"
                    log("","Portao 1 - Portao Fechado com Sucesso")

        if not portao2[11]:
            # PORTAO 2 - SAIDA SIMPLES ###########################################
            #comando p/ abrir, se fechado e sensor ativo
            if not cmd2_a and GPIO.input(S2_FEC) and GPIO.input(S2_LAC1) and not falha2:
                print "Comando Abrir - PORTAO2"
                log("","POrtao 2 - Comando Abrir Portao")
                #comando motor 2 segundo
                cmd_p2()
                cmd2_a=1
                #delay para esperar o portao descolar do sensor
                print "Aguarda 10 segundos para descolar"
                temp2=temp(1,0,0)

            #msg falha na abertura
            if cmd2_a and GPIO.input(S2_FEC) and not falha2 and temp(0,temp2,10):
                falha2=1
                print "Portao 2 - Falha no Acionamento - Aguardou 10s o Sensor de Fechado Continua Acionado "
                log("","Portao 2 - Falha no Acionamento - Aguardou 10s o Sensor de Fechado Continua Acionado")
                evento("Portao 2 -Falha de Acionamento  - Favor verifique o motor, caso tudo normal limpe a falha")
            #var abrindo e timer de 30s
            if cmd2_a and not GPIO.input(S2_FEC) and not falha2:
                abrindo2=1
                print "Portao 2 - Aguarda",portao2[1],"s P/CHEGAR NO FIM"
                log("","POrtao 2 - Abrindo - Aguardando Fim de Curso")

            if abrindo2 and not GPIO.input(S2_ABE) and not falha2 and temp(0,temp2,portao2[12]):
                print "Portao 2 - FALHA NA ABERTURA ",portao2[12],"s E NAO ABRIU"
                log("","Portao 2 - Falha na Abertura - Nao Acionou o Sensor de Fim de Curso ")
                evento("Portao 2 - Falha de Abertura- Favor verifique o motor, caso tudo normal limpe a falha")
                falha2=1
            #caso o portao abra completamente sao zerados os status
            if abrindo2 and GPIO.input(S2_ABE) and not falha2:
                abrindo2=0
                cmd2_a=0
                temp2=0
                print "Portao 2 - CONFIRMADO ABERTO"
                log("","Portao 2 Aberto com Sucesso")

            #----- CICLO DE FECHAMENTO
            
            #CASO O LAÇO JA TENHA SIDO ATIVDADO/s_aberto/infra ok
            if not cmd_f and not GPIO.input(S2_LAC1) and GPIO.input(S2_ABE) and GPIO.input(S2_INF) and not falha2 and not portao2[13]:
                #comando motor 1 segundo
                log("","Portao 2 - Comando Fechar")
                print "Portao 2 - CMD FECHAR"
                cmd_p2()
                cmd2_f=1

                print "Aguarda 10 segundos para descolar"
                temp2=temp(1,0,0)
            #falha no fechamento
            if cmd2_f and GPIO.input(S2_ABE) and not falha2 and not portao2[2] and temp(0,temp2,10):
                print "Portao 2 - Falha no Acionamento - Aguardou 10s o Sensor de Aberto Continua Acionado "
                log("","Portao 2 - Falha no Acionamento - Aguardou 10s o Sensor de Aberto Continua Acionado")
                evento("Portao 2 - Falha de Acionamento- Favor verifique o motor, caso tudo normal limpe a falha")
                falha2 =1

            #fechando aguarda tempo para confirmar fechado
            if cmd2_f and not GPIO.input(S2_ABE) and not falha2 and not portao2[13]:
                fechando2 =1
                print "Portao 2 - Fechando",portao2[12],"s P/CHEGAR NO FIM"
                log("","Portao 2 - Fechando - Aguardando Fim de Curso")

            #falha no fechamento
            if fechando2 and not GPIO.input(S2_FEC) and not falha2 and not portao2[2] and temp(0,temp2,portao2[12]):
                    falha2=1
                    print "Portao 2 - FALHA NO FECHAMENTO ",portao2[12],"s E NAO FECHOU"
                    log("","Portao 2 - Falha no Fechamento - Nao Acionou o Sensor de Fim de Curso ")
                    evento("Portao 2 - Falha de Fechamento - Favor verifique o motor, caso tudo normal limpe a falha")
            ######fechamento por fila
            if not cmd2_ff  and not GPIO.input(S2_LAC1) and GPIO.input(S2_ABE) and GPIO.input(S2_INF) and not falha2 and portao2[13]:

                print "aguarda 5 segundo depois as condicoes sao atendidas para verificar se chegou mais algum carro"
                tempo(5)

                if not cmd2_ff  and not GPIO.input(S2_LAC1) and GPIO.input(S2_ABE) and GPIO.input(S2_INF) and not falha2 and portao2[13]:
                        #comando motor 1 segundo
                        log("","Portao 2 - Comando Fechar Fila")
                        print "Portao 2 - CMD FECHAR FILA"
                        cmd_p2()
                        cmd2_ff=1
                        print "Aguarda 10 segundos para descolar"
                        temp2=temp(1,0,0)
            if cmd2_ff and GPIO.input(S2_ABE) and portao2[2] and not falha2 and temp(0,temp2,10):
                    print "Portao 2 - Falha no Acionamento Fila - Aguardou 10s o Sensor de Aberto Continua Acionado "
                    log("","Portao 2 - Falha no Acionamento Fila - Aguardou 10s o Sensor de Aberto Continua Acionado")
                    evento("Portao 2 - Falha de Acionamento Fila - Favor verifique o motor, caso tudo normal limpe a falha")
                    falha2 =1

            if cmd2_ff and  GPIO.input(S2_LAC1) and portao2[13]:
                    print "Portao 2 - CMD PARA REABRIR O PORTAO FILA"
                    log("","Portao 2 - Comando para parar o portao fila")
                    cmd_p2()
                    tempo(2)
                    log("","Portao 2 - Comando para reabrir o portao fila")
                    cmd_p2()
                    cmd2_ff=0
                    cmd2_a=1
            #confirmado fechado
            if  (cmd2_ff or cmd2_f) and GPIO.input(S2_FEC):
                    fechando2=0
                    cmd2_f=0
                    cmd2_ff=0
                    temp2=0
                    print "Portao 2 - CONFIRMADO FECHADO"
                    log("","Portao 2 - Fechado com Sucesso")
        ############################################
        #reset de falhas
        if falha and portao1[10]:
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
            temp1=0
        if falha2 and portao2[10]:
            print "Portao 2 - RESET FALHAS "
            log("","Portao 2 - Reset De Falhas")
            falha2 =0
            reset2=0
            cmd2_a=0
            cmd2_f=0
            temp2=0
            abrindo2=0
            fechando2=0

if __name__=="__main__":
    main()
