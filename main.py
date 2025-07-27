import os
import sys
from datetime import date, timedelta
import shared
from tabulate import tabulate
import re
import sqlite3
import random
import string

from pregpretiostalo import *
from sveostalo1 import *
from rezervacijeiostalo import *


connection = sqlite3.connect('Baza.db')
cursor = connection.cursor()





def provera_statusa():
    danasnji_datum = date.today().strftime('%Y-%m-%d')
    za_mesec_datum = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
    cursor.execute('''UPDATE korisnici
                        SET status_korisnika = 'neaktivan', paket = NULL
                        WHERE datum_isteka < ?''', (danasnji_datum,))
    connection.commit()



def restart_baze():
    with open('Tabele.sql', 'r', encoding = 'utf-8') as file:
        sql_fajl = file.read()

    milan = sql_fajl.split(';')
    for i in range(0, len(milan)):
        cursor.execute(milan[i])
        connection.commit();
        

def meniprvi():
    print('\n-----FIRST MENU-----\n')
    print('CHOOSE:\n'
          '1) REGISTRACIJA\n'
          '2) PRIJAVA\n'
          '3) Kruziraj gao guest\n'
          'x) IZLAZAK'
          )

    while True:
        odabir = input('Tvoj izbor: ')
        if odabir == '1':
            registracija()
        elif odabir == '2':
            log_in()
        elif odabir == '3':
            kruziraj_kao_gest()
        elif odabir.lower() == 'x':
            print('CAO')
            cursor.close()
            connection.close()
            sys.exit()
        else:
            print('NEVAZECI IZBOR')



def registracija():
    print('\n\nUNESI SVOJE INFORMACIJE')
    username = valusername()
    password = valpassword()

    while True:
        name = input('Tvoje ime: ')
        if name.strip() == '':
            print('Unesi svoje pravo ime.')
        elif name.isalpha():
            break
        else:
            print('Unesi svoje pravo ime.')

    while True:
        surname = input('Tvoje prezime: ')
        if surname.strip() == '':
            print('Unesi svoje pravo prezime.')
        elif surname.isalpha():
            break
        else:
            print('Unesi svoje pravo prezime.')

    role = 'korisnik'
    status = 'aktivan'
    packet = 'standard'

    datetoday = date.today().isoformat()
    exp_date = (date.today() + timedelta(days=30)).isoformat()

    cursor.execute(
        'INSERT INTO korisnici VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (username, password, name, surname, role, status, packet, datetoday, datetoday, exp_date)
    )
    connection.commit()



def valusername():
    cursor.execute('SELECT korisnicko_ime FROM korisnici')
    imenarazna = [imenica[0] for imenica in cursor.fetchall()]
    pattern = r'^[a-zA-Z0-9]+$'
    while True:
        username = input('Izaberi username, username sadrzi samo slova (A-Z) i brojeve: ')
        username = username.lower()
        if username in imenarazna:
            print('Username vec postoji.')
        elif not re.match(pattern, username):
            print('Izaberi neki drugi, samo slova i brojevi su dozvoljeni.')
        else:
            return username.strip()



def valpassword():
    while True:
        password = input('Izaberi sifru: ')
        if len(password) > 6:
            if any(char.isdigit() for char in password):
                return password
            else:
                print('Sifra treba da sadrzi bar jedan broj.')
        else:
            print('Sifra treba da bude dugacka bar 7 karaktera.')

def unosenje_termina():
    datum = date.today()
    godina = datum.year
    mesec = datum.month

    # if datum.day != 1:
    #     print('It is not first day in month.')
    #     return

    dani_u_nedelji = {
        'ponedeljak': 0,
        'utorak': 1,
        'sreda': 2,
        'cetvrtak': 3,
        'petak': 4,
        'subota': 5,
        'nedelja': 6
    }  
    
    dani_u_listi = ['ponedeljak', 'utorak', 'sreda', 'cetvrtak', 'petak', 'subota', 'nedelja']

    cursor.execute('SELECT sifra_treninga, dan FROM trening')
    informacije = cursor.fetchall()
    # if informacije == []:
    #     print("prazan skup")
    # else:
    #     print(informacije)

    for sifra_treninga, dan in informacije:
        dani_vezbanja = dan.lower().split('|') 

        svi_datumi = []
        
        for dan in dani_vezbanja:
            if dan not in dani_u_nedelji:
                print('Greska u bazi.')
                continue

            dan_vezbanja = dani_u_nedelji[dan]
            datum_za_loop = date(godina, mesec, 1)

            while datum_za_loop.month == mesec:
                if datum_za_loop.weekday() == dan_vezbanja:
                    svi_datumi.append(datum_za_loop)
                datum_za_loop += timedelta(days=1)

        for datic in svi_datumi:
            danko_bananko = dani_u_listi[datic.weekday()]
            datic = datic.strftime("%Y-%m-%d")
                    
            cursor.execute(
                'SELECT COUNT(*) FROM termin WHERE sifra_treninga = ? AND datum = ?',
                (sifra_treninga, datic)
            )
            already_exists = cursor.fetchone()[0] > 0

            if already_exists:
                continue

            while True:
                cursor.execute('SELECT sifra_termina FROM termin')
                sve_sifre_termina = [sif[0] for sif in cursor.fetchall()]
                random_slova = ''.join(random.choices(string.ascii_uppercase, k=2))
                sifra_termina = str(sifra_treninga) + random_slova

                if sifra_termina not in sve_sifre_termina:
                    break

            try:
                cursor.execute('INSERT INTO termin VALUES (?, ?, ?, ?)', (sifra_termina, datic, sifra_treninga, danko_bananko))
            except sqlite3.Error as e:
                print("SQL Error:", e)

    print('uspeo si')        
    connection.commit()
  

