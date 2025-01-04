from flask import Flask, render_template, request, Response, redirect, send_file, url_for, make_response
from hashlib import md5
from werkzeug.utils import secure_filename
from markupsafe import escape
from flask_mqtt import Mqtt # Solo se usa para enviar. pendiente utilizar para recibir.https://flask-mqtt.readthedocs.io/en/latest/usage.html
from html import unescape

import requests as outputRequests
import datetime
import time
import json
import sys
import os

#import MySQLdb
from db_connection import DBConnection

import logging
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
def raiz():
    pagina = 'div_login.html'
    
    usuario = request.cookies.get('userID')
    if not usuario:
        usuario=""
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            usuario=""            
        else:
            pagina = 'div_main.html'        

    delante = render_template(pagina, USUARIO=usuario)
    detras = ""
    return render_template('inicio.html', DELANTE=delante, DETRAS=detras,NOMBRE_PRINCIPIO=nombrePrincipio, NOMBRE_ROJO=nombreRojo, NOMBRE_FINAL=nombreFinal, PRINCIPIO=principio, ROJO=rojo, FINAL=final, PIE=pie, USUARIO=usuario)

    #************************************************* usuario *************************************************************
@app.route('/datosUsuario')
def datosUsuario():
    usuario = request.cookies.get('userID')
    if not usuario:
        logger.info("---------------->Sin cookie")
        return redirect('/',302)
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            logger.info("---------------->No se puede renovar")
            return redirect('/',302)

    usuarioValidado = dameUsuario(usuario)


    delante = render_template('div_datosUsuario.html',NOMBRE=usuarioValidado['Nombre'], APELLIDOS=usuarioValidado['Apellidos'], CORREO=usuarioValidado['Correo'], TELEFONO=usuarioValidado['Telefono'], DIRECCION=usuarioValidado['Direccion'], USUARIO=usuarioValidado['Usuario'])
    detras = ""
    return render_template('inicio.html', DELANTE=delante, DETRAS=detras,NOMBRE_PRINCIPIO=nombrePrincipio, NOMBRE_ROJO=nombreRojo, NOMBRE_FINAL=nombreFinal, PRINCIPIO=principio, ROJO=rojo, FINAL=final, PIE=pie, USUARIO=usuario)

@app.route('/debug')
def debug():
    return usuarioValidado

@app.route('/debug2')
def debug2():
    return "IP: " + str(IP) + ", puerto: " + str(puerto) + ", bd IP: " + str(dbIP) + ", puerto bd: " + str(dbPuerto) + ", nombre bd: " + str(dbUsuario) + ", password bd: " + str(dbPassword) + ", nombre bd: " + str(dbNombre)

@app.route('/debug3')
def debug3():
    return request.cookies.get('userID')

@app.route('/reconnect')
def reconect():
    db.check_connection()
    return redirect("/",302)
    '''
    logger.info("Reconectando...")
    try:
        db = MySQLdb.connect(dbIP,dbUsuario,dbPassword,dbNombre, charset='utf8')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        logger.info('Reconectado a la base de datos ' + dbNombre)
        return redirect("/",302)
    except MySQLdb.Error as e:
        logger.info("No puedo conectar a la base de datos:",e)
        sys.exit(1)
    '''
    
@app.route('/validaUsuario')
def validarUsuario():
    result = 0
    username = str(request.args.get('username'))
    password_txt = str(request.args.get('password'))
    password = md5(password_txt.encode("utf-8")).hexdigest()

    #logger.info("usuario: " + username + " password txt: " + password_txt + " password: " + password)
    logger.info(f"usuario: {username}  password: {password}")

    sql = "select Nombre, Apellidos, Correo, Telefono, Direccion_ppal from Usuarios where Usuario = '" + username + "' and Password='" + password + "'"
    logger.info("Consulta: " + sql)
    
    try:
        cursor = db.execute(sql)
      
        #Si he encontrado el usaurio
        if (cursor.rowcount>0): 
            registro = cursor.fetchone()
            #logger.info(registro["Nombre"],registro["Apellidos"],registro["Correo"],registro["Telefono"],registro["Direccion_ppal"],username)

            usuarioValidado["Nombre"] = registro["Nombre"]
            usuarioValidado["Apellidos"] = registro["Apellidos"]
            usuarioValidado["Direccion"] = registro["Direccion_ppal"]
            usuarioValidado["Correo"] = registro["Correo"]
            usuarioValidado["Telefono"] = registro["Telefono"]
            usuarioValidado["Usuario"] = username

            #Le añado a la lista de conectados
            usuariosConectados.crea(username)

            #respuesta = redirect("static/recargaPagina.html", code=302)
            respuesta = redirect("/", code=302)
            respuesta.set_cookie("userID",username)
            return respuesta

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

    except Exception as e: 
        logger.info(e)  
        logger.info("Error en la consulta") 
        return "Error en BD"
        
@app.route('/cerrarSesion')
def cerrarSesion():
    #Lo elimino de la lista
    logger.info('Se cerrara la sesion de ' + usuarioValidado["Usuario"])
    usuariosConectados.borra(usuarioValidado["Usuario"])

    usuarioValidado["Nombre"] = ""
    usuarioValidado["Apellidos"] = ""
    usuarioValidado["Direccion"] = 0
    usuarioValidado["Correo"] = ""
    usuarioValidado["Telefono"] = ""
    usuarioValidado["Usuario"] = ""

    resp = redirect('/', code=302)
    resp = redirect('/', code=302)
    resp.set_cookie("userID","")
    return resp

