from flask import Flask, render_template, request, Response, redirect, send_file, url_for, make_response
from hashlib import md5
from werkzeug.utils import secure_filename
from markupsafe import escape
from flask_mqtt import Mqtt
from html import unescape

import requests as outputRequests
import datetime
import json
import sys
import os

import MySQLdb

import config
import conectados


OK = 1
KO = 0
DISPOSITIVO_VALIDADO    = 1
DISPOSITIVO_NO_VALIDADO = 0

#declaracion de variables globales
configFile='config/config.json'
timeOutSesion=10 #time out de sesion en minutos

usuarioValidado={}
nombrePrincipio=""
nombreRojo=""
nombreFinal=""
principio=""
rojo=""
final=""
pie=""

mqtt_client = Mqtt()

app = Flask(__name__)
#Fin de declaracion de variables globales

#************************************************* GUI usuario *************************************************************
@app.route('/')
def raiz_bis():
    pagina = 'templates/div_login.html'

    usuario = request.cookies.get('userID')
    if not usuario:
        usuario=""
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            usuario=""            
        else:
            pagina = 'templates/div_main.html'
        
    fichero = open(pagina)    
    delante = fichero.read()
    detras = ""
    return render_template('inicio.html', DELANTE=delante, DETRAS=detras,NOMBRE_PRINCIPIO=nombrePrincipio, NOMBRE_ROJO=nombreRojo, NOMBRE_FINAL=nombreFinal, PRINCIPIO=principio, ROJO=rojo, FINAL=final, PIE=pie, USUARIO=usuario)

"""OLD"""
@app.route('/old')
def raiz():
    usuario = request.cookies.get('userID')
    if not usuario:
        usuario=""
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            usuario=""

    return render_template('index.html', NOMBRE_PRINCIPIO=nombrePrincipio, NOMBRE_ROJO=nombreRojo, NOMBRE_FINAL=nombreFinal, PRINCIPIO=principio, ROJO=rojo, FINAL=final, PIE=pie, USUARIO=usuario)

@app.route('/main')
def main():
    usuario = request.cookies.get('userID')
    if not usuario:
        usuario=""
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            usuario=""

    usuarioValidado = dameUsuario(usuario)

    return render_template('/main.html',NOMBRE=usuarioValidado['Nombre'], APELLIDOS=usuarioValidado['Apellidos'], CORREO=usuarioValidado['Correo'], TELEFONO=usuarioValidado['Telefono'], DIRECCION=usuarioValidado['Direccion'], USUARIO=usuario)
"""OLD"""

@app.route('/datosUsuario')
def datosUsuario():
    usuario = request.cookies.get('userID')
    if not usuario:
        print("---------------->Sin cookie")
        return redirect('/',302)
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            print("---------------->No se puede renovar")
            return redirect('/',302)

    usuarioValidado = dameUsuario(usuario)

    #return render_template('/datosUsuario.html',NOMBRE=usuarioValidado['Nombre'], APELLIDOS=usuarioValidado['Apellidos'], CORREO=usuarioValidado['Correo'], TELEFONO=usuarioValidado['Telefono'], DIRECCION=usuarioValidado['Direccion'], USUARIO=usuarioValidado['Usuario'])
        
    delante = render_template('div_datosUsuario.html',NOMBRE=usuarioValidado['Nombre'], APELLIDOS=usuarioValidado['Apellidos'], CORREO=usuarioValidado['Correo'], TELEFONO=usuarioValidado['Telefono'], DIRECCION=usuarioValidado['Direccion'], USUARIO=usuarioValidado['Usuario'])
    detras = ""
    return render_template('inicio.html', DELANTE=delante, DETRAS=detras,NOMBRE_PRINCIPIO=nombrePrincipio, NOMBRE_ROJO=nombreRojo, NOMBRE_FINAL=nombreFinal, PRINCIPIO=principio, ROJO=rojo, FINAL=final, PIE=pie, USUARIO=usuario)

@app.route('/debug')
def debug():
    return usuarioValidado

@app.route('/debug2')
def debug2():
    return "IP: " + str(IP) + ", puerto: " + str(puerto) + ", bd IP: " + str(dbIP) + ", puerto bd: " + str(dbPuerto) + ", nombre bd: " + str(dbUsuario) + ", password bd: " + str(dbPassword) + ", nombre bd: " + str(dbNombre)