def izvestaji():
    while True:
        print('1) Lista rezervacija za odabran datum rezervacije.\n'
              '2) Lista rezervacija za odabran datum termina treninga.\n'
              '3) Lista rezervacija za odabran datum rezervacije i odabranog instruktora.\n'
              '4) Ukupan broj rezervacija za izabran dan (u nedelji) održavanja treninga.\n'
              '5) Ukupan broj rezervacije po instruktorima.\n'
              '6) Ukupan broj rezervacija realizovanih za premium i za standard paket.\n'
              '7) Tri najpopularnija programa treninga u poslednjih godinu dana.\n'
              '8) Najpopularniji dan u nedelji.')
        odabir = input('Unesite broj vaseg odabira ili "x" za vracanje na meni: ')
        if odabir == '1':
            rezervacije_za_datum(cursor)
        elif odabir == '2':
            rezervacije_za_datum_termina(cursor)
        elif odabir == '3':
            rezervacije_za_datum_i_instruktora(cursor)
        elif odabir == '4':
            rezervacije_za_dan(cursor)
        elif odabir == '5':
            rezervacije_po_instruktoru(cursor)
        elif odabir == '6':
            rezervacije_za_premium_ili_standard(cursor)
        elif odabir == '7':
            najpopularniji_program(cursor)
        elif odabir == '8':
            najpopularniji_dan(cursor)
        elif odabir.lower() == 'x':
            return
        else:
            print('\nNEVAZECI IZBOR\n')
        

def mesecna_nagrada():
    cursor.execute('''UPDATE korisnici
                    SET status_korisnika = 'aktivan', paket = 'premium', datum_aktivacije = ?, datum_isteka = ?
                    WHERE status_korisnika = 'neaktivan' AND korisnicko_ime IN (
                            SELECT rezervacije.korisnicko_ime
                            FROM rezervacije
                            WHERE rezervacije.datum BETWEEN datum_aktivacije AND datum_isteka
                            GROUP BY korisnicko_ime
                            HAVING COUNT(sifra_rezervacije) > 27)''', (danasnji_datum, za_mesec_datum))
    connection.commit();

#
#
#
#
# MENUES FOR USERS

def log_in():
    username = input('Unesi username: ')
    cursor.execute('SELECT COUNT(korisnicko_ime) FROM korisnici WHERE korisnicko_ime = ?', (username,))
    brojac = cursor.fetchone()
    if brojac[0] > 0:
        password = input('Unesi lozinku: ')
        cursor.execute('SELECT lozinka FROM korisnici WHERE korisnicko_ime = ?', (username,))
        sifra = cursor.fetchone()
        if password == sifra[0]:
            cursor.execute('SELECT uloga, status_korisnika, paket, ime, prezime, datum_aktivacije, datum_isteka FROM korisnici WHERE korisnicko_ime = ?', (username,))
            role, status, package, name, surname, act_date, exp_date = cursor.fetchone()
            shared.current_user = [{'username': username, 'role': role, 'status' : status, 'package' : package, 'name' : name, 'surname' : surname, 'act_date' : act_date, 'exp_date' : exp_date}]

            if role == 'admin':
                meni_admin()
            elif role == 'instruktor':
                meni_instruktor()
            elif role == 'korisnik':
                meni_korisnik()
            else:
                print('!!!Greska u bazi!!!')
        else:
            print('Pogresna sifra!!!\n')
    else:
        print('Nepostojeci korisnik')
        log_in()

def log_out():
    if shared.current_user:
        print('CAOOOOOOOO')
        current_user = []
        meniprvi()
    else:
        print('Niko nije trenutno ulogovan.')