@app.route('/editaDatosUsuario/<string:usuario>')
def editaUsuario(usuario):
    username = request.cookies.get('userID')
    if not username:
        #username=""
        logger.info('Salgo por aqui')
        return redirect("/", code=302)
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            username=""
            return redirect("/", code=302)

    if(usuario!=username):
        #return make_response('',405)
        return redirect("/", code=302)

    usuarioValidado = dameUsuario(usuario)

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
    username = str(request.args.get('usuario'))
    username = str(request.args.get('usuario'))
    password_txt = str(request.args.get('password'))
    password = md5(password_txt.encode("utf-8")).hexdigest()

    logger.info("nombre: " + nombre + " " + apellidos)
    logger.info("direccion: " + direccion)
    logger.info("telefono: " + telefono)
    logger.info("correo: " + correo)
    logger.info("usuario: " + username + " password: " + password)
 
    #compruebo que no haya campos vacios
    if(nombre=="" or apellidos=="" or correo=="" or telefono=="" or direccion=="" or username=="" or password_txt==""):
        return render_template('mensaje.html', MENSAJE = "Error al crear usuario. Faltan datos requeridos", SECUNDARIO = "Todo KO")

    #compruebo que no haya usuario repetido
    sql = "select Usuario from Usuarios where usuario='" + username + "'"
    logger.info("Consulta: " + sql)

    try:
        cursor = db.execute(sql)
        if(cursor.rowcount>0):
            return render_template('mensaje.html', MENSAJE = "Error al crear usuario. El usuario [" + username + "]ya existe", SECUNDARIO = "Todo KO")

        #creo el nuevo usuario
        sql = "insert into Usuarios (Nombre, Apellidos, Correo, Telefono, Direccion_ppal, Usuario, Password) values ('" + nombre + "','" + apellidos + "','" + correo + "','" + telefono + "','" + direccion + "','" + username + "','" + password +"')"
        logger.info("Consulta: " + sql)  

        cursor = db.execute(sql)
        db.commit()

        #Le añado a la lista de conectados
        usuariosConectados.crea(username)

        resp = redirect("/", code=302)
        resp.set_cookie("userID",username)
        return resp
    
    except Exception as e: 
        logger.info(e)  
        db.rollback()
        logger.info("Error en la consulta")
        return render_template('mensaje.html', MENSAJE = "Error al crear usuario.", SECUNDARIO = "Todo KO")


@app.route('/actualizaUsuario/<string:usuario>')
def actualizaUsuario(usuario):
    username = request.cookies.get('userID')
    if not username:
        return redirect('/',302) 
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            username=""
            return redirect ('/',302)

    if(usuario!=username):
        return redirect ('/',302)

    nombre = str(request.args.get('nombre'))
    apellidos = str(request.args.get('apellidos'))
    correo = str(request.args.get('correo'))
    telefono = str(request.args.get('telefono'))
    direccion = str(request.args.get('direccion'))

    logger.info("nombre: " + nombre + " " + apellidos)
    logger.info("direccion: " + direccion)
    logger.info("telefono: " + telefono)
    logger.info("correo: " + correo)
    
    sql = "update Usuarios set Nombre='" + nombre + "', Apellidos='" + apellidos + "', Correo='" + correo + "', Telefono='" + telefono + "' where Usuario='" + usuario + "'"
    logger.info("Consulta: " + sql)
    
    try:
        cursor = db.execute(sql)
        db.commit()

        usuarioValidado = dameUsuario(usuario)

        resp = redirect('/datosUsuario', code=302)
        resp.set_cookie("userID",usuarioValidado['Usuario'])
        return resp

    except Exception as e: 
        logger.info(e)  
        db.rollback()
        logger.info("Error en la consulta")
        return render_template('mensaje.html', MENSAJE = "Error al crear usuario.", SECUNDARIO = "Todo KO")

@app.route('/resetPassword/<string:usuario>')
def resetPassword(usuario):
    username = request.cookies.get('userID')
    if not username:
        logger.info("Not username")
        return redirect('/',302) 
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            logger.info("Not connected")
            username=""
            return redirect ('/',302)

    if(usuario!=username):
        logger.info("Username not match")
        return redirect ('/',302)

    password_txt = str(request.args.get('password_txt'))
    password = md5(password_txt.encode("utf-8")).hexdigest()    

    logger.info("password: " + password)
    
    sql = "update Usuarios set Password='" + password + "' where Usuario='" + usuario + "'"
    logger.info("Consulta: " + sql)
    
    try:
        cursor = db.execute(sql)
        db.commit()

        usuarioValidado = dameUsuario(usuario)

        resp = redirect('/datosUsuario', code=302)
        resp.set_cookie("userID",usuarioValidado['Usuario'])
        return resp

    except Exception as e: 
        logger.info(e)  
        db.rollback()
        logger.info("Error en la consulta")
        return render_template('mensaje.html', MENSAJE = "Error al resetear contraseña.", SECUNDARIO = "Todo KO")

    #************************************************* fin usuario *************************************************************
    #*************************************************
    #*************************************************
    #************************************************* 
    #*************************************************
    #*************************************************
    #************************************************* 
    #************************************************* dispositivos ********************************************************