@app.route('/validaUsuario')
def validarUsuario():
    result = 0
    username = str(request.args.get('username'))
    password_txt = str(request.args.get('password'))
    password = md5(password_txt.encode("utf-8")).hexdigest()

    print("usuario: " + username + " password: " + password)

    sql = "select Nombre, Apellidos, Correo, Telefono, Direccion_ppal from Usuarios where Usuario = '" + username + "' and Password='" + password + "'"
    #print ("Consulta: " + sql)

    try:
        cursor.execute(sql)
    except Exception as e: 
        print(e)  
        print("Error en la consulta")       

    #Si he encontrado el usaurio
    if (cursor.rowcount>0): 
        registro = cursor.fetchone()
        #print(registro["Nombre"],registro["Apellidos"],registro["Correo"],registro["Telefono"],registro["Direccion_ppal"],username)

        usuarioValidado["Nombre"] = registro["Nombre"]
        usuarioValidado["Apellidos"] = registro["Apellidos"]
        usuarioValidado["Direccion"] = registro["Direccion_ppal"]
        usuarioValidado["Correo"] = registro["Correo"]
        usuarioValidado["Telefono"] = registro["Telefono"]
        usuarioValidado["Usuario"] = username

        #Le añado a la lista de conectados
        usuariosConectados.crea(username)

        #resp = redirect("static/recargaPagina.html", code=302)
        resp = redirect("/", code=302)
        resp.set_cookie("userID",username)
        return resp

    #Si la password no coincide
    else:
        usuarioValidado["Nombre"] = ""
        usuarioValidado["Apellidos"] = ""
        usuarioValidado["Direccion"] = 0
        usuarioValidado["Correo"] = ""
        usuarioValidado["Telefono"] = ""
        usuarioValidado["Usuario"] = ""
        
        respuesta = make_response(render_template('mensaje.html', MENSAJE = "El usuario o la password son incorrectos.", SECUNDARIO = "Todo KO"),200)
        respuesta.set_cookie("userID","")
        return respuesta

@app.route('/cerrarSesion')
def cerrarSesion():
    #Lo elimino de la lista
    print('Se cerrara la sesion de ' + usuarioValidado["Usuario"])
    usuariosConectados.borra(usuarioValidado["Usuario"])

    usuarioValidado["Nombre"] = ""
    usuarioValidado["Apellidos"] = ""
    usuarioValidado["Direccion"] = 0
    usuarioValidado["Correo"] = ""
    usuarioValidado["Telefono"] = ""
    usuarioValidado["Usuario"] = ""

    resp = redirect('static/recargaPagina.html', code=302)
    resp.set_cookie("userID","")
    return resp

@app.route('/editaDatosUsuario/<string:usuario>')
def editaUsuario(usuario):
    username = request.cookies.get('userID')
    if not username:
        #username=""
        print('Salgo por aqui')
        #return make_response('',405)
        return redirect("/", code=302)
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            username=""
            #return make_response('',405)
            return redirect("/", code=302)

    if(usuario!=username):
        #return make_response('',405)
        return redirect("/", code=302)

    usuarioValidado = dameUsuario(usuario)

    #return render_template('/editaDatosUsuario.html',NOMBRE=usuarioValidado['Nombre'], APELLIDOS=usuarioValidado['Apellidos'], CORREO=usuarioValidado['Correo'], TELEFONO=usuarioValidado['Telefono'], DIRECCION=usuarioValidado['Direccion'], USUARIO=usuarioValidado['Usuario'])
    delante = render_template('/div_editaDatosUsuario.html',NOMBRE=usuarioValidado['Nombre'], APELLIDOS=usuarioValidado['Apellidos'], CORREO=usuarioValidado['Correo'], TELEFONO=usuarioValidado['Telefono'], DIRECCION=usuarioValidado['Direccion'], USUARIO=usuarioValidado['Usuario'])
    detras = ""
    return render_template('inicio.html', DELANTE=delante, DETRAS=detras,NOMBRE_PRINCIPIO=nombrePrincipio, NOMBRE_ROJO=nombreRojo, NOMBRE_FINAL=nombreFinal, PRINCIPIO=principio, ROJO=rojo, FINAL=final, PIE=pie, USUARIO=usuario)  

