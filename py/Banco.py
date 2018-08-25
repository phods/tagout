#Banco de dados + Tkinter

#importando modulo do SQlite
import sqlite3


class Banco():
    def __init__(self):
        self.conexao = sqlite3.connect('bank.db')
        self.createTable()
        

    def createTable(self):
        c = self.conexao.cursor()

       
        c.execute("""create table if not exists usuarios (idusuario integer primary key autoincrement , nome text, tag text,endereco text)""")
        self.conexao.commit()
        c.close()
   
                
        

        