@app.route('/dispositivos/<string:usuario>', methods = ['POST','GET','DELETE'])
def dispositivosUsuario(usuario):
    dispositivios=()

    username = request.cookies.get('userID')
    logger.info('usuario de la cookie: ' + username)
    logger.info('usuario recbido: ' + usuario)

    if not username:
        #username=""
        logger.info('Salgo por aqui')
        return redirect("/", code=302)
        return redirect("/", code=302)
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            username=""
            return redirect("/", code=302)
            return redirect("/", code=302)

    if(usuario!=username):
        return redirect("/", code=302)
        return redirect("/", code=302)

    sql='select SID,DID,validado,version from Dispositivos where CID="' + usuario + '" order by SID'
    logger.info("Consulta: " + sql)
    try:
        cursor = db.execute(sql)
        if(cursor.rowcount>0):
            dispositivios = cursor.fetchall()
            logger.info(dispositivios)

        delante = render_template('/div_dispositivos.html',DISPOSITIVOS=dispositivios, USUARIO=usuario)
        detras = ""
        return render_template('inicio.html', DELANTE=delante, DETRAS=detras,NOMBRE_PRINCIPIO=nombrePrincipio, NOMBRE_ROJO=nombreRojo, NOMBRE_FINAL=nombreFinal, PRINCIPIO=principio, ROJO=rojo, FINAL=final, PIE=pie, USUARIO=usuario)  

    except Exception as e: 
        logger.info(e)  
        return make_response('Error SQL',500)


@app.route('/dispositivo/<string:DID>', methods = ['POST','GET','DELETE'])
def dispositivo(DID):
    logger.info('Entrando en dispositivo')
    delante=''
    detras=''
    
    usuario = dameUsuarioDispositivo(DID)

    if usuario=='':
        pass #Vamos a / sin cookie

    if validaSesion(usuario)!=OK:
        return redirect('/',302)

    if request.method=='POST':
        logger.info('Ha llegado a POST')
        validaDeviceID(DID)
        sql='select * from Dispositivos where DID="' + DID + '"'
        logger.info("Consulta: " + sql)
        try:
            cursor = db.execute(sql)
            if(cursor.rowcount>0):
                registro = cursor.fetchone()
                SID=registro['SID']
    
                #Envia mensaje al disp anunciando que ha sido validado
                msg = {
                    "tipo":"configura",
                    "subtipo":"asociacion",
                    "orden":"validado",
                    "id": 0,
                    "valor": DID
                    }

                topic = app.config['pubTopicRoot'] + '/' + usuario + '/' + SID + '/buzon'
                logger.info('topic: ' + topic)
                logger.info('mensaje: ' + json.dumps(msg))
                publish_result = mqtt_client.publish(topic, json.dumps(msg))
                logger.info(publish_result)

        except Exception as e: 
            logger.info(e)  
            return make_response('Error SQL',500)        
        
        delante = make_response("validado",200)

    elif request.method == 'GET':
        logger.info('Ha llegado a GET')
        accion = str(request.args.get('accion'))
        logger.info("Accion: " + accion)

        if(accion=="datos"):
            delante = render_template('div_dispositivoDatos.html',USUARIO=usuario,SID=dameNombreDispositivo(DID))
            detras = ''
        elif(accion=="configuracion"):
            delante = render_template('/div_dispositivoConfiguracion.html',USUARIO=usuario,SID=dameNombreDispositivo(DID))
            detras = ''
        elif(accion=="reiniciar"):
            #Envia mensaje al disp anunciando que debe reiniciarse
            msg = {
                "tipo":"utilidad",
                "subtipo":"restart",
                "orden":"",
                "id": 0,
                "valor": ""
                }

            SID=dameNombreDispositivo(DID)
            topic = app.config['pubTopicRoot'] + '/' + usuario + '/' + SID + '/buzon'
            logger.info('topic: ' + topic)
            logger.info('mensaje: ' + json.dumps(msg))
            publish_result = mqtt_client.publish(topic, json.dumps(msg))
            logger.info(publish_result)
            
            #flash('Soicitud de reinicio enviada a ' + SID)
            #return redirect("/dispositivos/" + usuario, code=302)            
            delante = render_template('div_mensaje.html', MENSAJE = "Orden de reinicio enviada al dspositivo " + SID, SECUNDARIO = "Todo KO")
            detras = ''
        else:
            delante = make_response("",400)
            detras = ''

    elif request.method == 'DELETE':
        logger.info('Ha llegado a DELETE')
        borraDeviceID(DID)


        delante = make_response("Borrado",200)
        detras = ''

    return render_template('inicio.html', DELANTE=delante, DETRAS=detras,NOMBRE_PRINCIPIO=nombrePrincipio, NOMBRE_ROJO=nombreRojo, NOMBRE_FINAL=nombreFinal, PRINCIPIO=principio, ROJO=rojo, FINAL=final, PIE=pie, USUARIO=usuario)  

#************************************************* fin dispositivos ********************************************************
#************************************************* Web Actuador ********************************************************
@app.route('/webActuador/', methods=['GET'])
@app.route('/webActuador/<string:DID>/', methods=['GET'])
def webActuador(DID=""):
    usuario = request.cookies.get('userID')
    if not usuario:
        logger.info("---------------->Sin cookie")
        return redirect('/',302)
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            logger.info("---------------->No se puede renovar")
            return redirect('/',302)

    SID=dameNombreDispositivo(DID)
    if(SID==""): SID="Test1"
        
    delante = render_template('root.html',SID=SID)
    detras = ""
    return render_template('inicio.html', DELANTE=delante, DETRAS=detras,NOMBRE_PRINCIPIO=nombrePrincipio, NOMBRE_ROJO=nombreRojo, NOMBRE_FINAL=nombreFinal, PRINCIPIO=principio, ROJO=rojo, FINAL=final, PIE=pie, USUARIO=usuario)
