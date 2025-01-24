import os
import sys
from datetime import date, timedelta
from pregpretiostalo import pregled_programa, pretraga_programa, pretragatermina, prikaz_pretrage_termina2, unos_izmena_brisanje_programa, pregled_treninga, unos_izmena_brisanje_treninga
from sveostalo1 import visekriterijumska_pretraga_programa, reg_instruktora, aktivacija_premiuma, aktivacija_statusa
from rezervacijeiostalo import rezervacija_mesta, pregled_rezervacija_korisnika, brisanje_rezervacija_korisnika, \
    rezervacija_mesta_instruktori, brisanje_rezervacija_instruktor, pregled_rezervacija_instruktor, pretraga_rez_mesta
import shared
from tabulate import tabulate
import mysql.connector
import re
import os
import sqlite3


connection = sqlite3.connect('projekatdva.db')
cursor = connection.cursor()

def restart_baze():
    with open('Tabele.sql', 'r', encoding = 'utf-8') as file:
        sql_fajl = file.read()

    milan = sql_fajl.split(';')
    for i in range(0, len(milan)):
        cursor.execute(milan[i])

def meniprvi():
    print('\n-----FIRST MENU-----\n')
    print('CHOOSE:\n'
          'Press 1 to register.\n'
          'Press 2 to log in.\n'
          'Press 3 to search as guest.\n'
          'For exit press "x".'
          )

    while True:
        odabir = input('Your choice is: ')
        if odabir == '1':
            registracija()
        elif odabir == '2':
            log_in()
        elif odabir == '3':
            kruziraj_kao_gest()
        elif odabir.lower() == 'x':
            print('GOODBYE')
            cursor.close()
            connection.close()
            sys.exit()
        else:
            print('INVALID CHOICE')



def registracija():
    print('\n\nPLEASE ENTER YOUR INFORMATION BELOW')
    username = valusername()
    password = valpassword()

    while True:
        name = input('Enter your name: ')
        if name.strip() == '':
            print('Enter your real name.')
        elif name.isalpha():
            break
        else:
            print('Enter your real name.')

    while True:
        surname = input('Enter your surname: ')
        if surname.strip() == '':
            print('Enter your real surname.')
        elif surname.isalpha():
            break
        else:
            print('Enter your real surname.')

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
    print(imenarazna)
    pattern = r'^[a-zA-Z0-9]+$'
    while True:
        username = input('Enter username, username contains only letters(A-Z) and digits: ')
        username = username.lower()
        if username in imenarazna:
            print('Username already exists.')
        elif not re.match(pattern, username):
            print('Invalid username! Only letters and digits are allowed.')
        else:
            return username.strip()



def valpassword():
    while True:
        password = input('Enter your password: ')
        if len(password) > 6:
            if any(char.isdigit() for char in password):
                return password
            else:
                print('Password should contain at least one digit.')
        else:
            print('Password should contain more than 6 chars.')


#
#
#
#
# MENUES FOR USERS

def log_in():
    username = input('ENTER YOUR USERNAME: ')
    cursor.execute('SELECT COUNT(korisnicko_ime) FROM korisnici WHERE korisnicko_ime = ?', (username,))
    brojac = cursor.fetchone()
    if brojac[0] > 0:
        password = input('ENTER YOUR PASSWORD: ')
        cursor.execute('SELECT lozinka FROM korisnici WHERE korisnicko_ime = ?', (username,))
        sifra = cursor.fetchone()
        if password == sifra[0]:
            cursor.execute('SELECT uloga, status, paket, ime, prezime, datum_aktivacije, datum_isteka FROM korisnici WHERE korisnicko_ime = ?', (username,))
            role, status, package, name, surname, act_date, exp_date = cursor.fetchone()
            shared.current_user = [{'username': username, 'role': role, 'status' : status, 'package' : package, 'name' : name, 'surname' : surname, 'act_date' : act_date, 'exp_date' : exp_date}]

            if role == 'admin':
                meni_admin()
            elif role == 'instruktor':
                meni_instruktor()
            elif role == 'korisnik':
                meni_korisnik()
            else:
                print('!!!THERE IS MISTAKE IN DATABASE!!!')
        else:
            print('Wrong password!!!\n')
    else:
        print('NO USER WITH THAT USERNAME')
        log_in()

def log_out():
    if shared.current_user:
        print('GOODBYE')
        current_user = []
        meniprvi()
    else:
        print('No user is currently logged in.')



def meni_admin():
    while True:
        print('\nCurrently you are here as admin.')
        print('If you want to see program overview enter 1.\n'
              'If you want to search program enter 2.\n'
              'If you want to search for date and training time enter 3.\n'
              'If you want to add new, change or delete old training programs enter 4.\n'
              'If you want to add new, change or delete old trainings enter 5.\n'
              'If you want to register instructor or admin enter 6.\n'
              'If you want to log out enter "xxx".\n'
              'If you want to exit app enter "x".\n')
        odabir = input('Your choice is: ')
        if odabir == '1':
            pregled_programa(cursor)
        elif odabir == '2':
            pretraga_programa(cursor)
        elif odabir == '3':
            pretragatermina(cursor)
        elif odabir == '4':
            unos_izmena_brisanje_programa(cursor)
        elif odabir == '5':
            unos_izmena_brisanje_treninga(cursor)
        elif odabir == '6':
            reg_instruktora(cursor)
            connection.commit()
        elif odabir == 'xxx':
            log_out()
        elif odabir.lower() == 'x':
            cursor.close()
            connection.close()
            sys.exit()
        else:
            print('INVALID CHOICE')

def meni_instruktor():
    while True:
        connection.commit()
        print('\nCurrently you are here as an instructor.')
        print('If you want to see program overview enter 1.\n'
              'If you want to search program enter 2.\n'
              'If you want to search for date and training time enter 3.\n'
              'If you want to activate premium package for user enter 4.\n'
              'If you want to reserve place for training session enter 5.\n'
              'If you want to do overview of your reservations enter 6.\n'
              'If you want to delete one of your reservation enter 7.\n'
              'If you want to search for reserved seats enter 8.\n'
              'If you want to change users status enter 9.\n'
              'If you want to log out enter "xxx".\n'
              'If you want to exit app enter "x".\n')
        odabir = input('Your choice is: ')
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
        elif odabir == 'xxx':
            log_out()
        elif odabir.lower() == 'x':
            cursor.close()
            connection.close()
            sys.exit()
        else:
            print('INVALID CHOICE')

def meni_korisnik():
    while True:
        print('\nCurrently you are here as an user.')
        print('If you want to see program overview enter 1.\n'
              'If you want to search program enter 2.\n'
              'If you want to search for date and training time enter 3.\n'
              'If you want to multi_criteria search for programs enter 4.\n'
              'If you want reserve seat for training session enter 5.\n'
              'If you want to see all your reservations enter 6.\n'
              'If you want to delete reservation enter 7.\n'
              'If you want to log out enter "xxx".\n'
              'If you want to exit app enter "x".\n')
        odabir = input('Your choice is: ')
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
            print('INVALID CHOICE')

def kruziraj_kao_gest():
    while True:
        print('\nCurrently you are here as a guest.')
        print('If you want to log in enter 1.\n'
              'If you want to register enter 2\n'
              'If you want to see program overview enter 3.\n'
              'If you want to search program enter 4.\n'
              'If you want to search for date and training time enter 5.\n'
              'If you want to exit app enter "x".\n')
        odabir = input('Your choice is: ')
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
            print('INVALID CHOICE')



# END OF MENUES FOR USERS
#
#
#
#



if __name__ == '__main__':
    meniprvi()

