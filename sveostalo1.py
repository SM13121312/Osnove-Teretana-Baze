from tabulate import tabulate
import re
import sys


from pregpretiostalo import pregled_programa
from datetime import date


def visekriterijumska_pretraga_programa(cursor):
    print('PROGRAM OVERVIEW')
    pregled_programa(cursor)
    print('\nOVERVIEW OF TRAINING PROGRAMS')
    print("\nMulti-Criteria Search of Training Programs")
    print("You can search by one or more criteria. Press enter if you don't want to search by that criterion and move to another one.")
    print('You can search programs by name, type, duration (min. time, max. time, time limit), and required package\n')

    while True:
        query1 = 'SELECT * FROM programi_treninga WHERE 1=1 '
        values = []

        odabir = input('\nIf you want to return to the menu, enter "x" or press Enter to continue the search: ')
        if odabir.lower() == 'x':
            break

        while True:
            naziv = input("\nEnter program name: ").strip()
            if naziv == '':
                break
            elif naziv.isalpha():
                query1 += ' AND naziv_programa = %s'
                values.append(naziv)
                break
            else:
                print('Program names only consist of letters.\nTry again.\n')

        while True:
            vrsta = input("Enter program type: ").strip()
            if vrsta == '':
                break
            elif vrsta.isalpha():
                query1 += ' AND vrsta_programa = %s'
                values.append(vrsta)
                break
            else:
                print('Program types only consist of letters.\nTry again.\n')

        while True:
            min_time = input("Enter min. time in minutes: ").strip()
            if min_time == '':
                break
            elif min_time.isdigit():
                query1 += ' AND trajanje >= %s'
                values.append(min_time)
                break
            else:
                print('Enter min time in digits.\nTry again.\n')

        while True:
            max_time = input("Enter max. time in minutes: ").strip()
            if max_time == '':
                break
            elif max_time.isdigit():
                query1 += ' AND trajanje <= %s'
                values.append(max_time)
                break
            else:
                print('Enter max time in digits.\nTry again.\n')

        while True:
            time_limit = input("Enter time limit in the format (min_minutes:max_minutes): ").strip()
            pattern = r"^\d+:\d+$"
            if time_limit == '':
                break
            elif re.match(pattern, time_limit):
                min_vreme, max_vreme = map(int, time_limit.split(":"))
                query1 += ' AND trajanje >= %s AND trajanje <= %s'
                values.extend([min_vreme, max_vreme])
                break
            else:
                print("Invalid format. Please enter time in the format (min_minutes:max_minutes), e.g., 10:30.")

        while True:
            paket = input("Enter required package (standard/premium): ").strip()
            if paket == '':
                break
            elif paket.lower() in ['standard', 'premium']:
                query1 += ' AND paket = %s'
                values.append(paket)
                break
            else:
                print('Package should be "standard" or "premium".\nTry again.\n')

        cursor.execute(query1, values)
        data = cursor.fetchall()
        if data:
            headers = [desc[0] for desc in cursor.description]
            table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
            print(table)
        else:
            print("No programs found matching your criteria.")


def valusername(cursor):
    cursor.execute('SELECT korisnicko_ime FROM korisnici')
    imenarazna = cursor.fetchall()
    pattern = r'^[a-zA-Z0-9]+$'
    while True:
        username = input('Enter username, username contains only letters(A-Z) and digits: ')
        username = username.lower()
        if any(username == ime[0] for ime in imenarazna):
            print('Username already exists.')
        elif not re.match(pattern, username):
            print('Invalid username! Only letters and digits are allowed.')
        else:
            return username.strip()

def valpassword(cursor):
    while True:
        password = input('Enter your password: ')
        if len(password) > 6:
            if any(char.isdigit() for char in password):
                return password
            else:
                print('Password should contain at least one digit.')
        else:
            print('Password should contain more than 6 chars.')

def reg_instruktora(cursor):
    print('NEW INSTRUCTOR REGISTRATION AND ADMINS')

    username = valusername(cursor)
    password = valpassword(cursor)
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
        elif name.isalpha():
            break
        else:
            print('Enter your real surname.')

    while True:
        uloga = input('Enter role ("instruktor" or "admin"): ')
        if uloga in ['instruktor', 'admin']:
            break
        else:
            print('Invalid choice.\n'
                  'Try again.\n')

    cursor.execute('INSERT INTO korisnici(korisnicko_ime, lozinka, ime, prezime, uloga) VALUES (%s, %s, %s, %s, %s)', (username, password, name, surname, uloga))

def aktivacija_statusa(cursor):
    while True:
        print('You are currently activating status for user.')
        cursor.execute('SELECT korisnicko_ime, ime, prezime, datum_aktivacije AS "datum aktivacije", datum_isteka AS "datum isteka" FROM korisnici WHERE status = "neaktivan" AND uloga = "korisnik"')
        data = cursor.fetchall()
        sva_imena = [informacija[0] for informacija in data]
        print(sva_imena)
        if data:
            headers = [desc[0] for desc in cursor.description]
            table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
            print(table)

            odabir = input('Enter username of user you want to activate status or enter "x" to return to menu: ')
            break

        else:
            print('\nTHERE IS NO USER WHO IS NOT ACTIVE.\n')
            return



def aktivacija_premiuma(cursor):
    print('You are currently activating premium package fro user.')
    cursor.execute('SELECT korisnicko_ime FROM korisnici')
    imenarazna = cursor.fetchall()
    while True:
        username = input('\nEnter username or "x" if you want to return to menu: ')
        username = username.lower()
        if username.lower() == 'x':
            break
        elif any(username == ime[0] for ime in imenarazna):
            cursor.execute('UPDATE korisnici SET paket = "premium" WHERE korisnicko_ime = %s AND uloga = "standard"', (username,))
            role_result = cursor.fetchone()

            if role_result and role_result[0] == 'standard':
                cursor.execute('UPDATE korisnici SET paket = "premium" WHERE korisnicko_ime = %s', (username,))
                print(f"Package successfully changed to 'premium' for user: {username}.")
            else:
                print(f"Package not changed. The role for user '{username}' is not 'standard'.")
        else:
            print('No users with that username or you are trying to change package for admin and instructor.\n'
                  'Try again.\n')