#************************************************* fin Web Actuador ********************************************************
    
#************************************************* GUI usuario *************************************************************
#*************************************************
#*************************************************
#*************************************************
#*************************************************
#*************************************************
#************************************************* 
#*************************************************
#*************************************************
#*************************************************
#*************************************************
#*************************************************
#************************************************* 
#************************************************* API *************************************************************
@app.route('/test', methods = ['POST','GET'])
def test():
    return "OK"

@app.route('/configuracion/<string:usuario>/<string:nombreDevice>/<string:servicio>', methods = ['POST','GET'])
def configuracion(usuario,nombreDevice,servicio):
    logger.info("Entrando en configuracion...")
    #compruebo la contraseña
    if(validaContrasena(usuario,dameDeviceID(nombreDevice,usuario),request.args.get('address'))!=200):
        return make_response('address incorrecta',401)

    #Aseguro que esta validado antes de guardar o enviar config
    if dameDeviceValidado(dameDeviceID(nombreDevice,usuario))!=DISPOSITIVO_VALIDADO:
        logger.info('El dispositivo no esta validado')
        return make_response(('Dispositivo no validado',402))

    if request.method == 'POST': 
        nombreFichero = os.getcwd()        
        if(not nombreFichero.endswith('/')): nombreFichero += '/'

        nombreFichero += dirUsuarios 
        if not os.path.exists(nombreFichero): os.mkdir(nombreFichero)

        if(not nombreFichero.endswith('/')): nombreFichero += '/'
        nombreFichero += usuario + '/'
        if not os.path.exists(nombreFichero): os.mkdir(nombreFichero)

        nombreFichero += nombreDevice + '/' #+ 'recibidos/'
        if not os.path.exists(nombreFichero): os.mkdir(nombreFichero)

        #logger.info('Directorio de configuracion del dispositivo: ' + nombreFichero)
        if not os.path.exists(nombreFichero): return make_response(('Dir not found',404))

        nombreFichero += str(servicio + '.json')

        logger.info('se guardara en ' + nombreFichero)


        cad = request.data #request.get_json(True)
        logger.info('conenido decoded: -->' + cad.decode('utf-8') + '<--')

        with open(nombreFichero, 'w') as f:
            f.write(cad.decode('utf-8'))

        return make_response('Fichero de configuracion guardado',200)

    if request.method == 'GET': 
        #nombreFichero = dirUsuarios + usuario + '/' + nombreDevice + '/generados/' + str(servicio + '.json')
        nombreFichero = dirUsuarios + usuario + '/' + nombreDevice + '/' + str(servicio + '.json')
        logger.info('se leera de ' + nombreFichero)
        if not os.path.exists(nombreFichero): return make_response(('File not found',404))

        with open(nombreFichero, 'r') as f:
            cad = f.read()
            logger.info(cad)
        
        #return make_response(cad,200)
        return Response(response=cad, status=200, mimetype="application/json")

