#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Tkinter import *
import MySQLdb
from socket import *
import tkMessageBox
import threading
import RPi.GPIO as GPIO
import time
from threading import Timer
#**********************************
#configuracao socket udp
#address=('192.168.15.56',5000)
#client_socket = socket(AF_INET,SOCK_DGRAM)
#client_socket.settimeout(1)
#**********************************
#tell the GPIO module tha we want to use the
#chip's pin numbrering scheme
GPIO.setmode(GPIO.BCM)

#---OUTPUT---
GPIO.setup(18,GPIO.OUT) #CMD_MOTOR
GPIO.setup(23,GPIO.OUT) #CMD_EMERG
#GPIO.setup(24,GPIO.OUT) #RESERVA
#GPIO.setup(25,GPIO.OUT) #RESERVA
#GPIO.setup(8,GPIO.OUT)  #RESERVA
#---INPUT---
GPIO.setup(4,GPIO.IN) #S_FECHADO
GPIO.setup(17,GPIO.IN)  #S_ABERTO
GPIO.setup(27,GPIO.IN)  #S_INFRA
GPIO.setup(22,GPIO.IN)  #S_LACO1
GPIO.setup(10,GPIO.IN)  #S_LACO2
GPIO.setup(9,GPIO.IN)   #RESERVA
#GPIO.setup(11,GPIO.IN)  #RESERVA
#GPIO.setup(7,GPIO.IN)   #RESERVA
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
#def f():
#do something here
#call f() again in 60 seconds
    #print"chamada da verificacaode tag"
    #threading.Timer(10,f).start()
    
#----------------------------
#--------------------------------------------------------
def cmd_open():
    print"cmd abrir"
    # se portao fechado e laco 1 ativado
    if GPIO.input(4) and GPIO.input(22):
            #the button is pressed
            GPIO.output(18,True)
            time.sleep(0.80)
            GPIO.output(18,False)
            print "CMD ABRIR"
def cmd_close():
    print"cmd abrir"
    # se portao fechado e laco 1 ativado
    if GPIO.input(17) and GPIO.input(27):
            #the button is pressed
            GPIO.output(18,True)
            time.sleep(0.80)
            GPIO.output(18,False)
            print "CMD FECHAR"
            
def comparar():
    db = MySQLdb.connect(host="localhost", user="root", passwd="toor",db="arduino")
    cur = db.cursor()
        
    var_bd=0
    var_temp=0
    var_cmd=0

   #le o tag temporario
    cur.execute("SELECT temp_tag FROM rfid_temp order by ID desc limit 1")
    for row in cur.fetchall():
        var_temp=row[0]
        var_temp= "189-255-255-172-255-255-255-181-255-255-57-255-255"
        #print"var_temp",var_temp
   #pesquisa no banco se existe o tag 
    cur.execute("SELECT tag FROM tabelarfid WHERE tag=%s ",var_temp)
    for row in cur.fetchall():
        var_bd=row[0]
        #print"var_bd  ",var_bd
    
        
    if(var_bd==var_temp and var_bd!=" "):
        cur.execute("SELECT * FROM tabelarfid WHERE tag=%s",var_bd)
        for row in cur.fetchall():
            row[0]
            row[1]
            vartag=row[2]
            varnome=row[3]
            varend=row[4]
            
        #print"encontrou"
        return (1)
       
        #comando para abrir o portao
        cmd_open()
      
    else:
        #print"NAO encontou"
        return (0)
                
#------logica para repeticao a cada 10s       
    #threading.Timer(10,comparar).start()
   
#*****************************************************************    
def main():
    cmd_a=0
    cmd_f=0
    abrindo=0
    fechando=0
    emerg=0
    laco2=0
    falha=0

    run=raw_input("start? > ")


 #---------------------------------   
    while True:
        tag= comparar()
        
        #CLICLO DE ABERTURA
        #comando abrir tem o s_fechado e laço1
        if not cmd_a and tag and GPIO.input(4) and GPIO.input(22) and not falha:
            #comando motor 1 segundo
            GPIO.output(23,True)
            time.sleep(1)
            GPIO.output(23,False)
            print "CMD ABRIR"
            cmd_a = True
            #delay para esperar o portao descolar do sensor
            print "conta 5 segundos para descolar"
            time.sleep(5)
         #msg falha na abertura   
        if cmd_a and GPIO.input(4) and not falha:
            falha=1
            print "FALHA NO ACIONAMENTO"
         #var abrindo e timer de 30s   
        if cmd_a and not GPIO.input(4) and not falha:
            abrindo=1
            print "conta 30 segundos P/CHEGAR NO FIM"
            time.sleep(30)

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
        if not cmd_f and laco2 and GPIO.input(17) and GPIO.input(27):
            #comando motor 1 segundo
            GPIO.output(23,True)
            time.sleep(1)
            GPIO.output(23,False)
            print "CMD FECHAR"
            cmd_f=1
            print "conta 5 segundos para descolar"
            time.sleep(5)
        #falha no fechamento
        if cmd_f and GPIO.input(17):
            print "falha no fechamento"
        if cmd_f and not GPIO.input(17):
            fechando =1
            print "conta 30 segundos ENCOSTAR NO FIM DE CURSO"
            time.sleep(30)
        if cmd_f and not GPIO.input(4):
            print "falha no fechamento sensor "

        if cmd_f and GPIO.input(4):
            print "portao fechadno com sucesso "
            fechando=0
            cmd_f=0

        if falha and GPIO.input(9):
            print "RESET FALHAS "
            falha =0
            reset=0
            cmd_a=0
            cmd_f=0
            
            

            
            
                
        #print "button pushed"

        #GPIO.cleanup()

        time.sleep(5.80)
#db.close



comparar()
if __name__=="__main__":
    main()




