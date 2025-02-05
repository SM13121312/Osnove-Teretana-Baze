from tabulate import tabulate
from datetime import date, timedelta, datetime
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
                query1 += ' AND naziv_programa = ?'
                values.append(naziv)
                break
            else:
                print('Program names only consist of letters.\nTry again.\n')

        while True:
            vrsta = input("Enter program type: ").strip()
            if vrsta == '':
                break
            elif vrsta.isalpha():
                query1 += ' AND vrsta_programa = ?'
                values.append(vrsta)
                break
            else:
                print('Program types only consist of letters.\nTry again.\n')

        while True:
            min_time = input("Enter min. time in minutes: ").strip()
            if min_time == '':
                break
            elif min_time.isdigit():
                query1 += ' AND trajanje >= ?'
                values.append(min_time)
                break
            else:
                print('Enter min time in digits.\nTry again.\n')

        while True:
            max_time = input("Enter max. time in minutes: ").strip()
            if max_time == '':
                break
            elif max_time.isdigit():
                query1 += ' AND trajanje <= ?'
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
                query1 += ' AND trajanje >= ? AND trajanje <= ?'
                values.extend([min_vreme, max_vreme])
                break
            else:
                print("Invalid format. Please enter time in the format (min_minutes:max_minutes), e.g., 10:30.")

        while True:
            paket = input("Enter required package (standard/premium): ").strip()
            if paket == '':
                break
            elif paket.lower() in ['standard', 'premium']:
                query1 += ' AND paket = ?'
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

    cursor.execute('INSERT INTO korisnici(korisnicko_ime, lozinka, ime, prezime, uloga) VALUES (?, ?, ?, ?, ?)', (username, password, name, surname, uloga))

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
    print('You are currently activating premium package for user.')
    cursor.execute('SELECT korisnicko_ime FROM korisnici')
    imenarazna = cursor.fetchall()
    while True:
        username = input('\nEnter username or "x" if you want to return to menu: ')
        username = username.lower()
        if username.lower() == 'x':
            break
        elif any(username == ime[0] for ime in imenarazna):
            cursor.execute('UPDATE korisnici SET paket = "premium" WHERE korisnicko_ime = ? AND uloga = "standard"', (username,))
            role_result = cursor.fetchone()

            if role_result and role_result[0] == 'standard':
                cursor.execute('UPDATE korisnici SET paket = "premium" WHERE korisnicko_ime = ?', (username,))
                print(f"Package successfully changed to 'premium' for user: {username}.")
            else:
                print(f"Package not changed. The role for user '{username}' is not 'standard'.")
        else:
            print('No users with that username or you are trying to change package for admin and instructor.\n'
                  'Try again.\n')

def datum_provera():
    while True:
        year = input('Unesi godinu ("yyyy") ili "x" za vracanje na meni: ').strip()
        if year.lower() == 'x':
            return None
        month = input('Unesi mesec ("mm") ili "x" za vracanje na meni: ').strip()
        if month.lower() == 'x':
            return None
        day = input('Unesi dan ("dd") ili "x" za vracanje na meni: ').strip()
        if day.lower() == 'x':
            return None
        
        try:
            year = int(year)
            month = int(month)
            day = int(day)
            datum = date(year, month, day)
            return datum
            
        except ValueError:
            print("Uneli ste neispravan datum.\n")
    

def rezervacije_za_datum(cursor):
    while True:
        print('\nLista rezervacija za odabran datum rezervacije\n')
        datum = datum_provera()
        if datum is None:
            return
        datum_str = datum.strftime('%Y-%m-%d')
        cursor.execute('SELECT * FROM rezervacije WHERE datum = ?', (datum_str,))
        data = cursor.fetchall()
        poruka = ('\nNema liste rezervacija za odabran datum rezervacije\n')
        naslovi = cursor.description
            
        prikaz_izvestaja(cursor, data, poruka, naslovi)
            

def rezervacije_za_datum_termina(cursor):
    while True:
        print('Lista rezervacija za odabran datum termina treninga.\n')
        datum = datum_provera()
        if datum is None:
            return
        datum_str = datum.strftime('%Y-%m-%d')
        cursor.execute('SELECT * FROM termin WHERE datum = ?', (datum_str,))
        data = cursor.fetchall()
        poruka = ('\nNema liste termina za odabran datum.\n')
        naslovi = cursor.description
            
        prikaz_izvestaja(cursor, data, poruka, naslovi)
                    
    

def rezervacije_za_datum_i_instruktora(cursor):
    while True:
        print('Lista rezervacija za odabran datum rezervacije i odabranog instruktora')
        datum = datum_provera()
        if datum is None:
            return
        
        ime = input('\nUnesi ime instruktora ili "x" za vracanje na meni: ')
        if ime.lower() == 'x':
            return
        prezime = input('Unesi prezime instruktora "x" za vracanje na meni: ')
        if prezime == 'x':
            return
        
        ime_prezime = f'{ime} {prezime}'
        cursor.execute('''SELECT termin.sifra_termina, termin.datum, termin.sifra_treninga
                            FROM termin
                            JOIN trening
                                ON termin.sifra_treninga = trening.sifra_treninga
                            JOIN programi_treninga
                                ON trening.naziv_programa = programi_treninga.naziv_programa
                            JOIN rezervacije
                                ON rezervacije.sifra_termina = termin.sifra_termina
                            WHERE instruktor = ? and rezervacije.datum = ?;''', (ime_prezime, datum))
        data = cursor.fetchall()
        naslovi = cursor.description
        poruka = ('Nema to sto ti trazis.')
        prikaz_izvestaja(cursor, data, poruka, naslovi)