@app.route('/asocia/<string:usuario>/<string:deviceID>', methods = ['POST','GET'])
def asocia(usuario,deviceID):    
    #Compruebo los datos de entrada
    #compruebo el ID
    if len(deviceID)!=16: #64 bits en hexa son 16 aracteres
        logger.info('deviceID [' + deviceID + '] no valido') 
        return make_response('deviceID no valido',404)
    
    #compruebo el usuario
    sql = "select Usuario from Usuarios where Usuario='" + usuario + "'"
    logger.info("Consulta: " + sql)
    cursor = db.execute(sql)
    if(cursor.rowcount<=0):
        return make_response('Usuario no valido',404)

    #Segun el metodo de invocacion
    #POST
    if request.method == 'POST': 
        #Compruebo el nombreServicio
        nombreServicio=request.args.get('nombreServicio')        
        if not nombreServicio:
            return make_response('Nombre no valido',404)
        
        tipoDispositivo=request.args.get('tipoDispositivo')
        if not tipoDispositivo:
            return make_response('tipoDispositivo no valido',404)
        
        versionDispositivo=request.args.get('version')
        if not versionDispositivo:
            versionDispositivo=""

        #Compruebo si el dispositivo ya existe
        sql = "select * from Dispositivos where DID='" + deviceID + "'"
        logger.info("Consulta: " + sql)
        try:
            cursor = db.execute(sql)
            if(cursor.rowcount<=0):
                #Compruebo si hay otro con el mismo nombre para ese usuario
                sql = "select * from Dispositivos where CID='" + usuario + "' and SID='" + nombreServicio +"'"
                logger.info("Consulta: " + sql)
                cursor = db.execute(sql)
                
                if(cursor.rowcount<=0):
                    #Si no existe, lo creo
                    logger.info('No existe el deviceID, lo creo')
                    contrasena_txt = usuario + deviceID + nombreServicio
                    logger.info("Contrasena txt: " + contrasena_txt)
                    contrasena = md5(contrasena_txt.encode("utf-8")).hexdigest()

                    sql = "insert into Dispositivos (DID,SID,CID,Contrasena,DeviceType,version) values ('" + deviceID + "','" + nombreServicio + "','" + usuario + "','" + contrasena + "','" + tipoDispositivo + "','" + versionDispositivo + "')"
                    logger.info("Consulta: " + sql)
                    cursor = db.execute(sql)
                    db.commit()
                    return make_response('Dispositivo asignado', 201) #El dispositivo no estaba y se ha registrado
                else:
                    return make_response('El dispositivo no estaba registrado pero el usuario ya tiene otro con el mismo nombre', 409) #El dispositivo no estaba, pero hay otro del mismo usuariuo con ese nombre

            else: #Ya exite una relacion para ese dispositivo
                registro = cursor.fetchone()
                if(registro['CID']==usuario):
                    if(registro['SID']==nombreServicio):
                        if(registro['Validado']==1):
                            #Actualizo la version del dispositivo si toca
                            versionDispositivo=request.args.get('version')
                            if(registro['Version']!=versionDispositivo):
                                sql = "UPDATE Dispositivos SET version='"+ versionDispositivo +  "' WHERE DID='" + deviceID + "'"
                                logger.info("Consulta: " + sql)
                                cursor = db.execute(sql)
                                db.commit()  
                                logger.info("actualizada version del dispositivo")                              
                            return make_response('El dispositivo ya estaba registrado para ese usuario y con ese nombre', 200) #El dispositivo ya estaba asociado con el mismo usuario y nombre
                        else:
                            return make_response('El dispositivo ya estaba registrado para ese usuario y con ese nombre, pero no esta validado', 203) #El dispositivo ya estaba asociado con el mismo usuario y nombre
                    else: 
                        return make_response('El dispositivo ya existe, asignado a ese usuario con otro nombre ' + registro["SID"], 406) #El dispositivo esta pero con otro nombre
                else:
                    return make_response('El dispositivo ya existe, asignado a otro usuario', 401) #El dispositivo esta pero con otro usuario
        
        except Exception as e: 
            logger.info(e)  
            logging.error("Exception lanzada:\n %s",e)
            return make_response('Error SQL',500)
        
    #GET
    elif request.method == 'GET': 
        try:
            #compruebo la contraseña
            if(validaContrasena(usuario,deviceID,request.args.get('address'))!=200):
                return make_response('address incorrecta',405)

            #Compruebo si el dispositivo ya existe
            sql = "select * from Dispositivos where Validado=1 and DID='" + deviceID + "'"
            logger.info("Consulta: " + sql)
            cursor = db.execute(sql)
            if(cursor.rowcount<=0):
                #Si no existe, retorna error
                logger.info('No existe el deviceID')
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
            logger.info(e)            
            return make_response('Error SQL',500)  

@app.route('/lista')
def lista():
    return usuariosConectados.lista()

@app.route('/ficheroConfiguracion/<string:usuario>/<string:nombreDevice>/<string:servicio>', methods = ['POST','GET'])
def ficheroConfiguracion(usuario,nombreDevice,servicio):
    logger.info("Entrando en ficheroConfiguracion (" + usuario + "|" + nombreDevice + "|" +  servicio + ")...")
    #compruebo la sesion
    if(validaSesion(usuario)==KO):
        return redirect('/',302) #Esto deberia enviarse al navegador
        return make_response('No tiene sesion',401) #esto a un API

    #Aseguro que esta validado antes de guardar o enviar config
    if dameDeviceValidado(dameDeviceID(nombreDevice,usuario))!=DISPOSITIVO_VALIDADO:
        logger.info('El dispositivo no esta validado')
        return make_response(('Dispositivo no validado',402))

    if request.method == 'POST': 
        nombreFichero = dirUsuarios + usuario + '/'
        if not os.path.exists(nombreFichero):
            os.mkdir(nombreFichero)
        nombreFichero += nombreDevice + '/' #+ 'recibidos/'
        if not os.path.exists(nombreFichero):
            os.mkdir(nombreFichero)

        #logger.info('Directorio de configuracion del dispositivo: ' + nombreFichero)
        if not os.path.exists(nombreFichero): return make_response(('Dir not found',404))

        nombreFichero += str(servicio + '.json')

        logger.info('El fichero se guardara en ' + nombreFichero)

        cad = request.get_json(True,True,True)
        if(cad==None): resp = make_response('json no valido',400)
        else:
            #logger.info(request.get_json(True))
            cad=request.data
            with open(nombreFichero, 'w') as f:
                f.write(cad.decode('utf-8'))
            
            resp = make_response('Fichero de configuracion guardado',200)
        return resp

    if request.method == 'GET': 
        #valido que tiene permiso
        nombreFichero = dirUsuarios + usuario + '/' + nombreDevice + '/' + servicio + '.json'
        logger.info('se leera de ' + nombreFichero)
        if not os.path.exists(nombreFichero): return make_response(('File not found',404))

        with open(nombreFichero, 'r') as f:
            cad = f.read()
            logger.info(cad)
    
    return make_response(cad,200)

@app.route('/recuperaDatos/<string:usuario>/<string:nombreDevice>/<string:SSID>')
def recuperaDatos(usuario,nombreDevice,SSID):
    logger.info("Entrando en recuperaDatos...")
    #compruebo la sesion
    if(validaSesion(usuario)!=OK):
        return redirect('/',302) #Bueno para navegador

    #Aseguro que esta validado antes de guardar o enviar config
    if dameDeviceValidado(dameDeviceID(nombreDevice,usuario))!=DISPOSITIVO_VALIDADO:
        logger.info('El dispositivo no esta validado')
        return make_response(('Dispositivo no validado',405))

    #Recupero el valor de la base de datos
    sql='select Dato from Datos where CID="' + usuario + '" and SID="' + nombreDevice + '" and SSID="' + SSID + '"'
    cursor = db.execute(sql)
    if(cursor.rowcount==0): return make_response(('Sin datos',404))
    
    datos=cursor.fetchone()
    registros=json.loads(datos["Dato"])

    if SSID in ['maquinaestados','secuenciador']:
        registros={"datos":[registros]}
    
    logger.info(registros["datos"])
    logger.info(len(registros["datos"]))

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

    topic = app.config['pubTopicRoot'] + '/' + usuario + '/' + SID + '/buzon'
    publish_result = mqtt_client.publish(topic, json.dumps(msg))
    logger.info(publish_result)

    return make_response("Codigo de retorno:" + str(publish_result[0]), 200)

