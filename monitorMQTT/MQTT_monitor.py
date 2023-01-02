import sys

import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

import MySQLdb

#declaracion de constantes
#Retorno de funciones
OK = 1
KO = 0

# MQTT Error values 
MQTT_ERR_AGAIN = -1
MQTT_ERR_SUCCESS = 0
MQTT_ERR_NOMEM = 1
MQTT_ERR_PROTOCOL = 2
MQTT_ERR_INVAL = 3
MQTT_ERR_NO_CONN = 4
MQTT_ERR_CONN_REFUSED = 5
MQTT_ERR_NOT_FOUND = 6
MQTT_ERR_CONN_LOST =7
MQTT_ERR_TLS = 8
MQTT_ERR_PAYLOAD_SIZE = 9
MQTT_ERR_NOT_SUPPORTED = 10
MQTT_ERR_AUTH = 11 
MQTT_ERR_ACL_DENIEDE =12
MQTT_ERR_UNKNOWN = 13 
MQTT_ERR_ERRNO = 14
MQTT_ERR_QUEUE_SIZE = 15 

#declaracion de variables globales
configFile='../config/config.json'
CID = ""
SID = ""
DID = ""
db=""

# when connecting to mqtt do this;
def on_connect(client, userdata, flags, rc):
    print("Conectado al bus con el codigo de resultado "+str(rc))
    ret = client.subscribe(subTopicRoot + '/#')
    print("Subscrito al topic " + subTopicRoot + ", con el resultado "+str(ret))
    #publish_mqtt("Conectrado al bus...")

# when receiving a mqtt message do this;
def on_message(client, userdata, msg):
    try:
        #print("recibido= topic:" + msg.topic + " | mensaje: " + str(msg.payload))
        print("recibido= topic:" + msg.topic)

        topics = str(msg.topic).split('/')

        i=0
        for t in topics:
            #print("topic " + str(i) + ": " + t) 
            i = i+1

        if len(topics)<3:
            print("Faltan valores en el topic " + len(topics))
            return KO

        if(topics[0]!= subTopicRoot):
            return KO
            
        CID = topics[1] #Customer ID
        SID = topics[2] #Service ID
        SSID = topics[3] #Sub service ID

        #Transformo el mensaje entrante que debe ser un json
        mensaje = str(msg.payload.decode("utf-8"))
        #print (mensaje)
        datos_dic = json.loads(mensaje)
        #print(datos_dic)
        datos = json.dumps(datos_dic)

        #compruebo el SID y el DID existen y estan asociados a ese CID        
        sql="select Validado from Dispositivos where SID='" + SID + "' and CID='" + CID + "'"
        #print("consulta: ", sql)

        cursor.execute(sql)
        if(cursor.rowcount==0): 
            print("La pareja CID - SID no es valida") 
            return KO

        registro=cursor.fetchone()
        if(registro["Validado"]==0):
            print("El dispositivio no esta validado por el usuario")
            return KO

        #compruebo si es el primer dato (=Insert) o ya hay datos para ese servicio (=update)
        sql="select * from Datos where SSID='" + SSID + "' and SID='" + SID + "' and CID='" + CID + "'"
        #print("consulta: ", sql)

        cursor.execute(sql)
        if(cursor.rowcount==0):
            #Preparo la insercion de los datos
            sql = "insert into Datos (CID, SID, SSID, Dato) values ('" + CID + "','" + SID + "','" + SSID + "','" + datos + "')"
        else:
            #Preparo la actualizacion de los datos
            sql = "update Datos set Dato='" + datos + "' where SSID='" + SSID + "' and SID='" + SID + "' and CID='" + CID + "'"
            
        #print("consulta: ", sql)
        cursor.execute(sql)
        db.commit()
        return OK

    except Exception as e:
        print(e)  
        db.rollback()
        print("Error en la consulta")
        return KO

# to send a message
def publish_mqtt(data):
    mqttc = mqtt.Client("domoticaeMonitor")
    mqttc.connect(broker, puerto)
    mqttc.publish(pubTopicRoot, data)
    #mqttc.loop(2) //timeout = 2s

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


if __name__ == "__main__":
    with open(configFile) as json_file:
        configuracion = json.load(json_file)        

        #config de BBDD
        dbConfig = configuracion["DB"]
        if "dbIP" in dbConfig: dbIP = dbConfig["dbIP"]
        else: dbIP=""
        if "dbPuerto" in dbConfig: dbPuerto = dbConfig["dbPuerto"]
        else: dbPuerto=""
        if "dbUsuario" in dbConfig: dbUsuario = dbConfig["dbUsuario"]
        else: dbUsuario=""
        if "dbPassword" in dbConfig: dbPassword = dbConfig["dbPassword"]
        else: dbPassword=""
        if "dbNombre" in dbConfig: dbNombre  = dbConfig["dbNombre"]
        else: dbNombre=""

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
        if "broker" in MQTT: broker = MQTT["broker"]
        else: broker=""
        if "puerto" in MQTT: puerto = MQTT["puerto"]
        else: puerto=""
        if "usuario" in MQTT: MQTTusuario = MQTT["usuario"]
        else: MQTTusuario=""
        if "password" in MQTT: MQTTpass = MQTT["password"]
        else: MQTTpass=""
        if "pubTopic" in MQTT: pubTopicRoot = MQTT["pubTopic"]
        else: pubTopicRoot=""
        if "subTopic" in MQTT: subTopicRoot = MQTT["subTopic"]
        else: subTopicRoot=""

        print("Configuracion MQTT\nbroker: [" + str(broker) + "]\npuerto: [" + str(puerto) + "]\nusuario: [" + str(MQTTusuario) + "]\npass: [" + str(MQTTpass) + "]\npub topic root: [" + str(pubTopicRoot) + "]\nsub topic root: [" + str(subTopicRoot) + "]")

        client = mqtt.Client(client_id="domoticae", clean_session=False, userdata=None)
        client.on_connect = on_connect
        client.on_message = on_message
        client.username_pw_set(MQTTusuario, MQTTpass)
        ret = client.connect(broker, puerto, 60)
        client.loop_forever()