@app.route('/nuevoUsuario')
def nuevoUsuario():
    usuario=""
    fichero = open('static/div_nuevoUsuario.html')
    delante = fichero.read()
    detras = ""
    return render_template('inicio.html', DELANTE=delante, DETRAS=detras,NOMBRE_PRINCIPIO=nombrePrincipio, NOMBRE_ROJO=nombreRojo, NOMBRE_FINAL=nombreFinal, PRINCIPIO=principio, ROJO=rojo, FINAL=final, PIE=pie, USUARIO=usuario)  

@app.route('/creaUsuario')
def crearUsuario():
    nombre = str(request.args.get('nombre'))
    apellidos = str(request.args.get('apellidos'))
    correo = str(request.args.get('correo'))
    telefono = str(request.args.get('telefono'))
    direccion = str(request.args.get('direccion'))
    username = str(request.args.get('username'))
    password_txt = str(request.args.get('password'))
    password = md5(password_txt.encode("utf-8")).hexdigest()

    print("nombre: " + nombre + " " + apellidos)
    print("direccion: " + direccion)
    print("telefono: " + telefono)
    print("correo: " + correo)
    print("usuario: " + username + " password: " + password)
 
    #compruebo que no haya campos vacios
    if(nombre=="" or apellidos=="" or correo=="" or telefono=="" or direccion=="" or username=="" or password_txt==""):
        return render_template('mensaje.html', MENSAJE = "Error al crear usuario. Faltan datos requeridos", SECUNDARIO = "Todo KO")

    #compruebo que no haya usuario repetido
    sql = "select Usuario from Usuarios where usuario='" + username + "'"
    print ("Consulta: " + sql)

    cursor.execute(sql)
    if(cursor.rowcount>0):
        return render_template('mensaje.html', MENSAJE = "Error al crear usuario. El usuario [" + username + "]ya existe", SECUNDARIO = "Todo KO")

    #creo el nuevo usuario
    sql = "insert into Usuarios (Nombre, Apellidos, Correo, Telefono, Direccion_ppal, Usuario, Password) values ('" + nombre + "','" + apellidos + "','" + correo + "','" + telefono + "','" + direccion + "','" + username + "','" + password +"')"
    print ("Consulta: " + sql)  

    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e: 
        print(e)  
        db.rollback()
        print("Error en la consulta")
        return render_template('mensaje.html', MENSAJE = "Error al crear usuario.", SECUNDARIO = "Todo KO")

    #Le añado a la lista de conectados
    usuariosConectados.crea(username)

    #resp = redirect("static/recargaPagina.html", code=302)
    resp = redirect("/", code=302)
    resp.set_cookie("userID",username)
    return resp

@app.route('/actualizaUsuario/<string:usuario>')
def actualizaUsuario(usuario):
    username = request.cookies.get('userID')
    if not username:
        return redirect('/',302) #return make_response('',405)
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            username=""
            return redirect ('/',302) #make_response('',405)

    if(usuario!=username):
        return redirect ('/',302) #make_response('',405)

    nombre = str(request.args.get('nombre'))
    apellidos = str(request.args.get('apellidos'))
    correo = str(request.args.get('correo'))
    telefono = str(request.args.get('telefono'))
    direccion = str(request.args.get('direccion'))

    print("nombre: " + nombre + " " + apellidos)
    print("direccion: " + direccion)
    print("telefono: " + telefono)
    print("correo: " + correo)
    
    sql = "update Usuarios set Nombre='" + nombre + "', Apellidos='" + apellidos + "', Correo='" + correo + "', Telefono='" + telefono + "' where Usuario='" + usuario + "'"
    print ("Consulta: " + sql)
    
    try:
        cursor.execute(sql)
        db.commit()

    except Exception as e: 
        print(e)  
        db.rollback()
        print("Error en la consulta")
        return render_template('mensaje.html', MENSAJE = "Error al crear usuario.", SECUNDARIO = "Todo KO")

    usuarioValidado = dameUsuario(usuario)

    resp = redirect('/datosUsuario', code=302)
    resp.set_cookie("userID",usuarioValidado['Usuario'])
    return resp
