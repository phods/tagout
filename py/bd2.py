import MySQLdb
from socket import *
import time

#configuracao socket udp
address=('192.168.25.159',5000)
client_socket = socket(AF_INET,SOCK_DGRAM)
client_socket.settimeout(1)


db = MySQLdb.connect(host="localhost", user="root", passwd="toor",db="arduino")
cur = db.cursor()
var=0
var1=0
data=0


#cur.execute("SELECT temp_tag FROM rfid_temp WHERE id=1")
cur.execute("SELECT temp_tag FROM rfid_temp order by ID desc limit 1")
for row in cur.fetchall():
        
    var=row[0]
    print var
    time.sleep(2)

cur.execute("SELECT tag FROM tabelarfid WHERE tag=%s ",var)
for row in cur.fetchall():
       
    var1=row[0]
    print var1
    time.sleep(2)
    
if(var==var):
    print"encontrou"

    data="0"
    client_socket.sendto(data,address)
    try:
        rec_data,addr=client_socket.recvfrom(2048)
        print "fdsf %s",rec_data
    except:
        pass
    
else:
    print"NAO encontou"
    #print "valor:%s"%var
   # print row[1]
   # print row[2]
   # print row[3]
#con.commit()
#print 'DATAbase version :%s'%data
db.close
