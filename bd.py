#import mysql.connector as mariadb
import mariadb

mariadb_conexion = mariadb.connect(host='localhost',
                                   port='3306',
                                   user='domoticae',
                                   password='88716',
                                   database='domoticae',
                                   charset="utf8mb3")

cursor = mariadb_conexion.cursor()

try:
    cursor.execute("SELECT * FROM Usuarios")
    for nombre, apellidos, correo, telefono, usuario, password in cursor:
        print("nombre: " + nombre)
        print("apellido: " + apellido)
        print("correo: " + correo)
        print("telefono: " + telefono)
        print("usuario: " + usuario)
        print("password: " + password)

except mariadb.Error as error:
    print("Error: {}".format(error))

mariadb_conexion.close()