#************************************************* GUI usuario *************************************************************

#************************************************* API *************************************************************
@app.route('/test', methods = ['POST','GET'])
def test():
    return "OK"

@app.route('/configuracion/<string:usuario>/<string:nombreDevice>/<string:servicio>', methods = ['POST','GET'])
def configuracion(usuario,nombreDevice,servicio):
    print("Entrando en configuracion...")
    #compruebo la contrasena
    if(validaContrasena(usuario,dameDeviceID(nombreDevice,usuario),request.args.get('address'))!=200):
        return make_response('address incorrecta',401)

    #Aseguro que esta validado antes de guardar o enviar config
    if dameDeviceValidado(dameDeviceID(nombreDevice,usuario))!=DISPOSITIVO_VALIDADO:
        print('El dispositivo no esta validado')
        return make_response(('Dispositivo no validado',402))

    if request.method == 'POST': 
        nombreFichero = dirUsuarios + usuario + '/'
        if not os.path.exists(nombreFichero):
            os.mkdir(nombreFichero)
        nombreFichero += nombreDevice + '/'
        if not os.path.exists(nombreFichero):
            os.mkdir(nombreFichero)

        #print('Directorio de configuracion del dispositivo: ' + nombreFichero)
        if not os.path.exists(nombreFichero): return make_response(('Dir not found',404))

        nombreFichero += str(servicio + '.json')

        print('se guardara en ' + nombreFichero)
        """
        print('conenido: -->')
        print(request.data)
        print('<--')
        """
        cad = request.data #request.get_json(True)
        print('conenido decoded: -->' + cad.decode('utf-8') + '<--')

        with open(nombreFichero, 'w') as f:
            f.write(cad.decode('utf-8'))
        
        return make_response('Fichero de configuracion guardado',200)

    if request.method == 'GET': 
        nombreFichero = dirUsuarios + usuario + '/' + nombreDevice + '/' + str(servicio + '.json')
        print('se leera de ' + nombreFichero)
        if not os.path.exists(nombreFichero): return make_response(('File not found',404))

        with open(nombreFichero, 'r') as f:
            cad = f.read()
            print(cad)
        
        #return make_response(cad,200)
        return Response(response=cad, status=200, mimetype="application/json")

@app.route('/asocia/<string:usuario>/<string:deviceID>', methods = ['POST','GET'])
def asocia(usuario,deviceID):    
    #Compruebo los datos de entrada
    #compruebo el ID
    if len(deviceID)!=16: #64 bits en hexa son 16 aracteres
        print('deviceID [' + deviceID + '] no valido') 
        return make_response('deviceID no valido',404)
    
    #compruebo el usuario
    sql = "select Usuario from Usuarios where Usuario='" + usuario + "'"
    print ("Consulta: " + sql)
    cursor.execute(sql)
    if(cursor.rowcount<=0):
        return make_response('Usuario no valido',404)

    #Segun el metodo de invocacion
    #POST
    if request.method == 'POST': 
        #Compruebo el nombreServicio
        nombreServicio=request.args.get('nombreServicio')    
        if not nombreServicio:
            return make_response('Nombre no valido',404)

        #Compruebo si el dispositivo ya existe
        sql = "select * from Dispositivos where DID='" + deviceID + "'"
        print ("Consulta: " + sql)
        try:
            cursor.execute(sql)
            if(cursor.rowcount<=0):
                #Si no existe, lo creo
                print('No existe el deviceID, lo creo')
                contrasena_txt = usuario + deviceID
                print("Contrasena txt: " + contrasena_txt)
                contrasena = md5(contrasena_txt.encode("utf-8")).hexdigest()

                sql = "insert into Dispositivos (DID,SID,CID,Contrasena) values ('" + deviceID + "','" + nombreServicio + "','" + usuario + "','" + contrasena + "')"
                print ("Consulta: " + sql)
                cursor.execute(sql)
                db.commit()
                return make_response('Dispositivo asignado', 200)

            else: #Ya exite una relacion
                registro = cursor.fetchone()
                return make_response('El dispositivo ya existe, asignado a ' + registro["CID"] ,405)
                
        except Exception as e: 
            print(e)  
            return make_response('Error SQL',500)

    #GET
    elif request.method == 'GET': 
        try:
            #compruebo la contrasena
            if(validaContrasena(usuario,deviceID,request.args.get('address'))!=200):
                return make_response('address incorrecta',405)

            #Compruebo si el dispositivo ya existe
            sql = "select * from Dispositivos where Validado=1 and DID='" + deviceID + "'"
            print ("Consulta: " + sql)
            cursor.execute(sql)
            if(cursor.rowcount<=0):
                #Si no existe, retorna error
                print('No existe el deviceID')
                return make_response('No existe el dispositivo',404)

            elif(cursor.rowcount>1): #Dispositivo tiene mas de una relacion!!!!!
                return make_response('El dispositivo esta duplicado',500)

            else:
                registro = cursor.fetchone()
                if(registro["Usuario"]==usuario):
                    #return make_response('{"ID": "' + deviceID + '", "usuario": "' + registro["Usuario"] + '"}',200)
                    return Response(response='{"ID": "' + deviceID + '", "nombre": "' + registro["Nombre"] + '", "usuario": "' + registro["Usuario"] + '"}', status=200, mimetype="application/json")
                else:
                    return make_response('El dispositivo no esta asignado a este usuario',405)

        except Exception as e: 
            print(e)            
            return make_response('Error SQL',500)  

