#! /usr/bin/python env

import serial
tag=[]
sp = serial.Serial(port="/dev/ttyAMA0",baudrate=9600,timeout=0.1)
print ("teste antena: BaudRate = 9600")

while True:
    i = sp.read()
    
    #print i.encode("hex")
    for i in range(10):
        tag[i]=2
    print tag[0]
    print "tag"
