#usuarios
# -*- coding: utf-8 -*-

from Banco import Banco

class Usuarios(object):


    def __init__(self, nome = "", endereco ="",tag = "", placa = ""):
        self.info = {}
        self.nome = nome
        self.tag = tag
        self.endereco = endereco
        self.placa = placa
        
    def insertUser(self):

        banco = Banco()
        try:

            c = banco.conexao.cursor()
            c.execute("insert into usuarios (nome, tag, endereco) values ('" + self.nome + "', '" + self.tag + "', '" + self.endereco + "' )")

            banco.conexao.commit()
            c.close()

            return "Usuário cadastrado com sucesso!"
        except:
            return "Ocorreu um erro na inserção do Usuário"

    def updateUser(self):

        banco = Banco()
        try:


            c = banco.conexao.cursor()

            c.execute("update usuarios set nome = '" + self.nome + "', tag = '" + self.tag + "', endereco = '" + self.endereco + "' where idusuario = " + self.idusuario + " ")

            banco.conexao.commit()
            c.close()

            return "Usuario atualizado com sucesso!"
        except:
            return "Ocorreu um erro na alteração do usuário"

    def deleteUser(self):

        banco = Banco()

        try:

            c = banco.conexao.cursor()

            c.execute("delete from usuarios where idusuario = " + self.idusuario + " ")

            banco.conexao.commit()
            c.close()

            return "excluido"
        except:
            return "não excluido"

    def selectUser(self, idusuario):
        banco =  Banco()
        try:

            c = banco.conexao.cursor()
            c.execute("select * from usuarios where idusuario = " + idusuario + " ")


            for linha in c:
                self.idusuario = linha[0]
                self.nome = linha[1]
                self.tag = linha[2]
                self.endereco = linha[3]
                

            c.close()

            return " Busca feita com sucesso!"
        except:
            return " Ocorreu um erro na busca do usuário"

    def selectUsernm(self, nome):
        banco =  Banco()
        try:
            sql = "Select * from usuarios where nome=?"
            c = banco.conexao.cursor()
            c.execute(sql, [(nome)])
            print (c.fetchall())


            for linha in c:
                self.idusuario = linha[0]
                self.nome = linha[1]
                self.tag = linha[2]
                self.endereco = linha[3]
                

            c.close()

            return " Busca feita com sucesso!"
        except:
            return " Ocorreu um erro na busca do usuário"

        
    def selectUsertg(self, tag):
        banco =  Banco()
        try:

            c = banco.conexao.cursor()
            c.execute("select * from usuarios where tag = " + tag + " ")


            for linha in c:
                self.idusuario = linha[0]
                self.nome = linha[1]
                self.tag = linha[2]
                self.endereco = linha[3]
                

            c.close()

            return " Busca feita com sucesso!"
        except:
            return " Ocorreu um erro na busca do usuário"
        

    