def rezervacije_za_dan(cursor):
    print('Ukupan broj rezervacija za izabran dan (u nedelji) održavanja treninga')
    prvi_datum = datetime.today().replace(day=1).strftime('%Y-%m-%d')
    drugi_datum = (datetime.today().replace(day=28) + timedelta(days=4)).replace(day=1).strftime('%Y-%m-%d')

    cursor.execute('''SELECT COUNT(rezervacije.sifra_rezervacije) AS "broj rezervacija", termin.dan, trening.sifra_treninga, trening.naziv_programa
                        FROM rezervacije
                        JOIN termin 
                        ON termin.sifra_termina = rezervacije.sifra_termina
                        JOIN trening 
                        ON trening.sifra_treninga = termin.sifra_treninga
                        WHERE rezervacije.datum >= ? AND rezervacije.datum < ?
                        GROUP BY termin.dan, trening.sifra_treninga, trening.naziv_programa
                        ORDER BY trening.sifra_treninga, rezervacije.sifra_rezervacije DESC''', (prvi_datum, drugi_datum))
    data = cursor.fetchall()
    poruka = 'Nema rezervacija nikojih.'
    naslovi = cursor.description
    prikaz_izvestaja(cursor, data, poruka, naslovi)
        
    
    
def rezervacije_po_instruktoru(cursor):
    print('\nUkupan broj rezervacije po instruktorima u poslednjih 30 dana.\n') 
    pre_mesec = date.today() - timedelta(days=30)
    cursor.execute('''SELECT COUNT(sifra_rezervacije) AS "broj rezervacija", programi_treninga.instruktor
                                FROM rezervacije
                                JOIN termin
                                    ON rezervacije.sifra_termina = termin.sifra_termina
                                JOIN trening
                                    ON trening.sifra_treninga = termin.sifra_treninga
                                JOIN programi_treninga
                                    ON programi_treninga.naziv_programa = trening.naziv_programa
                                WHERE rezervacije.datum >= ?
                                GROUP BY programi_treninga.instruktor
                                HAVING COUNT(sifra_rezervacije) > 0
                                ORDER BY sifra_rezervacije DESC''', (pre_mesec,))
    data = cursor.fetchall()
    poruka = ('Nema to sto ti trazis.')
    naslovi = cursor.description
    prikaz_izvestaja(cursor, data, poruka, naslovi)


def rezervacije_za_premium_ili_standard(cursor):
    print('Ukupan broj rezervacija realizovanih u terminima treninga za koje je potreban premium  ili standard paket članstva ')
    pre_mesec = date.today() - timedelta(days=30)
    cursor.execute('''SELECT COUNT(sifra_rezervacije) AS "broj rezervacija", programi_treninga.paket
                            FROM rezervacije
                            JOIN termin
                                ON rezervacije.sifra_termina = termin.sifra_termina
                            JOIN trening
                                ON trening.sifra_treninga = termin.sifra_treninga
                            JOIN programi_treninga
                                ON programi_treninga.naziv_programa = trening.naziv_programa
                            WHERE rezervacije.datum >= ?
                            GROUP BY programi_treninga.paket
                            HAVING COUNT(sifra_rezervacije) > 0;''', (pre_mesec,))
    data = cursor.fetchall()
    poruka = ('Nema jos nikakvih rezervacija')
    naslovi = cursor.description
    prikaz_izvestaja(cursor, data, poruka, naslovi)

def najpopularniji_program(cursor):
    print('3 najpopularnija programa treninga po broju rezervacija izvršenih u poslednjih godinu dana.')
    pre_godinu = date.today() - timedelta(days=365)
    cursor.execute('''SELECT COUNT(sifra_rezervacije) AS "broj rezervacija", programi_treninga.naziv_programa
                        FROM rezervacije
                        JOIN termin
                            ON rezervacije.sifra_termina = termin.sifra_termina
                        JOIN trening
                            ON trening.sifra_treninga = termin.sifra_treninga
                        JOIN programi_treninga
                            ON programi_treninga.naziv_programa = trening.naziv_programa
                        WHERE rezervacije.datum >= ?
                        GROUP BY programi_treninga.naziv_programa
                        LIMIT 3;''', (pre_godinu,))
    data = cursor.fetchall()
    poruka = 'Brat je nesto opako zezno u sistemu.'
    naslovi = cursor.description
    prikaz_izvestaja(cursor, data, poruka, naslovi)        


def najpopularniji_dan(cursor):
    print('Najpopularniji dan u nedelji.')
    cursor.execute('''SELECT COUNT(sifra_rezervacije) AS "broj rezervacija", termin.dan
                        FROM rezervacije
                        JOIN termin
                        ON rezervacije.sifra_termina = termin.sifra_termina
                        GROUP BY termin.dan
                        ORDER BY COUNT(sifra_rezervacije) DESC''')
    data = cursor.fetchall()
    poruka = 'Nema bajo rezervacija nikojih.'
    naslovi = cursor.description
    prikaz_izvestaja(cursor, data, poruka, naslovi)


def prikaz_izvestaja(cursor, data, poruka, naslovi):
    if data:
        headers = [desc[0] for desc in naslovi]
        table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
        print(table)
    else:
        print(poruka)
    