def meni_admin():
    while True:
        print('\nCao, admine.')
        print('1) Pregled programa treninga\n'
              '2) Pretraga programa treninga\n'
              '3) Pretraga termina treninga\n'
              '4) Unos, izmena i brisanje programa treninga\n'
              '5) Unos, izmena i brisanje treninga\n'
              '6) Registracija novih intruktora i admina\n'
              
              '7) Razni izvestaji\n'
              'xxx) Odjava\n'
              'x) Izlazak iz aplikacije\n')
        odabir = input('Tvoj odabir: ')
        if odabir == '1':
            pregled_programa(cursor)
        elif odabir == '2':
            pretraga_programa(cursor)
        elif odabir == '3':
            pretragatermina(cursor)
        elif odabir == '4':
            unos_izmena_brisanje_programa(cursor)
            connection.commit()
        elif odabir == '5':
            unos_izmena_brisanje_treninga(cursor)
            connection.commit()
        elif odabir == '6':
            reg_instruktora(cursor)
            connection.commit()
        
        elif odabir == '7':
            izvestaji()
        elif odabir == 'xxx':
            log_out()
        elif odabir.lower() == 'x':
            cursor.close()
            connection.close()
            sys.exit()
        else:
            print('NEVAZECI IZBOR')

def meni_instruktor():
    while True:
        connection.commit()
        print('\nCao, instruktore.')
        print('1) Pregled programa treninga\n'
              '2) Pretraga programa treninga\n'
              '3) Pretraga termina treninga\n'
              '4) Aktivacija premium paketa članstva\n'
              '5) Rezervacija mesta\n'
              '6) Pregled rezervisanih mesta\n'
              '7) Poništavanje rezervisanih mesta\n'
              '8) Pretraga rezervisanih mesta\n'
              '9) Aktivacija statusa člana\n'
              '10) Aktivacija premiuma člana\n'
              '11) Izmena rezervacije mesta\n'
              'xxx) Odjava\n'
              'x) Izlazak iz aplikacije\n')
        odabir = input('Tvoj izbor je: ')
        if odabir == '1':
            pregled_programa(cursor)
        elif odabir == '2':
            pretraga_programa(cursor)
        elif odabir == '3':
            pretragatermina(cursor)
        elif odabir == '4':
            aktivacija_premiuma(cursor)
            connection.commit()
        elif odabir == '5':
            rezervacija_mesta_instruktori(cursor)
            connection.commit()
        elif odabir == '6':
            pregled_rezervacija_instruktor(cursor)
        elif odabir == '7':
            brisanje_rezervacija_instruktor(cursor)
            connection.commit()
        elif odabir == '8':
            pretraga_rez_mesta(cursor)
        elif odabir == '9':
            aktivacija_statusa(cursor)
            connection.commit()
        elif odabir == '10':
            aktivacija_premiuma(cursor)
            connection.commit()
        elif odabir == '11':
            print("Izgleda da nisam uradio izmenu rezervacije")
            pass
        elif odabir == 'xxx':
            log_out()
        elif odabir.lower() == 'x':
            cursor.close()
            connection.close()
            sys.exit()
        else:
            print('NEVAZECI IZBOR')

def meni_korisnik():
    while True:
        print('\nCao, korisnice.')
        print('1) Pregled programa treninga\n'
              '2) Pretraga programa treninga\n'
              '3) Pretraga termina treninga\n'
              '4) Višekriterijumska pretraga programa treninga. \n'
              '5) Rezervacija mesta.\n'
              '6) Pregled rezervisanih mesta\n'
              '7) Poništavanje rezervacije mesta\n'
              'xxx) Odjava\n'
              'x) Izlazak iz aplikacije\n')
        odabir = input('Tvoj odabir: ')
        if odabir == '1':
            pregled_programa(cursor)
        elif odabir == '2':
            pretraga_programa(cursor)
        elif odabir == '3':
            pretragatermina(cursor)
        elif odabir == '4':
            visekriterijumska_pretraga_programa(cursor)
        elif odabir == '5':
            rezervacija_mesta(cursor)
            connection.commit()
        elif odabir == '6':
            pregled_rezervacija_korisnika(cursor)
        elif odabir == '7':
            brisanje_rezervacija_korisnika(cursor)
            connection.commit()
        elif odabir == 'xxx':
            log_out()
        elif odabir.lower() == 'x':
            cursor.close()
            connection.close()
            sys.exit()
        else:
            print('NEVAZECI IZBOR')

def kruziraj_kao_gest():
    while True:
        print('\nTrenutni si tu kao gost.')
        print('1) PRIJAVA\n'
              '2) REGISTRACIJA\n'
              '3) Pregled programa treninga\n'
              '4) Pretraga programa treninga\n'
              '5) Pretraga termina treninga\n'
              'x) Izlazak iz aplikacije\n')
        odabir = input('Tvoj izbor je:: ')
        if odabir == '1':
            log_in()
        elif odabir == '2':
            registracija()
        elif odabir == '3':
            pregled_programa(cursor)
        elif odabir == '4':
            pretraga_programa(cursor)
        elif odabir == '5':
            pretragatermina(cursor)
        elif odabir.lower() == 'x':
            cursor.close()
            connection.close()
            sys.exit()
        else:
            print('NEVAZECI IZBOR')



# END OF MENUES FOR USERS
#
#
#
#


if __name__ == '__main__':
    # restart_baze()
    unosenje_termina()
    meniprvi()