@app.route('/enviaMQTT/<string:usuario>', methods=['POST'])
def enviaMQTT(usuario):
    username = request.cookies.get('userID')
    logger.info('usuario de la cookie: ' + username)
    logger.info('usuario recbido: ' + usuario)

    if not username:
        #username=""
        logger.info('Salgo por aqui')
        #return make_response('',401)
        return redirect("/", code=302)
    else:        
        if(usuariosConectados.renueva(usuario,timeOutSesion)==False):
            username=""
            #return make_response('',402)
            return redirect("/", code=302)

    if(usuario!=username):
        #return make_response('motivo: ' + usuario + '!=' + username,405)
        return redirect("/", code=302)
    
    myTopic=request.args.get('topic')
    msg=request.args.get('msg')

    topic = app.config['pubTopicRoot'] + '/' + usuario + '/' + myTopic
    logger.info("A enviar:\ntopic:" + topic + "\nmensage:" + msg)
    publish_result = mqtt_client.publish(topic, msg)
    #logger.info(publish_result)

    return make_response("Codigo de retorno:" + str(publish_result[0]), 200)

@app.route('/<string:SID>/<string:servicio>', methods=['GET'])
def nombreDispositivoAPI(SID,servicio):
    servicioDatos={
            "estadoEntradas":"entradas",
            "estadoSalidas":"salidas",
            "estadoSecuenciador":"secuenciador",
            "estadoMaquinaEstados":"maquinaEstados",
            "estadoVariables":"Variables"
            }
    cad=""
    resp={}
    
    if servicio=="nombre":
        #Consulto el SID en la bd
        sql = "select SID, DeviceType,Version from Dispositivos where SID='" + SID +"'"
        logger.info("Consulta: " + sql)
        cursor = db.execute(sql)
        
        if(cursor.rowcount>0):
            registro = cursor.fetchone()
            
            resp = {
                "nombreDispositivo": registro["SID"],
                "nombreFamilia": registro["DeviceType"],
                "version": registro["Version"]
            }
        cad=json.dumps(resp)
        
    elif servicio=="servicios":
        #Consulto el SID en la bd
        sql = "select SSID from Datos where SID='" + SID +"'"
        logger.info("Consulta: " + sql)
        cursor = db.execute(sql)
        
        if(cursor.rowcount>0):
            registro = cursor.fetchall()
            
        datos=[]
        for x in registro:        
            datos.append(x["SSID"])
        
        resp["datos"]=datos
        cad=json.dumps(resp)
        
    elif servicio in servicioDatos:
        #Consulto el SID y el servicio en la bd
        sql = "select Dato from Datos where SID='" + SID + "' and SSID='" + servicioDatos[servicio] + "'"
        logger.info("Consulta: " + sql)
        cursor = db.execute(sql)
        
        if(cursor.rowcount>0):
            registro = cursor.fetchone()
            cad=registro["Dato"]
            cursor.fetchall()

    return Response(response=cad, status=200, mimetype="application/json")
#************************************************* API *************************************************************
#*************************************************
#*************************************************
#*************************************************
#*************************************************
#*************************************************
#*************************************************     
#*************************************************
#*************************************************
#*************************************************
#*************************************************
#*************************************************
#*************************************************     
#*************************************************Funciones**********************************************************************
def dameUsuario(username):
    sql = "select Nombre, Apellidos, Correo, Telefono, Direccion_ppal from Usuarios where Usuario = '" + username + "'"
    logger.info("Consulta: " + sql)

    try:
        cursor = db.execute(sql)

        #Si he encontrado el usaurio
        if (cursor.rowcount>0): 
            registro = cursor.fetchone()
            logger.info(f"Nombre: {registro['Nombre']}, Apellido: {registro['Apellidos']}, Correo: {registro['Correo']}, Telefono: {registro['Telefono']}, Direccion {registro['Direccion_ppal']}, Usuario {'username'}")

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

    except Exception as e: 
        logger.info(e)  
        logger.info("Error en la consulta")       
    
def validaContrasena(_usuario, _deviceID, _contrasena_in):
    sql="select Contrasena from Dispositivos where CID='" + _usuario + "' and DID='" + _deviceID + "'"
    cursor = db.execute(sql)
    if(cursor.rowcount<=0):
        #Si no existe, retorna error
        logger.info('No existe el dispositivo')
        return 404
    else:
        logger.info("hay un dispositivo, comparo las contrasenas")
        registro=cursor.fetchone()
        if(_contrasena_in!=registro['Contrasena']):
            #La contrasena recibida no es correcta
            logger.info('Contrasena incorrecta')
            return 405
    
    return 200

