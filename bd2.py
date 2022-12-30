import sys
import MySQLdb
try:
	db = MySQLdb.connect("localhost","domoticae","88716","domoticae" )
except MySQLdb.Error as e:
	print("No puedo conectar a la base de datos:",e)
	sys.exit(1)

sql="select * from Usuarios"
cursor = db.cursor()
try:
   cursor.execute(sql)
   registros = cursor.fetchall()
   for registro in registros:
      print(registro[0],registro[1],registro[2],registro[3],registro[4])
except:
   print("Error en la consulta")
db.close()