@app.route('/dispositivos/<string:usuario>', methods = ['POST','GET','DELETE'])
def dispositivosUsuario(usuario):
    dispositivios=()

    username = request.cookies.get('userID')
    print('usuario de la cookie: ' + username)
    print('usuario recbido: ' + usuario)

    if not username:
        #username=""
        print('Salgo por aqui')
        return make_response('',401)
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            username=""
            return make_response('',402)

    if(usuario!=username):
        return make_response('motivo: ' + usuario + '!=' + username,405)

    sql='select SID,DID,validado from Dispositivos where CID="' + usuario + '" order by SID'
    print ("Consulta: " + sql)
    try:
        cursor.execute(sql)
        if(cursor.rowcount>0):
            dispositivios = cursor.fetchall()
            print(dispositivios)

    except Exception as e: 
        print(e)  
        return make_response('Error SQL',500)

    resp = make_response(render_template('/dispositivos.html',DISPOSITIVOS=dispositivios, USUARIO=usuario),200)
    return resp

@app.route('/dispositivo/<string:DID>', methods = ['POST','GET','DELETE'])
def dispositivo(DID):
    print('Entrando en dispositivo')
    usuario = dameUsuarioDispositivo(DID)

    if usuario=='':
        pass #Vamos a / sin cookie

    if validaSesion(usuario)!=OK:
        return redirect('/',302)

    if request.method=='POST':
        print('Ha llegado a POST')
        validaDeviceID(DID)
        resp = make_response("validado",200)

    elif request.method == 'GET':
        print('Ha llegado a GET')
        accion = str(request.args.get('accion'))
        print("Accion: " + accion)

        if(accion=="datos"):
            resp = make_response(render_template('/dispositivoDatos.html',USUARIO=usuario,SID=dameNombreDispositivo(DID)),200)
        elif(accion=="configuracion"):
            resp = make_response(render_template('/dispositivoConfiguracion.html',USUARIO=usuario,SID=dameNombreDispositivo(DID)),200)
        else:
            resp = make_response("",400)
        
        #return resp
    elif request.method == 'DELETE':
        print('Ha llegado a DELETE')
        borraDeviceID(DID)
        resp = make_response("Borrado",200)

    return resp

@app.route('/lista')
def lista():
    return usuariosConectados.lista()

