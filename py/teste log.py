#! /usr/bin/python env
import sys
import serial
from struct import *
import binascii
from binascii import hexlify
import MySQLdb
from sshtunnel import SSHTunnelForwarder

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



    
def teste_db():
    try:
        cur.execute("SELECT * FROM logs WHERE 1")
        for row in cur.fetchall():
            print row[0]
            print row[1]
            print row[2]
            print row[3]
    except:
        print "erro na fun~ao testedb()"
    

def inserir(tag):
    try:
        cur.execute("INSERT INTO usuario (tag) VALUES (%s)",(tag))
        print"inserido"
        db.commit()
                
    except:
         print"NAO inserido"
         db.rollback()
def comparar(tag):
    
   # db=MySQLdb.connect(host="192.168.16.6",user="root",passwd="toor",db="wordpress")
   # cur=db.cursor()
        
    tag_bd=0
    
    var_cmd=0
    #print "tag a ser comparado na base"
    #print tag
   
    #pesquisa no banco se existe o tag 
    #cur.execute("SELECT tag FROM usuario WHERE tag=%s ",tag)
    cur.execute("SELECT tag FROM usuario order by id_user DESC LIMIT 1")
    for row in cur.fetchall():
        tag_bd=row[0]
        print tag_bd
        if tag_bd==tag:
            print "tag ja na base"
        else:
            inserir(tag)
            #cur.execute("SELECT tag FROM usuario order by id_user DESC LIMIT 1")
            cur.execute("SELECT id_user FROM usuario WHERE tag=%s ",tag)
            for row in cur.fetchall():
                print row[0]

def log1(tag,desc):
    try:
        print tag
        x=1
        y=0
        while not y:
            cur.execute("SELECT tag FROM log order by id_log DESC LIMIT 1")
            for row in cur.fetchall():
                print"entrou no for"
                if tag!="":
                    if row[0]!=tag:
                        cur.execute("INSERT INTO log (tag,descr) VALUES (%s,%s)",(tag,desc))
                        print"LOG inserido com tag"
                        db.commit()
                    print"escreveu no y"
                    y=1
                else:
                    cur.execute("INSERT INTO log (tag,descr) VALUES (%s,%s)",(tag,desc))
                    print"LOG inserido sem tag"
                    db.commit()
                    y=1
                    
            x=x+1
    except:
         print"LOG NAO inserido"
         db.rollback()
def log(tag,desc):
    try:

        if tag == "":
            cur.execute("INSERT INTO log (tag,descr) VALUES (%s,%s)",(tag,desc))
            print"LOG inserido sem tag"
            db.commit()
        else:
                   
            cur.execute("SELECT tag FROM log WHERE tag != ''  ORDER BY id_log DESC LIMIT 1")
            for row in cur.fetchall():
                print row[0]
                if row[0]!=tag:
                    cur.execute("INSERT INTO log (tag,descr) VALUES (%s,%s)",(tag,desc))
                    print"LOG inserido c/ tag"
                    db.commit()
                else:
                    print"esse ja eh o ultimo tag q entrou"
                
    except:
         print"LOG NAO inserido"
         db.rollback()        
#--------------------------------------------------------------      
sp = serial.Serial(port="/dev/ttyAMA0",baudrate=9600,timeout=0.1)
print "teste antena: BaudRate = 9600"
x=0
tagg=b''

while True:
    log("","ABCDEFGRTEWUILKJKLDFGSDFNM,NCV,NBM,XNBXHJKDFGHFJKHGKJSHGJKDSGHJKSDOIRUEWO52346982768957825689")
    ant = sp.read()
    if ant != b'':
        x=x+1
        tagg=ant+tagg
        
        
    if x==17:
        #print"tag-->"
        #print hexlify(tagg).decode('ascii')
        tagg=hexlify(tagg).decode('ascii')
        log(tagg,"ghh")
        x=0
        
        tagg=b''
        
"""
    #print(b'\xE2\x82\xAC'.decode('UTF-8'))
#a=b'\x00'+ b'\x00'+ b'\xe2'+ b'\x00'+ b'0'+ b'\x98'+b'\x07'+ b'\x02'+ b'\x02'+ b'c'+ b'\x13'+        b'`'+b'\x8b'+ b'n'+ b'\x00'+ b'|'+ b'\xff'
a=b'\xff\x96\x00\xa4,`"c\x02\x02\x07\x980\x00\xe2\x00\x00'
print(binascii.hexlify(a))
print(hexlify(a).decode('ascii'))

[b'\x00', b'\x00', b'\xe2', b'\x00', b'0', b'\x98',
        b'\x07', b'\x02', b'\x02', b'c', b'\x13',
        b'`', b'\x8b', b'n', b'\x00', b'|', b'\xff']
        ff960-0a42c-60226-30202-07983-000e2-0000    
"""


    
