import json

OK                          =  0
CONFIGURACION_POR_DEFECTO   = -1
ERROR_FICHERO_CONFIGURACION = -2
INICIAL                     = -100

class Configuracion:
    __IP = 0
    __puerto = 0
    __outputFile = ''
    __dbIP = 0
    __dbPuerto = 0
    __baseDatos = 0
    __measurement =0
    __configurado = INICIAL

    def __init__(self, fichero, debug = False, IP = "0.0.0.0",puerto = "0",outputFile='', dbIP = "0.0.0.0",dbPuerto = 0,baseDatos = '',measurement = ''):
        #valores por defecto sobre el bus MQTT
        __IP = IP
        __puerto = puerto
        __outputFile = outputFile

        #valores por defecto sobre la base de datos InfluxDB
        __dbIP = dbIP
        __dbPuerto = dbPuerto
        __baseDatos = baseDatos
        __measurement = measurement

        self.__leeConfiguracion(fichero,debug)

    def __leeConfiguracion(self,fichero,debug=False):
        if (debug==True): print("\nInicio de configuracion----------------------------------------------------------------------")
        self.__configurado = OK #por defecto va bien...

        try:
            #leo el fichero de configuracion
            with open(fichero) as json_file:
                configuracion = json.load(json_file)
                if (debug==True): print("Configuracion leida=\n %s" %configuracion)
        except :
            if (debug==True): print("No se pudo obtener el fichero de configuracion")
            self.__configurado = ERROR_FICHERO_CONFIGURACION
            return

        if configuracion.has_key('Proceso'): 
            proceso = configuracion['Proceso']

            if proceso.has_key('IP'): self.setIP(proceso.pop("IP"))
            else: 
                if (debug==True): 
                    print("IP no esta configurado. Valor por defecto.")
                    self.__configurado = CONFIGURACION_POR_DEFECTO

            if proceso.has_key('puerto'): self.setPuerto(proceso.pop("puerto"))
            else: 
                if (debug==True): 
                    print("puerto no esta configurado. Valor por defecto.")
                    self.__configurado = CONFIGURACION_POR_DEFECTO

            if proceso.has_key('outputFile'): self.setOutputFile(proceso.pop("outputFile"))
            else: 
                if (debug==True): 
                    print("outputFile no esta configurado. Valor por defecto.")
                    self.__configurado = CONFIGURACION_POR_DEFECTO
        else: 
            if (debug==True): 
                print("No se ha configurado el proceso. Valores pore defecto")
                self.__configurado = CONFIGURACION_POR_DEFECTO

        if configuracion.has_key('DB'): 
            DBConfig = dict(configuracion['DB'])

            if DBConfig.has_key('dbIP'): self.setDbIP(DBConfig.pop("dbIP"))
            else: 
                if (debug==True): 
                    print("dbIP no esta configurado. Valor por defecto.")
                    self.__configurado = CONFIGURACION_POR_DEFECTO

            if DBConfig.has_key('dbPuerto'): self.setDbPuerto(DBConfig.pop("dbPuerto"))
            else: 
                if (debug==True): 
                    print("dbPuerto no esta configurado. Valor por defecto.")
                    self.__configurado = CONFIGURACION_POR_DEFECTO

            if DBConfig.has_key('baseDatos'): self.setBaseDatos(DBConfig.pop("baseDatos"))
            else: 
                if (debug==True): 
                    print("baseDatos no esta configurado. Valor por defecto.")
                    self.__configurado = CONFIGURACION_POR_DEFECTO

            if DBConfig.has_key('measurement'): self.setMeasurement(DBConfig.pop("measurement"))
            else: 
                if (debug==True): 
                    print("measurement no esta configurado. Valor por defecto.")
                    self.__configurado = CONFIGURACION_POR_DEFECTO
        else:
            if (debug==True): 
                print("No se ha configurado DB. Valores pore defecto")
                self.__configurado = CONFIGURACION_POR_DEFECTO

        if (debug==True): print("Configuracion del proceso")
        if (debug==True): print("IP = %s" %self.__IP)
        if (debug==True): print("puerto = %s" %self.__puerto)
        if (debug==True): print("outputFile = %s" %self.__outputFile)

        if (debug==True): print("Configuracion de DB Influx")
        if (debug==True): print("dbIP = %s" %self.__dbIP)
        if (debug==True): print("dbPuerto = %s" %self.__dbPuerto)
        if (debug==True): print("baseDatos = %s" %self.__baseDatos)
        if (debug==True): print("measurement = %s" %self.__measurement)


    def setIP(self,valor): self.__IP=str(valor)
    def setPuerto(self,valor): self.__puerto=valor
    def setOutputFile(self,valor): self.__outputFile=valor
    def setDbIP(self,valor): self.__dbIP=str(valor)
    def setDbPuerto(self,valor): self.__dbPuerto=valor
    def setBaseDatos(self,valor): self.__baseDatos=str(valor)
    def setMeasurement(self,valor): self.__measurement=str(valor)

    def getIP(self): return self.__IP
    def getPuerto(self): return self.__puerto
    def getOutputFile(self): return self.__outputFile    
    def getDbIP(self): return self.__dbIP
    def getDbPuerto(self): return self.__dbPuerto
    def getBaseDatos(self): return self.__baseDatos
    def getMeasurement(self): return self.__measurement

    def getConfigurado(self): return self.__configurado