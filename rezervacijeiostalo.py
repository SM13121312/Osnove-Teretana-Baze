from tabulate import tabulate
from datetime import date
import random
import shared
from pregpretiostalo import pretragatermina



def pregled_termina(cursor):
    print('\nTRAINING SESSION OVERVIEW\n')
    cursor.execute('SELECT * FROM termin')
    data = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]
    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)

def rezervacija_mesta(cursor):
    if shared.current_user[0]['status'] == 'neaktivan':
        print('\n!!!!!Your profile is currently inactive. Pay your membership so you can reserve seats for trainings.!!!!!\n')
        return
    while True:
        print('You can reserve directly by entering training session code or by searching training sessions.\n'
              'If you want to enter code directly enter 1.\n'
              'If you want to search for session enter 2.\n'
              'To get back to your menu enter "x".\n')
        odabir = input('Enter your choice: ')
        if odabir == '1':
            pregled_termina(cursor)
            print('You are currently reserving session directly by entering session code.')
            while True:
                sifra = input('Enter session code: ')
                if sifra == 'x':
                    return

                cursor.execute('''SELECT programi_treninga.paket
                                  FROM trening
                                  JOIN programi_treninga
                                  ON trening.naziv_programa = programi_treninga.naziv_programa
                                  JOIN termin
                                  ON trening.sifra_treninga = termin.sifra_treninga
                                  WHERE termin.sifra_termina = ?''', (sifra,))

                paket = cursor.fetchone()
                if paket is None:
                    print('\nEnter one of existing session codes.\n'
                          'Try again.\n')
                    continue
                else:
                    paket = paket[0]
                if not paket:
                    print('No session with that code.\n'
                          'Try again.\n')
                elif shared.current_user[0]['package'] == 'premium':
                    print('Bravo majmune imas premium')
                    odabir_mesta(cursor, sifra)
                elif shared.current_user[0]['package'] == 'standard' and paket == 'premium':
                    print('Cant access this session due to not having premium package.\n'
                          'Try another session.\n')
                elif shared.current_user[0]['package'] == 'standard' and paket == 'standard':
                    print('Bravo sirotinjj imas stadnard.\n')
                    odabir_mesta(cursor, sifra)
                else:
                    print('No session with that code.\n'
                          'Try again.\n')

        elif odabir == '2':
            pretragatermina(cursor)
            #
            #
            #
            #
            #
            #NATAVITI!!!!!!!!!!!!
            #
            #
            #
            #
            #

        elif odabir == 'x':
            return
        else:
            print('Invalid choice.\n'
                  'Try again.\n')

def odabir_mesta(cursor, sifra):
    cursor.execute('''SELECT sale.broj_redova, sale.oznaka_mesta 
                      FROM trening
                      JOIN sale ON trening.sifra_sale = sale.sifra_sale
                      JOIN termin ON trening.sifra_treninga = termin.sifra_treninga
                      WHERE termin.sifra_termina = ?''', (sifra,))
    data = cursor.fetchone()
    broj_redova, oznaka_mesta = data

    cursor.execute('SELECT oznaka_reda_i_mesta FROM rezervacije WHERE sifra_termina = ?', (sifra,))
    rezervisano = [rez[0] for rez in cursor.fetchall()]

    sva_mesta_slobodna = []
    table_rows = []
    for red in range(1, broj_redova + 1):
        row = [f"Red {red}"]
        for slovo in oznaka_mesta:
            seat_id = f"{red}{slovo}"
            if seat_id in rezervisano:
                row.append("X")
            else:
                row.append(slovo)
                sva_mesta_slobodna.append(seat_id)
        table_rows.append(row)

    table = tabulate(table_rows, tablefmt="fancy_grid", stralign="center")
    print(table)
    while True:
        biracko_mesto = input('Enter free place in hall: ')
        if biracko_mesto in sva_mesta_slobodna:
            break
        else:
            print('Plese choose one of free places.\n'
                  'Try again.\n')

    cursor.execute('SELECT sifra_rezervacije FROM rezervacije')
    sifre_rezervacija = [sifra_rezervacije[0] for sifra_rezervacije in cursor.fetchall()]
    while True:
        rdm_sifra = random.randint(1, 2000)
        if rdm_sifra not in sifre_rezervacija:
            break
    korisnicko_ime = shared.current_user[0]['username']
    datum = date.today()

    cursor.execute('INSERT INTO rezervacije VALUES (?, ?, ?, ?, ?)', (rdm_sifra, korisnicko_ime, sifra, biracko_mesto, datum))

