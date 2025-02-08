from tabulate import tabulate
from datetime import date, timedelta, datetime
import re
import sys


from pregpretiostalo import pregled_programa
from datetime import date


def visekriterijumska_pretraga_programa(cursor):
    print('\nPregled dostupnih programa treninga')
    pregled_programa(cursor)
    
    while True:
        print("\nVišekriterijumska pretraga programa treninga")
        print("Pretrazujete po jednom ili vise kriterijuma. Pritisni 'enter' da preskocis kriterijum i predjes na sledeci.")
        print('Pretražujete listu programa po nazivu, vrsti, trajanju treninga (minimalno trajanje, maksimalno trajanje, navođenje granica), potrebnom uplaćenom paketu.\n')
        query1 = 'SELECT * FROM programi_treninga WHERE 1=1 '
        values = []

        odabir = input('\nAko zelite da se vratite na meni pritisnite sada "x" ili "enter" da nastavite za pretrazivanjem: ').strip()
        if odabir.lower() == 'x':
            break

        while True:
            naziv = input("\nUnesi naziv programa: ").strip()
            if naziv == '':
                break
            elif naziv.isalpha():
                query1 += ' AND naziv_programa = ?'
                values.append(naziv)
                break
            else:
                print('Program sadrzi samo slova.\nUnesite ponovo.\n')

        while True:
            vrsta = input("Unesi vrstu programa: ").strip()
            if vrsta == '':
                break
            elif vrsta.isalpha():
                query1 += ' AND vrsta_programa = ?'
                values.append(vrsta)
                break
            else:
                print('Vrsta programa sadrzi samo slova.\nUnesite ponovo.\n')

        while True:
            min_time = input("Unesi minimalno trajanje treninga: ").strip()
            if min_time == '':
                break
            elif min_time.isdigit():
                query1 += ' AND trajanje >= ?'
                values.append(min_time)
                break
            else:
                print('Unesi samo brojeve.\nUnesi ponovo.\n')

        while True:
            max_time = input("Unesi maksimalno trajanje treninga: ").strip()
            if max_time == '':
                break
            elif max_time.isdigit():
                query1 += ' AND trajanje <= ?'
                values.append(max_time)
                break
            else:
                print('Unesi samo brojeve.\nUnesi ponovo.\n')

        while True:
            time_limit = input("Unesite vremensko ogranicenje u formatu 'min. minuta: max. minuta': ").strip()
            pattern = r"^\d+:\d+$"
            if time_limit == '':
                break
            elif re.match(pattern, time_limit):
                min_vreme, max_vreme = map(int, time_limit.split(":"))
                query1 += ' AND trajanje >= ? AND trajanje <= ?'
                values.extend([min_vreme, max_vreme])
                break
            else:
                print("Nevalja format. Unesite u formatu 'min. minuta: max. minuta', npr. 10:30.")

        while True:
            paket = input("Unesite paket (standard/premium): ").strip()
            if paket == '':
                break
            elif paket.lower() in ['standard', 'premium']:
                query1 += ' AND paket = ?'
                values.append(paket)
                break
            else:
                print('Paket je ili "standard" ili "premium".\nUnesite ponovo.\n')

        cursor.execute(query1, values)
        data = cursor.fetchall()
        if data:
            headers = [desc[0] for desc in cursor.description]
            table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
            print(table)
        else:
            print("Nema bato programa sa tvojim kriteriumima, previse si zahtevan.")


def valusername(cursor):
    cursor.execute('SELECT korisnicko_ime FROM korisnici')
    imenarazna = cursor.fetchall()
    pattern = r'^[a-zA-Z0-9]+$'
    while True:
        username = input('Izaberi username, username sadrzi samo slova (A-Z) i brojeve: ')
        username = username.lower()
        if any(username == ime[0] for ime in imenarazna):
            print('Username vec postoji.')
        elif not re.match(pattern, username):
            print('Izaberi neki drugi, samo slova i brojevi su dozvoljeni.')
        else:
            return username.strip()

def valpassword(cursor):
    while True:
        password = input('Unesi sifru: ')
        if len(password) > 6:
            if any(char.isdigit() for char in password):
                return password
            else:
                print('Sifra treba da sadrzi bar jedan broj.')
        else:
            print('Sifra treba da bude dugacka bar 7 karaktera.')

def reg_instruktora(cursor):
    print('Registracija novih instruktora i admina.')

    username = valusername(cursor)
    password = valpassword(cursor)
    while True:
        name = input('Unesi ime: ')
        if name.strip() == '':
            print('Unesi pravo ime.')
        elif name.isalpha():
            break
        else:
            print('Unesi pravo ime.')

    while True:
        surname = input('Unesi prezime: ')
        if surname.strip() == '':
            print('Unesi pravo prezime.')
        elif name.isalpha():
            break
        else:
            print('Unesi pravo prezime.')

    while True:
        uloga = input('Unesi ulogu ("instruktor" ili "admin"): ')
        if uloga in ['instruktor', 'admin']:
            break
        else:
            print('Nepostojeca uloga.\n'
                  'Unesi ponovo.\n')

    cursor.execute('INSERT INTO korisnici(korisnicko_ime, lozinka, ime, prezime, uloga) VALUES (?, ?, ?, ?, ?)', (username, password, name, surname, uloga))

