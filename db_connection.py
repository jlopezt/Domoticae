import logging
import MySQLdb
from MySQLdb import cursors
import time

class DBConnection:
    def __init__(self, host, user, password, db_name):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """Establece la conexión inicial a la base de datos"""
        try:
            self.connection = MySQLdb.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.db_name,
                charset='utf8'
            )
            self.connection.autocommit(True)
            self.cursor = self.connection.cursor(cursors.DictCursor)
        except MySQLdb.Error as e:
            print(f"Error conectando a la base de datos: {e}")
            raise
    
    def check_connection(self):
        """Verifica si la conexión está activa y reconecta si es necesario"""
        try:
            # Intentamos hacer ping sin argumentos
            self.connection.ping()
        except (AttributeError, MySQLdb.Error):
            # Si hay error, intentamos reconectar
            print("Conexión perdida. Intentando reconectar...")
            self.connect()
    
    def execute(self, query, params=None):
        """Ejecuta una consulta asegurando que la conexión esté activa"""
        try:
            self.check_connection()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor
        except MySQLdb.Error as e:
            print(f"Error ejecutando consulta: {e}")
            raise
    
    def commit(self):
        """Hace commit de la transacción actual"""
        self.connection.commit()
    
    def close(self):
        """Cierra la conexión y el cursor"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()