def validaSesion(usuario):
    username = request.cookies.get('userID')
    if not username:
        logger.info('No hay usuario en la cookie')
        return KO
    elif(usuario!=username):
        logger.info("El usuario pasado no es el de la cookie")
        return KO
    elif(usuariosConectados.renueva(usuario,timeOutSesion)==False):
        logger.info("Seion espirada")
        return KO

    return OK    

def dameNombreDispositivo(deviceID):
    sql='select SID from Dispositivos where DID="' + deviceID +'"'
    try:
        cursor = db.execute(sql)
        if(cursor.rowcount>0):
            registro=cursor.fetchone()
            return registro['SID']
        else:
            return ''
    except Exception as e: 
        logger.info(e)            
        return '' 

def dameUsuarioDispositivo(deviceID):
    sql='select CID from Dispositivos where DID="' + deviceID +'"'
    try:
        cursor = db.execute(sql)
        if(cursor.rowcount>0):
            registro=cursor.fetchone()
            return registro['CID']
        else:
            return ''
    except Exception as e: 
        logger.info(e)            
        return ''#make_response('Error SQL',500)

def dameDeviceID(nombre,usuario):
    sql='select DID from Dispositivos where CID="' + usuario + '" and SID="' + nombre +'"'
    try:
        cursor = db.execute(sql)
        if(cursor.rowcount>0):
            registro=cursor.fetchone()
            return registro['DID']
        else:
            return ''
    except Exception as e: 
        logger.info(e)            
        return ''#make_response('Error SQL',500)  

def dameDeviceValidado(ID):
    sql='select Validado from Dispositivos where DID="' + ID +'"'
    try:
        cursor = db.execute(sql)
        if(cursor.rowcount>0):
            registro=cursor.fetchone()
            return registro['Validado']
        else:
            return ''
    except Exception as e: 
        logger.info(e)            
        return ''#make_response('Error SQL',500)  

def borraDeviceID(ID):
    sql='delete from Dispositivos where DID="' + ID +'"'
    logger.info(sql)
    try:
        cursor = db.execute(sql)
        db.commit()
        return True

    except Exception as e: 
        logger.info(e)            
        return False

def validaDeviceID(DID):
    sql='update Dispositivos set Validado=1 where DID="' + DID +'"'
    logger.info(sql)
    try:
        cursor = db.execute(sql)
        db.commit()
        return True

    except Exception as e: 
        logger.info(e)            
        return False        

#***************MQTT*************
@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       logger.info('Conectado al bus MQTT')
       
       ret=mqtt_client.subscribe(app.config['subTopicRoot'] + '/#') # subscribe topic
       logger.info("subscrito al topic: " + app.config['subTopicRoot']  + "/#")
   else:
       logger.info('No se pudo conectar con el bus MQTT. Codigo de error:', rc)

@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):    
    try:
        #logger.info("recibido= topic:" + message.topic + " | mensaje: " + str(message.payload).decode("utf-8"))

        topics = str(message.topic).split('/')

        i=0
        for t in topics:
            #logger.info("topic " + str(i) + ": " + t) 
            i = i+1

        if len(topics)<3:
            logger.info("Faltan valores en el topic " + len(topics))
            return KO

        if(topics[0]!= app.config['subTopicRoot']):
            return KO
            
        CID = topics[1] #Customer ID
        SID = topics[2] #Service ID
        SSID = topics[3] #Sub service ID

        #Filtro los SSID que no se almacenan en la BD, por ejemplo will
        if (SSID in ["will","NULL","humbrales","buzon"]):
            #logger.info("Se descarta ", SSID)
            return OK

        #Transformo el mensaje entrante que debe ser un json
        mensaje = str(message.payload.decode("utf-8"))
        #logger.info(mensaje)
        datos_dic = json.loads(mensaje)
        #logger.info(datos_dic)
        datos = json.dumps(datos_dic)

        #compruebo el SID y el DID existen y estan asociados a ese CID        
        sql="select Validado from Dispositivos where SID='" + SID + "' and CID='" + CID + "'"
        #logger.info("consulta: ", sql)

        cursor = db.execute(sql)
        if(cursor.rowcount==0): 
            #logger.info("La pareja CID - SID no es valida") 
            return KO

        registro=cursor.fetchone()
        if(registro["Validado"]==0):
            #logger.info("El dispositivio no esta validado por el usuario")
            return KO

        #compruebo si es el primer dato (=Insert) o ya hay datos para ese servicio (=update)
        sql="select * from Datos where SSID='" + SSID + "' and SID='" + SID + "' and CID='" + CID + "'"
        #logger.info("consulta: " + sql, file=sys.stderr)

        timeStamp=time.strftime("%Y-%m-%d %I:%M:%S")

        cursor = db.execute(sql)
        if(cursor.rowcount>1):
            logger.info(f"Encuentro mas de un registro para {sql}")#, file=sys.stderr)

            sql="DELETE FROM Datos WHERE CID='" + CID + "' AND SID='" + SID + "' AND SSID='" + SSID +"'"
            #logger.info("sqi: " + sql, file=sys.stderr)
            cursor = db.execute(sql)
    
        elif(cursor.rowcount==0):
            #Preparo la insercion de los datos
            sql = "insert into Datos (CID, SID, SSID, Dato, timeCambio) values ('" + CID + "','" + SID + "','" + SSID + "','" + datos + "','"  + timeStamp + "')"
        else:
            #Preparo la actualizacion de los datos
            #sql = "update Datos set Dato='" + datos + "', timeCambio= STR_TO_DATE( '" + timeStamp + "', '%d/%m/%Y %H:%i:%s') where SSID='" + SSID + "' and SID='" + SID + "' and CID='" + CID + "'"
            sql = "update Datos set Dato='" + datos + "', timeCambio= '" + timeStamp + "' where SSID='" + SSID + "' and SID='" + SID + "' and CID='" + CID + "'"
        #logger.info("consulta: ", sql)
        cursor = db.execute(sql)
        db.commit()
        return OK

    except Exception as e:
        logger.info("------------------error--------------")
        logger.info(f"topic: {str(message.topic)} || mensaje: {str(message.payload.decode('utf-8'))}")
        logger.info(e)  
        logger.info("Topic que genera el error: ", message.topic)
        logger.info("Mensaje que genera el error: ", message.payload.decode("utf-8"))
        db.rollback()
        logger.info("Error en la consulta")
        return KO   
      
