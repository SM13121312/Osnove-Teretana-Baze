import sqlite3
from datetime import date, timedelta, datetime
from tabulate import tabulate
import random
import string
import sys

connection = sqlite3.connect('BAZAzaprojekat.db')
cursor = connection.cursor()


dani_u_nedelji = ('ponedeljak', 'utorak', 'sreda', 'cetvrtak', 'petak', 'subota', 'nedelja')
while True:
    print('\n Ukupan broj rezervacija za izabran dan (u nedelji) održavanja treninga.\n')
    odabir = input('Unesi dan u nedelji koji te zanima: ')
    if odabir not in dani_u_nedelji:
        print('\nIzmislili ste dan u nedelji.\n'
                  'Unesi ponovo.\n')
    else:
        break


izbor_dana = f'%{odabir}%'    
cursor.execute('''SELECT COUNT(rezervacije.sifra_rezervacije), trening.dan, rezervacije.datum
                        FROM rezervacije
                        JOIN trening
                        ON trening.sifra_treninga
                        WHERE trening.dan LIKE ? 
                        GROUP BY trening.dan;''', (izbor_dana,))
data = cursor.fetchall()
tabela_data = []
for informacija in data:
    datum = informacija[2]
    zaprebacivanje = [informacija[0], odabir, datum]
    print(datum)
    
    dan_int = datetime.strptime(datum, "%Y-%m-%d")
    print(dan_int)
    
    dan_broj = dan_int.weekday()
    print
    
    # print(dan_broj)
    # print(type(dan_broj))
    # if dani_u_nedelji[dan_broj] = odabir:
    #     print(zaprebacivanje)
     
    
    
    


cursor.close()
connection.close()



