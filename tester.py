import sqlite3
from datetime import date, timedelta, datetime
from tabulate import tabulate
import random
import string
import sys

connection = sqlite3.connect('BAZAzaprojekat.db')
cursor = connection.cursor()


dasnji_datum = date(2025, 2, 23)
prosli_datum = dasnji_datum - timedelta(days=30)
print(prosli_datum)


cursor.close()
connection.close()



