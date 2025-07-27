from multiprocessing import connection
from tabulate import tabulate
from datetime import date, datetime
import random
import shared
from pregpretiostalo import pretragatermina



def pregled_termina(cursor):
    print('\nPregled termina treninga\n')
    
    danasnji_datum = date.today()

    trenutno_vreme = datetime.now().strftime("%H:%M")

    cursor.execute('''
        SELECT * 
        FROM termin
        JOIN trening ON termin.sifra_treninga = trening.sifra_treninga
        WHERE termin.datum >= ? AND trening.vreme_pocetka > ?
    ''', (danasnji_datum, trenutno_vreme))
    data = cursor.fetchall()
    
    if not data:
        print("Nema termina koji ti trebaju")
        return
    
    headers = [desc[0] for desc in cursor.description]
    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)

def rezervacija_mesta(cursor):
    if shared.current_user[0]['status'] == 'neaktivan':
        print('\n!!!!!Plati clanarinu pa se onda igraj.!!!!!\n')
        return
    while True:
        print('Mozes rezervisati direktnim unosom sifre termina ili prvo hoces da istrazis termine: \n'
              '1) Direktan unos\n'
              '2) Prvo istrazi termine\n'
              'x) Za povratak na meni\n')
        odabir = input('Tvoj izbor: ')
        if odabir == '1':
            pregled_termina(cursor)
            print('Direktan unos')
            while True:
                sifra = input('Unesi sifru: ')
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
                    print('\nUnesi neki od postojecih.\n'
                          'Pokusaj ponovo.\n')
                    continue
                else:
                    paket = paket[0]
                if not paket:
                    print('Nema termina sa tom sifrom.\n'
                          'Pokusaj ponovo.\n')
                elif shared.current_user[0]['package'] == 'premium':
                    print('Bravo imas premium')
                    odabir_mesta(cursor, sifra)
                elif shared.current_user[0]['package'] == 'standard' and paket == 'premium':
                    print('Nemas premium koji treba za trening, idi kupi premium.\n'
                          'Probaj neki drugi termin.\n')
                elif shared.current_user[0]['package'] == 'standard' and paket == 'standard':
                    print('Imas standard, bravo.\n')
                    odabir_mesta(cursor, sifra)
                else:
                    print('Pokusaj ponovo.\n')

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
            print('Nevazeci izbor.\n'
                  'Ponovo pokusaj.\n')

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
        biracko_mesto = input('Unesi slobodno mest u fromatu BROJslovo "1A", "3B", "6J": ')
        if biracko_mesto in sva_mesta_slobodna:
            break
        else:
            print('Izaberi slobodno mesto.\n'
                  'Pokusaj ponovo.\n')

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
    print('Pregled rezervisanih mesta')
    username = shared.current_user[0]['username']
    cursor.execute('''SELECT rezervacije.sifra_rezervacije, rezervacije.sifra_termina, termin.datum, trening.naziv_programa, trening.vreme_pocetka, trening.vreme_kraja 
                        FROM rezervacije
                        JOIN termin
                        ON rezervacije.sifra_termina = termin.sifra_termina
                        JOIN trening
                        ON trening.sifra_treninga = termin.sifra_treninga
                        WHERE rezervacije.korisnicko_ime = ?''', (username,))
    data = cursor.fetchall()
    if data == []:
        print("idi prvo pa rezervisi nesto")
        return
    headers = [desc[0] for desc in cursor.description]
    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)


def brisanje_rezervacija_korisnika(cursor):
    username = shared.current_user[0]['username']
    while True:
        pregled_rezervacija_korisnika(cursor)
        print('\nPoništavanje rezervacije mesta\n')
        cursor.execute('SELECT sifra_rezervacije FROM rezervacije WHERE korisnicko_ime = ?', (username,))
        sifre = [sifra[0] for sifra in cursor.fetchall()]
        
        if len(sifre) > 0:
            odabir = input('Unesi sifru rezervacije ili "x" za povratak na meni: ').strip()
            if odabir.lower() == 'x':
                return
            elif int(odabir) in sifre:
                cursor.execute('DELETE FROM rezervacije WHERE sifra_rezervacije = ?', (odabir,))
                print('Rezervacija obrisana.')
            else:
                print('Unesi ispravnu sifru rezervacije.\n'
                    'Unesi ponovo.\n')
        else: 
            print("Nemas sta da obrises")
            break