def pregled_rezervacija_korisnika(cursor):
    print('OVERVIEW OF YOUR RESERVATIONS')
    username = shared.current_user[0]['username']
    cursor.execute('''SELECT rezervacije.sifra_rezervacije, rezervacije.sifra_termina, termin.datum, trening.naziv_programa, trening.vreme_pocetka, trening.vreme_kraja 
                        FROM rezervacije
                        JOIN termin
                        ON rezervacije.sifra_termina = termin.sifra_termina
                        JOIN trening
                        ON trening.sifra_treninga = termin.sifra_treninga
                        WHERE rezervacije.korisnicko_ime = ?''', (username,))
    data = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]
    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)


def brisanje_rezervacija_korisnika(cursor):
    pregled_rezervacija_korisnika(cursor)
    print('\nDELETE YOUR RESERVATIONS\n')
    print('Enter reservation code from reservation you want to delete.')
    while True:
        cursor.execute('SELECT sifra_rezervacije FROM rezervacije WHERE sifra_rezervacije < 1000')
        sifre = [sifra[0] for sifra in cursor.fetchall()]
        odabir = input('Enter reservation code or enter "x" to return to menu: ')
        if odabir.lower() == 'x':
            return
        elif any(eval(odabir) == sifra for sifra in sifre):
            cursor.execute('DELETE FROM rezervacije WHERE sifra_rezervacije = ?', (odabir,))
        else:
            print('Enter code from reservation which exists.\n'
                  'Try again.\n')

def rezervacija_mesta_instruktori(cursor):
    print('\nTRAINING SESSION OVERVIEW\n')
    ime_prezime = f'{shared.current_user[0]["name"]} {shared.current_user[0]["surname"]}'
    cursor.execute('''SELECT termin.sifra_termina, programi_treninga.naziv_programa, vrsta_programa, sifra_sale, datum, vreme_pocetka, vreme_kraja, paket
                            FROM termin
                            JOIN trening
                            ON trening.sifra_treninga = termin.sifra_treninga
                            JOIN programi_treninga
                            ON trening.naziv_programa = programi_treninga.naziv_programa
                            WHERE programi_treninga.instruktor = ?''', (ime_prezime,))
    data = cursor.fetchall()
    sifre_termina = [informacija[0] for informacija in data]

    if data:
        headers = [desc[0] for desc in cursor.description]
        table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
        print(table)
    else:
        print('\nYou are instructor without job.\n')
        return

    print('You can reserve directly by entering training session code or by searching training sessions.\n'
          'If you want to enter code directly enter 1.\n'
          'If you want to search for session enter 2.\n'
          'To get back to your menu enter "x".\n')
    while True:
        odabir = input('Enter your choice: ')
        if odabir == '1':
            while True:
                print('You are currently reserving session directly by entering session code.')
                while True:
                    sifra = input('Enter session code or enter "x" to return to menu: ')
                    if sifra in sifre_termina:
                        break
                    elif sifra.lower() == 'x':
                        return
                    else:
                        print('Choose one of existing session codes.\n')
                while True:
                    cursor.execute('SELECT korisnicko_ime FROM korisnici WHERE uloga = "korisnik"')
                    svi_usernames = [user[0] for user in cursor.fetchall()]
                    username = input('Enter username of your candidate or enter "x" to return to menu: ')
                    if username in svi_usernames:
                        break
                    elif username == 'x':
                        return
                    else:
                        print('Choose one of existing users.\n')

                cursor.execute('''SELECT programi_treninga.paket
                                    FROM trening
                                    JOIN programi_treninga
                                    ON trening.naziv_programa = programi_treninga.naziv_programa
                                    JOIN termin
                                    ON trening.sifra_treninga = termin.sifra_treninga
                                    WHERE termin.sifra_termina = ?''', (sifra,))

                paket_potreban = cursor.fetchone()[0]

                cursor.execute('SELECT status, paket FROM korisnici WHERE korisnicko_ime = ?', (username,))
                status, paket = cursor.fetchone()
                if status == 'neaktivan':
                    print(f'\n{username} isnt activ and cant reserve session.\n')
                elif paket == 'premium':
                    odabir_mesta_instruktor(cursor, sifra, username)
                elif paket == 'standard' and paket_potreban == 'premium':
                    print('Your candidate doesnt have needed package, he only has standard.\n')
                elif paket == 'standard' and paket_potreban == 'standard':
                    odabir_mesta_instruktor(cursor, sifra, username)
                else:
                    print('Invalid choice.\n'
                          'Try again.\n')


        elif odabir == '2':
            pretragatermina(cursor)
            #
            #
            #
            #
            #
            # NAsTAVITI!!!!!!!!!!!!
            #
            #
            #
            #
            #

        elif odabir == 'x':
            return
        else:
            print('Invalid choice.\n'
                  'Try again.\n')

