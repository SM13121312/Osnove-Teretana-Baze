import mysql.connector
from datetime import date
from tabulate import tabulate

# connection = mysql.connector.connect(
#     host="localhost",         # Replace with your database host
#     user="root",              # Replace with your database username
#     password="1234",          # Replace with your database password
#     database="projekatjedan"  # Replace with your database name
# )
#
# cursor = connection.cursor()
#
# datetoday = date.today()
#
#
# query = "SELECT * FROM korisnici WHERE datum_isteka < %s"
# cursor.execute(query, (datetoday,))
# data = cursor.fetchall()
# if data:
#     print(data)
# else:
#     print('Nema tkavih')



cursor.close()
connection.close()