def aktivacija_statusa(cursor):
    while True:
        print('Aktivacija statusa člana.')
        cursor.execute('SELECT korisnicko_ime, ime, prezime, datum_aktivacije AS "datum aktivacije", datum_isteka AS "datum isteka" FROM korisnici WHERE status_korisnika = "neaktivan" AND uloga = "korisnik"')
        data = cursor.fetchall()
        sva_imena = [informacija[0] for informacija in data]
        if data:
            headers = [desc[0] for desc in cursor.description]
            table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
            print(table)
            while True:
                odabir = input('Unesite username korisnika ili "x" za vracanje na meni: ')
                datetoday = date.today().isoformat()
                exp_date = (date.today() + timedelta(days=30)).isoformat()
                if odabir in sva_imena:
                    cursor.execute('''UPDATE korisnici
                                   SET status_korisnika = "aktivan", paket = "standard", datum_aktivacije = ?, datum_isteka = ?
                                   WHERE korisnicko_ime = ?''', ( datetoday, exp_date, odabir))
                    break
                elif odabir.lower() == 'x':
                    return
                else:
                    print('\nTaj vec ima paket i status na fejsu.\n')

        else:
            print('\nSada svi korisnici imaju i status i paket.\n')
            return



def aktivacija_premiuma(cursor):
    print('Aktivacija premium paketa članstva.')
    cursor.execute('SELECT korisnicko_ime FROM korisnici WHERE status_korisnika = "aktivan"')
    imenarazna = cursor.fetchall()
    datum = date.today().isoformat() 
    za_mesec = (date.today() + timedelta(days=30)).isoformat()
    
    while True:
        username = input('\nUnesi username ili "x" za vracanje na meni: ')
        username = username.lower()
        if username.lower() == 'x':
            break
        elif any(username == ime[0] for ime in imenarazna):
            cursor.execute('UPDATE korisnici SET paket = "premium", datum_aktivacije = ?, datum_isteka = ? WHERE korisnicko_ime = ?', (datum, za_mesec, username))
            print('Uspesno promenjen paket.')
        else:
            print('Nema korisnika sa aktivnim statusom sa tim usernamom.\n'
                  'Unesi ponovo.\n')

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
    naziv_fajla = 'rezervacije_za_datum'
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
            
        prikaz_izvestaja(cursor, data, poruka, naslovi, naziv_fajla)
        
            

def rezervacije_za_datum_termina(cursor):
    naziv_fajla = 'rezervacije_za_datum_termina'
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
            
        prikaz_izvestaja(cursor, data, poruka, naslovi, naziv_fajla)
                    
    

def rezervacije_za_datum_i_instruktora(cursor):
    naziv_fajla = 'rezervacije_za_datum_i_instruktora'
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
        prikaz_izvestaja(cursor, data, poruka, naslovi, naziv_fajla)


def rezervacije_za_dan(cursor):
    naziv_fajla = 'rezervacije_za_dan'
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
    prikaz_izvestaja(cursor, data, poruka, naslovi, naziv_fajla)
        
    
    
def rezervacije_po_instruktoru(cursor):
    naziv_fajla = 'rezervacije_po_instruktoru'
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
    prikaz_izvestaja(cursor, data, poruka, naslovi, naziv_fajla)


def rezervacije_za_premium_ili_standard(cursor):
    naziv_fajla = 'rezervacije_za_premium_ili_standard'
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
    prikaz_izvestaja(cursor, data, poruka, naslovi, naziv_fajla)

def najpopularniji_program(cursor):
    naziv_fajla = 'najpopularniji_program'
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
    prikaz_izvestaja(cursor, data, poruka, naslovi, naziv_fajla)        


def najpopularniji_dan(cursor):
    naziv_fajla = 'najpopularniji_dan'
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
    prikaz_izvestaja(cursor, data, poruka, naslovi, naziv_fajla)


def prikaz_izvestaja(cursor, data, poruka, naslovi, naziv_fajla):
    if data:
        headers = [desc[0] for desc in naslovi]
        table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
        print(table)
    else:
        print(poruka)
    
    while True:
        odabir = input('\nDa li zelis da se izvestaj otstampa, da/ne: ')
        if odabir.lower() == 'da':
            filename = naziv_fajla + '.txt'
            with open(filename, 'w') as fajl:
                for line in data:
                    fajl.write('|'.join(map(str, line)) + '\n')
            break
        elif odabir.lower() == 'ne':
            break
        else:
            print('\nJel hoces ili neces?\n')
    







