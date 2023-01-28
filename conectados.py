#from typing import final
from flask import Flask, render_template, request, redirect, make_response
from markupsafe import escape

import datetime

OK =  1
KO =  0

#declaracion de variables globales

#Fin declaracion de variables globales


class Conectados:   
    __conectados=[]

    def __init__(self):
        pass

    def borra(self,user):
        for x in self.__conectados:
            if(x['usuario']==user):
                print(x)
                self.__conectados.remove(x)
                return OK

        return KO

    def crea(self,user):
        self.__conectados.append({'usuario':user,'expira':datetime.datetime.now()})

        return OK

    def busca(self,user):
        for x in self.__conectados:
            if(x['usuario']==user):
                #print(x['usuario'])
                return x

        return KO

    def lista(self):
        return self.__conectados

    def compruebaExpirado(self,user,timeOut):
        #Si ahora es mayor de tiempo + timeOut devuelve cierto
        #si no, devuelve falso
        x=self.busca(user)
        if(x==KO):
            return False

        finValidez = x['expira'] + datetime.timedelta(minutes=timeOut)
        if (datetime.datetime.now()>finValidez):
            return False
        else:
            return True

    def renueva(self,user,timeOut):
        #Si ahora es mayor de tiempo + timeOut devuelve cierto y actualiza la fecha de expiracion a ahora
        #si no, devuelve falso y lo borra de la lista
        x=self.busca(user)
        if(x==KO):
            return False

        if(self.compruebaExpirado(user,timeOut)):
            x['expira']=datetime.datetime.now()
            return True
        else:
            self.__conectados.remove(x)
            return False