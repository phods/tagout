
from socket import *
import time


address = ('192.168.0.159', 5000)
client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(1)

while(1):
    print "teste"
    data = "0"
    client_socket.sendto(data, address)

    try:
        print "teste2"
        rec_data, addr = client_socket.recvfrom(2048)
        print rec_data
    except:
        pass

    time.sleep(2)

   
    data = "0"
    client_socket.sendto(data, address)

    try:
        print "teste3"
        rec_data, addr = cliente_socket.recvfrom(2048)
        print rec_data
    except:
        pass

    time.sleep(2)