def odabir_mesta_instruktor(cursor, sifra, username):
    cursor.execute('''SELECT sale.broj_redova, sale.oznaka_mesta 
                              FROM trening
                              JOIN sale ON trening.sifra_sale = sale.sifra_sale
                              JOIN termin ON trening.sifra_treninga = termin.sifra_treninga
                              WHERE termin.sifra_termina = ?''', (sifra,))
    data = cursor.fetchone()
    broj_redova, oznaka_mesta = data

    cursor.execute('SELECT oznaka_reda_i_mesta FROM rezervacije WHERE sifra_termina = ?', (sifra,))
    rezervisano = [rezer[0] for rezer in cursor.fetchall()]

    oznaka_mesta = list(oznaka_mesta)
    slobodna_mesta = []
    table_rows = []
    for red in range(1, broj_redova + 1):
        zaprebacivanje = [f'Red {red}']
        for slovo in oznaka_mesta:
            if f'{red}{slovo}' in rezervisano:
                zaprebacivanje.append('X')
            else:
                slobodna_mesta.append(f'{red}{slovo}')
                zaprebacivanje.append(slovo)
        table_rows.append(zaprebacivanje)

    table = tabulate(table_rows, tablefmt='fancy_grid')
    print(table)

    while True:
        biracko_mesto = input('Enter seat you want to reserve: ')
        if biracko_mesto in slobodna_mesta:
            break
        else:
            print('Choose one of free seats.\n'
                  'Try again.\n')

    cursor.execute('SELECT sifra_rezervacije FROM rezervacije')
    sifre_rezervacija = [sifra_rezervacije[0] for sifra_rezervacije in cursor.fetchall()]
    while True:
        rdm_sifra = random.randint(1, 2000)
        if rdm_sifra not in sifre_rezervacija:
            break

    datum = date.today()

    cursor.execute('INSERT INTO rezervacije VALUES (?, ?, ?, ?, ?)', (rdm_sifra, username, sifra, biracko_mesto, datum))

def pregled_rezervacija_instruktor(cursor):
    print('OVERVIEW OF YOUR RESERVATIONS')
    ime_prezime = f'{shared.current_user[0]["name"]} {shared.current_user[0]["surname"]}'
    print(ime_prezime)
    cursor.execute('''SELECT rezervacije.sifra_rezervacije, rezervacije.sifra_termina, termin.datum, trening.naziv_programa, trening.vreme_pocetka, trening.vreme_kraja 
                        FROM rezervacije
                        JOIN termin
                        ON rezervacije.sifra_termina = termin.sifra_termina
                        JOIN trening
                        ON trening.sifra_treninga = termin.sifra_treninga
                        JOIN programi_treninga
                        ON programi_treninga.naziv_programa = trening.naziv_programa
                        WHERE programi_treninga.instruktor = ?''', (ime_prezime,))
    data = cursor.fetchall()
    if data:
        headers = [desc[0] for desc in cursor.description]
        table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
        print(table)
    else:
        print('\nYou have no reservations.\n')

