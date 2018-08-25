#Banco de dados + Tkinter

#importando modulo do SQlite
import MySQLdb


class Banco():
    def __init__(self):
        self.conexao = MySQLdb.connect(host="localhost", user="root", passwd="toor",db="arduino")

   
                
        

        
