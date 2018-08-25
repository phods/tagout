#! /usr/bin/python env
import sys,time
import serial
from struct import *
import binascii
from binascii import hexlify
import MySQLdb
sp = serial.Serial(port="/dev/ttyAMA0",baudrate=9600,timeout=0.1)
print ("teste antena: BaudRate = 9600")
x=0
y=0
tagg=b''
sp.flush()
while True:
    if sp.read()!=b'':
        while y<16:
                  
            sp.read()
            y=y+1
        while x<17:
            
            ant = sp.read()
            if ant != b'':
                x=x+1
                tagg=ant+tagg
                
            if x==17:
                print"tag-->",(hexlify(tagg).decode('ascii'))
                x=0
                y=0
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


    