@app.route('/ficheroConfiguracion/<string:usuario>/<string:nombreDevice>/<string:servicio>', methods = ['POST','GET'])
def ficheroConfiguracion(usuario,nombreDevice,servicio):
    print("Entrando en ficheroConfiguracion (" + usuario + "|" + nombreDevice + "|" +  servicio + ")...")
    #compruebo la sesion
    if(validaSesion(usuario)==KO):
        return redirect('/',302) #Esto deberia enviarse al navegador
        return make_response('No tiene sesion',401) #esto a un API

    #Aseguro que esta validado antes de guardar o enviar config
    if dameDeviceValidado(dameDeviceID(nombreDevice,usuario))!=DISPOSITIVO_VALIDADO:
        print('El dispositivo no esta validado')
        return make_response(('Dispositivo no validado',402))

    if request.method == 'POST': 
        nombreFichero = dirUsuarios + usuario + '/'
        if not os.path.exists(nombreFichero):
            os.mkdir(nombreFichero)
        nombreFichero += nombreDevice + '/'
        if not os.path.exists(nombreFichero):
            os.mkdir(nombreFichero)

        #print('Directorio de configuracion del dispositivo: ' + nombreFichero)
        if not os.path.exists(nombreFichero): return make_response(('Dir not found',404))

        nombreFichero += str(servicio + '.json')

        print('se guardara en ' + nombreFichero)

        cad = request.get_json(True,True,True)
        if(cad==None): resp = make_response('json no valido',400)
        else:
            #print(request.get_json(True))
            cad=request.data
            with open(nombreFichero, 'w') as f:
                f.write(cad.decode('utf-8'))
            
            resp = make_response('Fichero de configuracion guardado',200)
        return resp

    if request.method == 'GET': 
        #valido que tiene permiso
        nombreFichero = dirUsuarios + usuario + '/' + nombreDevice + '/' + servicio + '.json'
        print('se leera de ' + nombreFichero)
        if not os.path.exists(nombreFichero): return make_response(('File not found',404))

        with open(nombreFichero, 'r') as f:
            cad = f.read()
            print(cad)
    
    return make_response(cad,200)

@app.route('/recuperaDatos/<string:usuario>/<string:nombreDevice>/<string:SSID>')
def recuperaDatos(usuario,nombreDevice,SSID):
    print("Entrando en recuperaDatos...")
    #compruebo la sesion
    if(validaSesion(usuario)!=OK):
        return redirect('/',302) #Bueno para navegador
        return make_response('No tiene sesion',405) #esto deberia mandarse a un API

    #Aseguro que esta validado antes de guardar o enviar config
    if dameDeviceValidado(dameDeviceID(nombreDevice,usuario))!=DISPOSITIVO_VALIDADO:
        print('El dispositivo no esta validado')
        return make_response(('Dispositivo no validado',405))

    #Recupero el valor de la base de datos
    sql='select Dato from Datos where CID="' + usuario + '" and SID="' + nombreDevice + '" and SSID="' + SSID + '"'
    cursor.execute(sql)
    if(cursor.rowcount==0): return make_response(('Sin datos',404))
    
    datos=cursor.fetchone()
    registros=json.loads(datos["Dato"])
    print(len(registros["datos"]))


    #elijo el template
    template='/' + SSID + '.html'

    return render_template(template,REGISTROS=registros["datos"])

@app.route('/descargaConfig/<string:usuario>/<string:SID>/<string:SSID>', methods=['POST'])
def descargaConfig(usuario,SID,SSID):
    msg = {
 	"tipo":"configura",
	"subtipo":"fichero",
	"orden":"download",
    "id": 0,
	"valor": SSID
    }

    topic = pubTopicRoot + '/' + usuario + '/' + SID + '/buzon'
    publish_result = mqtt_client.publish(topic, json.dumps(msg))
    print(publish_result)

    return make_response("Codigo de retorno:" + str(publish_result[0]), 200)
#************************************************* API *************************************************************
    
#*************************************************Funciones**********************************************************************
def dameUsuario(username):
    sql = "select Nombre, Apellidos, Correo, Telefono, Direccion_ppal from Usuarios where Usuario = '" + username + "'"
    print ("Consulta: " + sql)

    try:
        cursor.execute(sql)
    except Exception as e: 
        print(e)  
        print("Error en la consulta")       

    #Si he encontrado el usaurio
    if (cursor.rowcount>0): 
        registro = cursor.fetchone()
        print(registro["Nombre"],registro["Apellidos"],registro["Correo"],registro["Telefono"],registro["Direccion_ppal"],username)

        usuarioValidado["Nombre"] = registro["Nombre"]
        usuarioValidado["Apellidos"] = registro["Apellidos"]
        usuarioValidado["Direccion"] = registro["Direccion_ppal"]
        usuarioValidado["Correo"] = registro["Correo"]
        usuarioValidado["Telefono"] = registro["Telefono"]
        usuarioValidado["Usuario"] = username
    else:
        usuarioValidado["Nombre"] = ""
        usuarioValidado["Apellidos"] = ""
        usuarioValidado["Direccion"] = 0
        usuarioValidado["Correo"] = ""
        usuarioValidado["Telefono"] = ""
        usuarioValidado["Usuario"] = ""

    return usuarioValidado
    