@mqtt_client.on_log()
def handle_logging(client, userdata, level, buf):
    if level == MQTT.MQTT_LOG_ERR:
        logger.info('Error: {}'.format(buf))   
    else:
        logger.info('Mensaje: {}'.format(buf))   
        
@mqtt_client.on_publish()
def handle_publish(client, userdata, mid):
    #logger.info('Published message with mid {}.'.format(mid))        
    pass
#***************MQTT*************
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

        # Enable log if need
        if "Logging" in configuracion:
            LogConfig = configuracion["Logging"]
            if "LOG_FILE" in LogConfig: LOG_FILE = LogConfig["LOG_FILE"]
            if "LOG_LEVEL" in LogConfig: LOG_LEVEL = LogConfig["LOG_LEVEL"]
            if "LOG_FORMAT" in LogConfig: LOG_FORMAT = LogConfig["LOG_FORMAT"]
            if "LOG_DATE_FORMAT" in LogConfig: LOG_DATE_FORMAT = LogConfig["LOG_DATE_FORMAT"]
            logging.basicConfig(level=LOG_LEVEL,
                            format=LOG_FORMAT,
                            datefmt=LOG_DATE_FORMAT,
                            filename=LOG_FILE,
                            filemode='a')
        logger = logging.getLogger()
        logger.info("Logger on")

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
            '''
            db = MySQLdb.connect(dbIP,dbUsuario,dbPassword,dbNombre, charset='utf8')
            db.autocommit(True)
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            logger.info('Conectado a la base de datos ' + dbNombre)
            '''
            db = DBConnection(dbIP, dbUsuario, dbPassword, dbNombre)
        except MySQLdb.Error as e:
            logger.info("No puedo conectar a la base de datos:",e)
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
        if "pubTopic" in MQTT: app.config['pubTopicRoot'] = MQTT["pubTopic"]
        else: app.config['pubTopicRoot']=""
        if "subTopic" in MQTT: app.config['subTopicRoot'] = MQTT["subTopic"]
        else: app.config['subTopicRoot']=""
        if "pubTopic" in MQTT: app.config['pubTopicRoot'] = MQTT["pubTopic"]
        else: app.config['pubTopicRoot']=""
        if "subTopic" in MQTT: app.config['subTopicRoot'] = MQTT["subTopic"]
        else: app.config['subTopicRoot']=""

        app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
        app.config['MQTT_TLS_ENABLED'] = False  # If your server supports TLS, set it True
        # Parameters for SSL enabled
        # app.config['MQTT_BROKER_PORT'] = 8883
        # app.config['MQTT_TLS_ENABLED'] = True
        # app.config['MQTT_TLS_INSECURE'] = True
        # app.config['MQTT_TLS_CA_CERTS'] = 'ca.crt'
        
        logger.info("Configuracion MQTT\nbroker: [" + str(app.config['MQTT_BROKER_URL']) + "]\npuerto: [" + str(app.config['MQTT_BROKER_PORT']) + "]\nusuario: [" + str(app.config['MQTT_USERNAME']) + "]\npass: [" + str(app.config['MQTT_PASSWORD']) + "]\npub topic root: [" + str(app.config['pubTopicRoot']) + "]\nsub topic root: [" + str(app.config['subTopicRoot']) + "]")

        mqtt_client.init_app(app)

        #Config de presentacion
        raiz=configuracion["Raiz"]
        nombre=raiz["nombre"]
        cabecera = raiz["cabecera"]
        pie = raiz["pie"]
        
        
        #nombre
        i=0
        nombrePrincipio=""
        while i<(len(nombre)-3):
            nombrePrincipio += nombre[i]
            i = i + 1

        #logger.info('Nombre principio: ' + nombrePrincipio,sys.stderr)

        nombreRojo=nombre[len(nombre)-3]
        #logger.info('rojo: ' + nombreRojo,sys.stderr)
        nombreFinal=nombre[len(nombre)-2]+nombre[len(nombre)-1]
        #logger.info('final: ' + nombreFinal,sys.stderr)

        #cabecera
        i=0
        principio=""
        while i<(len(cabecera)-3):
            principio += cabecera[i]
            i = i + 1

        rojo=cabecera[len(cabecera)-3]
        #logger.info('rojo: ' + rojo,sys.stderr)
        final=cabecera[len(cabecera)-2]+cabecera[len(cabecera)-1]
        #logger.info('final: ' + final,sys.stderr)

        #config conectados
        usuariosConectados=conectados.Conectados()

        #Arranco el app
        app.run(host=IP, port=puerto)
#*************************************************MAIN**********************************************************************
#desconexion db https://stackoverflow.com/questions/19440055/correct-way-of-keeping-mysql-connection
