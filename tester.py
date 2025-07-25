import sqlite3
from datetime import date, timedelta, datetime
from tabulate import tabulate
import random
import string
import sys

connection = sqlite3.connect('BAZAzaprojekat.db')
cursor = connection.cursor()


cursor.execute('SELECT sifra_treninga, dan FROM trening')
informacije = cursor.fetchall()
for proiz, info in informacije:
  print(kita)


cursor.close()
connection.close()



