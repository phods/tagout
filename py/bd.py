import MySQLdb
import time
db = MySQLdb.connect(host="localhost", user="root", passwd="toor",db="arduino")
cur = db.cursor()
var=0
var1=0


cur.execute("SELECT temp_tag FROM rfid_temp WHERE id=1")
for row in cur.fetchall():
        
    var=row[0]
    print var
    time.sleep(2)

cur.execute("SELECT tag FROM tabelarfid WHERE tag=%s ",var)
for row in cur.fetchall():
       
    var1=row[0]
    print var1
    time.sleep(2)
    
if var==var1:
    print"encontrou"
else:
    print"NAO encontou"
    #print "valor:%s"%var
   # print row[1]
   # print row[2]
   # print row[3]
#con.commit()
#print 'DATAbase version :%s'%data
db.close