def validaContrasena(_usuario, _deviceID, _contrasena_in):
    sql="select Contrasena from Dispositivos where CID='" + _usuario + "' and DID='" + _deviceID + "'"
    cursor.execute(sql)
    if(cursor.rowcount<=0):
        #Si no existe, retorna error
        print('No existe el dispositivo')
        return 404
    else:
        print("hay un dispositivo, comparo las contrasenas")
        registro=cursor.fetchone()
        if(_contrasena_in!=registro['Contrasena']):
            #La contrasena recibida no es correcta
            print('Contrasena incorrecta')
            return 405
    
    return 200

def validaSesion(usuario):
    username = request.cookies.get('userID')
    if not username:
        print('No hay usuario en la cookie')
        return KO
    elif(usuario!=username):
        print("El usuario pasado no es el de la cookie")
        return KO
    elif(usuariosConectados.renueva(usuario,timeOutSesion)==False):
        print("Seion espirada")
        return KO

    return OK    

def dameNombreDispositivo(deviceID):
    sql='select SID from Dispositivos where DID="' + deviceID +'"'
    try:
        cursor.execute(sql)
        if(cursor.rowcount>0):
            registro=cursor.fetchone()
            return registro['SID']
        else:
            return ''
    except Exception as e: 
        print(e)            
        return '' 

def dameUsuarioDispositivo(deviceID):
    sql='select CID from Dispositivos where DID="' + deviceID +'"'
    try:
        cursor.execute(sql)
        if(cursor.rowcount>0):
            registro=cursor.fetchone()
            return registro['CID']
        else:
            return ''
    except Exception as e: 
        print(e)            
        return ''#make_response('Error SQL',500)

def dameDeviceID(nombre,usuario):
    sql='select DID from Dispositivos where CID="' + usuario + '" and SID="' + nombre +'"'
    try:
        cursor.execute(sql)
        if(cursor.rowcount>0):
            registro=cursor.fetchone()
            return registro['DID']
        else:
            return ''
    except Exception as e: 
        print(e)            
        return ''#make_response('Error SQL',500)  

def dameDeviceValidado(ID):
    sql='select Validado from Dispositivos where DID="' + ID +'"'
    try:
        cursor.execute(sql)
        if(cursor.rowcount>0):
            registro=cursor.fetchone()
            return registro['Validado']
        else:
            return ''
    except Exception as e: 
        print(e)            
        return ''#make_response('Error SQL',500)  

def borraDeviceID(ID):
    sql='delete from Dispositivos where DID="' + ID +'"'
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
        return True

    except Exception as e: 
        print(e)            
        return False

def validaDeviceID(DID):
    sql='update Dispositivos set Validado=1 where DID="' + DID +'"'
    print(sql)
    try:
        cursor.execute(sql)
        db.commit()
        return True

    except Exception as e: 
        print(e)            
        return False        

#***************MQTT*************
@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(topic) # subscribe topic
   else:
       print('Bad connection. Code:', rc)

@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
   data = dict(
       topic=message.topic,
       payload=message.payload.decode()
  )
   print('Received message on topic: {topic} with payload: {payload}'.format(**data))

#*************************************************Funciones**********************************************************************