def rezervacija_mesta_instruktori(cursor):
    print('\nRezervacija mesta\n')
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
        print('\nNema posla za sada.\n')
        return


    while True:
        print("Upravo rezervises: ")
        
        while True:
            sifra = input('Enter session code or enter "x" to return to menu: ')
            if sifra in sifre_termina:
                break
            elif sifra.lower() == 'x':
                return
            else:
                print('Choose one of existing session codes.\n')
        while True:
            username = input('Enter username of your candidate or enter "x" to return to menu: ')
            cursor.execute('SELECT status_korisnika, paket FROM korisnici WHERE korisnicko_ime = ?', (username,))
            data = cursor.fetchone()

            if username.lower() == "x":
                return
            elif data:
                status, paket = data
                break
            else:
                print('Izaberi jednog od postojecih korisnika.\n')

        cursor.execute('''SELECT programi_treninga.paket
                            FROM trening
                            JOIN programi_treninga
                            ON trening.naziv_programa = programi_treninga.naziv_programa
                            JOIN termin
                            ON trening.sifra_treninga = termin.sifra_treninga
                            WHERE termin.sifra_termina = ?''', (sifra,))

        paket_potreban = cursor.fetchone()[0]

        if status == 'neaktivan':
            print(f'\n{username} korisnik nije aktivan.\n')
        elif paket == 'premium':
            odabir_mesta_instruktor(cursor, sifra, username)
        elif paket == 'standard' and paket_potreban == 'premium':
            print('Korisniku treba premium, a on ima samo standard.\n')
        elif paket == 'standard' and paket_potreban == 'standard':
            odabir_mesta_instruktor(cursor, sifra, username)
        else:
            print('Nesto nevalja tu.\n'
                    'Pokusaj ponovo.\n')


        

def odabir_mesta_instruktor(cursor, sifra, username):
    while True:
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
            biracko_mesto = input('Unesi mesto koje zelis da rezervises: ')
            if biracko_mesto not in slobodna_mesta:
                print("Izaberi slobodno mesto")
            else:
                break

        cursor.execute('SELECT sifra_rezervacije FROM rezervacije')
        sifre_rezervacija = [sifra_rezervacije[0] for sifra_rezervacije in cursor.fetchall()]
        while True:
            rdm_sifra = random.randint(1, 2000)
            if rdm_sifra not in sifre_rezervacija:
                break

        datum = date.today()

        cursor.execute('INSERT INTO rezervacije VALUES (?, ?, ?, ?, ?)', (rdm_sifra, username, sifra, biracko_mesto, datum))
        break

def query_za_pregled_rez_instruktor(cursor):
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
    return cursor.fetchall(), cursor.description

def pregled_rezervacija_instruktor(cursor):
    print('Pregled rezervisanih mesta')
    data, headers = query_za_pregled_rez_instruktor(cursor)
    
    if data:
        headers = [desc[0] for desc in headers]
        table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
        print(table)
    else:
        print('\nNemas nikakvih rezervacija.\n')

def brisanje_rezervacija_instruktor(cursor):
    while True:
        print('Pregled rezervisanih mesta')
        data, headers = query_za_pregled_rez_instruktor(cursor)
        
        if data:
            headers = [desc[0] for desc in cursor.description]
            table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
            print(table)
        else:
            print('\nNemas nikakvih rezervacija.\n')
            return

        instruktorove_rez = [informacije[0] for informacije in data]

        print('\nPoništavanje rezervisanih mesta\n')
        odabir = input('\nUnesi sifru rezervacije ili "x" za povratak na meni: ')
        if odabir.lower() == 'x':
            return
        elif eval(odabir) in instruktorove_rez:
            cursor.execute('DELETE FROM rezervacije WHERE sifra_rezervacije = ?', (odabir,))
            print('Uspesno obrisano.')
        else:
            print('Unesi sifru rezervacije koja postoji.\n'
                  'Unesi ponovo.\n')

def pretraga_rez_mesta(cursor):
    while True:
        print('Pretraga rezervisanih mesta')
        print('\n može se pretraživati po šifri treninga, imenu, prezimenu člana, po datumu, vremenu početka/kraja treninga.\n')
        print('1) Sifra treninga\n'
            '2) Ime korisnika\n'
            '3) Prezime korisnika\n'
            '4) Datum treninga\n'
            '5) Vreme pocetka treninga\n'
            '6) Vreme kraja treninga\n'
            'x) Povratak na meni\n')
        odabir = input('Kako hoces da pretrazujes rezervacije: ')
        if odabir == '1':
            word = eval(input('Unesi sifru treninga: '))
            nastavak = ' AND trening.sifra_treninga = ?'
            pretraga_rez_mesta_nastavak(cursor, nastavak, word)

        elif odabir == '2':
            word = input('Unesi ime korisnika: ')
            nastavak = 'AND korisnici.ime = ?'
            pretraga_rez_mesta_nastavak(cursor, nastavak, word)

        elif odabir == '3':
            word = input('Unesi prezime korisnika: ')
            nastavak = 'AND korisnici.prezime = ?'
            pretraga_rez_mesta_nastavak(cursor, nastavak, word)
            

        elif odabir == '4':
            word = input('Unesi datum u formatu (yyyy-mm-dd): ')
            nastavak = 'AND termin.datum = ?'
            pretraga_rez_mesta_nastavak(cursor, nastavak, word)

        elif odabir == '5':
            word = input('Unesi pocetak treninga (hh:mm): ')
            nastavak = 'AND trening.vreme_pocetka = ?'
            pretraga_rez_mesta_nastavak(cursor, nastavak, word)

        elif odabir == '6':
            word = input('Unesi kraj treninga (hh:mm): ')
            nastavak = 'AND trening.vreme_kraja = ?'
            pretraga_rez_mesta_nastavak(cursor, nastavak, word)

        elif odabir.lower() == 'x':
            return
        else:
            print('Nevazeci izbor.\n'
                  'Unesi ponovo.\n')

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
        print('\nNema tih rezervacija sa tim podacima.\n')