def brisanje_rezervacija_instruktor(cursor):
    print('OVERVIEW OF YOUR RESERVATIONS')
    ime_prezime = f'{shared.current_user[0]["name"]} {shared.current_user[0]["surname"]}'
    cursor.execute('''SELECT rezervacije.sifra_rezervacije, rezervacije.sifra_termina, termin.datum, trening.naziv_programa, trening.vreme_pocetka, trening.vreme_kraja 
                            FROM rezervacije
                            JOIN termin
                            ON rezervacije.sifra_termina = termin.sifra_termina
                            JOIN trening
                            ON trening.sifra_treninga = termin.sifra_treninga
                            JOIN programi_treninga
                            ON programi_treninga.naziv_programa = trening.naziv_programa
                            WHERE programi_treninga.instruktor = ?''', (ime_prezime,))
    data = cursor.fetchall()
    if data:
        headers = [desc[0] for desc in cursor.description]
        table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
        print(table)
    else:
        print('\nYou have no reservations.\n')
        return

    instruktorove_rez = [informacije[0] for informacije in data]

    print('\nDELETE YOUR RESERVATIONS\n')
    print('Enter reservation code from reservation you want to delete.')
    while True:
        odabir = input('\nEnter reservation code or enter "x" to return to menu: ')
        if odabir.lower() == 'x':
            return
        elif eval(odabir) in instruktorove_rez:
            cursor.execute('DELETE FROM rezervacije WHERE sifra_rezervacije = ?', (odabir,))
        else:
            print('Enter code from reservation which exists.\n'
                  'Try again.\n')

def pretraga_rez_mesta(cursor):


    print('\nYou can search by training code, name or surname of users, date of training, start time, end time.\n')
    print('To search by training code enter 1.\n'
          '             name enter 2.\n'
          '             surname enter 3.\n'
          '             date of training enter 4.\n'
          '             start time enter 5.\n'
          '             end time enter 6.\n'
          '             to get back to menu enter "x".\n')

    while True:
        odabir = input('Enter how you would like to search reservations: ')
        if odabir == '1':
            print('You are searching by training code.')
            word = eval(input('Enter training code: '))
            nastavak = ' AND trening.sifra_treninga = ?'
            pretraga_rez_mesta_nastavak(cursor, nastavak, word)

        elif odabir == '2':
            print('You are searching by name of the user.')
            word = input('Enter name of user: ')
            nastavak = 'AND korisnici.ime = ?'
            pretraga_rez_mesta_nastavak(cursor, nastavak, word)

        elif odabir == '3':
            print('You are searching by surname of the user.')
            word = input('Enter surname of user: ')
            nastavak = 'AND korisnici.prezime = ?'
            pretraga_rez_mesta_nastavak(cursor, nastavak, word)

        elif odabir == '4':
            print('You are searching by date of training.')
            word = input('Enter date of training in format (yyyy-mm-dd): ')
            nastavak = 'AND termin.datum = ?'
            pretraga_rez_mesta_nastavak(cursor, nastavak, word)

        elif odabir == '5':
            print('You are searching by start time.')
            word = input('Enter start time in format (hh:mm): ')
            nastavak = 'AND trening.vreme_pocetka = ?'
            pretraga_rez_mesta_nastavak(cursor, nastavak, word)

        elif odabir == '6':
            print('You are searching by end time.')
            word = input('Enter end time in format (hh:mm): ')
            nastavak = 'AND trening.vreme_kraja = ?'
            pretraga_rez_mesta_nastavak(cursor, nastavak, word)

        elif odabir.lower() == 'x':
            return
        else:
            print('Invalid choice.\n'
                  'Try again.\n')

def pretraga_rez_mesta_nastavak(cursor, nastavak, word):
    ime_prezime = f'{shared.current_user[0]["name"]} {shared.current_user[0]["surname"]}'
    query = '''SELECT rezervacije.sifra_rezervacije, termin.sifra_termina, termin.datum, trening.naziv_programa, trening.vreme_pocetka, trening.vreme_kraja, rezervacije.datum AS "datum rezervacije"
                    FROM rezervacije
                    JOIN korisnici
                    ON korisnici.korisnicko_ime = rezervacije.korisnicko_ime
                    JOIN termin 
                    ON termin.sifra_termina = rezervacije.sifra_termina
                    JOIN trening 
                    ON trening.sifra_treninga = termin.sifra_treninga
                    JOIN programi_treninga
                    ON trening.naziv_programa = programi_treninga.naziv_programa 
                    WHERE programi_treninga.instruktor = ? '''

    cursor.execute(query + nastavak, (ime_prezime,word))
    data = cursor.fetchall()
    if data:
        headers = [desc[0] for desc in cursor.description]
        table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
        print(table)
    else:
        print('\nThere is no reservation with that information.\n')