#*************************************************MAIN**********************************************************************
if __name__ == "__main__":
    with open(configFile) as json_file:
        usuarioValidado["Nombre"] = ""
        usuarioValidado["Apellidos"] = ""
        usuarioValidado["Direccion"] = 0
        usuarioValidado["Correo"] = ""
        usuarioValidado["Telefono"] = ""
        usuarioValidado["Usuario"] = ""

        configuracion = json.load(json_file)

        #Config de proceso        
        proceso =configuracion["Proceso"] 
        puerto = proceso["puerto"]
        IP = proceso["IP"]

        #ficheros
        ficheros = configuracion['Ficheros']
        dirUsuarios = str(ficheros['usuarios'])
        if not dirUsuarios.endswith('/'): dirUsuarios += '/'

        #config de BBDD
        if "DB" in configuracion: 
            dbConfig = configuracion["DB"]
            if "dbIP" in dbConfig: dbIP = dbConfig["dbIP"]
            if "dbPuerto" in dbConfig: dbPuerto = dbConfig["dbPuerto"]
            if "dbUsuario" in dbConfig: dbUsuario = dbConfig["dbUsuario"]
            if "dbPassword" in dbConfig: dbPassword = dbConfig["dbPassword"]
            if "dbNombre" in dbConfig: dbNombre  = dbConfig["dbNombre"]

        try:
            db = MySQLdb.connect(dbIP,dbUsuario,dbPassword,dbNombre)
            db.autocommit(True)
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            print('Conectado a la base de datos ' + dbNombre)
        except MySQLdb.Error as e:
            print("No puedo conectar a la base de datos:",e)
            sys.exit(1)


        #config de MQTT
        MQTT = configuracion["MQTT"]
        if "broker" in MQTT: app.config['MQTT_BROKER_URL'] = MQTT["broker"]
        else: broker=""
        if "puerto" in MQTT: app.config['MQTT_BROKER_PORT'] = MQTT["puerto"]
        else: puerto=""
        if "usuario" in MQTT: app.config['MQTT_USERNAME'] = MQTT["usuario"]
        else: MQTTusuario=""
        if "password" in MQTT: app.config['MQTT_PASSWORD'] = MQTT["password"]
        else: MQTTpass=""
        if "pubTopic" in MQTT: pubTopicRoot = MQTT["pubTopic"]
        else: pubTopicRoot=""
        if "subTopic" in MQTT: subTopicRoot = MQTT["subTopic"]
        else: subTopicRoot=""

        app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
        app.config['MQTT_TLS_ENABLED'] = False  # If your server supports TLS, set it True
        # Parameters for SSL enabled
        # app.config['MQTT_BROKER_PORT'] = 8883
        # app.config['MQTT_TLS_ENABLED'] = True
        # app.config['MQTT_TLS_INSECURE'] = True
        # app.config['MQTT_TLS_CA_CERTS'] = 'ca.crt'
        
        print("Configuracion MQTT\nbroker: [" + str(app.config['MQTT_BROKER_URL']) + "]\npuerto: [" + str(app.config['MQTT_BROKER_PORT']) + "]\nusuario: [" + str(app.config['MQTT_USERNAME']) + "]\npass: [" + str(app.config['MQTT_PASSWORD']) + "]\npub topic root: [" + str(pubTopicRoot) + "]\nsub topic root: [" + str(subTopicRoot) + "]")

        mqtt_client = Mqtt(app)

        #Config de presentacion
        raiz=configuracion["Raiz"]
        nombre=raiz["nombre"]
        cabecera = raiz["cabecera"]
        pie = raiz["pie"]
        
        #print('cabecera: ' + cabecera + ' longitud=' + str(len(cabecera)),sys.stderr)
        #print('pie: ' + pie,sys.stderr)

        #nombre
        i=0
        nombrePrincipio=""
        while i<(len(nombre)-3):
            nombrePrincipio += nombre[i]
            i = i + 1

        #print('Nombre principio: ' + nombrePrincipio,sys.stderr)

        nombreRojo=nombre[len(nombre)-3]
        #print('rojo: ' + nombreRojo,sys.stderr)
        nombreFinal=nombre[len(nombre)-2]+nombre[len(nombre)-1]
        #print('final: ' + nombreFinal,sys.stderr)

        #cabecera
        i=0
        principio=""
        while i<(len(cabecera)-3):
            principio += cabecera[i]
            i = i + 1

        rojo=cabecera[len(cabecera)-3]
        #print('rojo: ' + rojo,sys.stderr)
        final=cabecera[len(cabecera)-2]+cabecera[len(cabecera)-1]
        #print('final: ' + final,sys.stderr)

        #config conectados
        usuariosConectados=conectados.Conectados()

        #Arranco el app
        app.run(host=IP, port=puerto)
#*************************************************MAIN**********************************************************************
