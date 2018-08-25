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
        print "erro na leitura"
    
teste_db()    
    

def inserir(tag):
    try:
        cur.execute("INSERT INTO log (tag,descr) VALUES (%s,%s)",(tag,"portao entrada"))
        print"inserido"
        db.commit()
    except:
         print"NAO inserido"
         db.rollback()
        
sp = serial.Serial(port="/dev/ttyAMA0",baudrate=9600,timeout=0.1)
print "teste antena: BaudRate = 9600"
x=0
tagg=b''

while True:
    ant = sp.read()
    if ant != b'':
        x=x+1
        tagg=ant+tagg
        
    if x==17:
        print"tag-->"
        print hexlify(tagg).decode('ascii')
        tagg=hexlify(tagg).decode('ascii')
        inserir(tagg)
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


    
