from tabulate import tabulate
import re
import sys


def pregled_programa(cursor):
    print('Pregled dostupnih programa treninga')
    cursor.execute("SELECT * FROM programi_treninga")
    data = cursor.fetchall()

    headers = [desc[0] for desc in cursor.description]
    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)

def pretraga_programa(cursor):
    print('Pretraga programa treninga')
    print('Mozes da pretražujes listu programa po nazivu, vrsti, trajanju treninga (minimalno trajanje, maksimalno trajanje, navođenje granica), potrebnom uplaćenom paketu.\n')
    print('1) Naziv\n'
          '2) Vrsta\n'
          '3) Minimalno trajanje\n'
          '4) Maksimalno trajanje\n'
          '5) Navodjenje min i max trajanja\n'
          '6) Paket\n'
          'x) Za vracanje na meni.\n')
    while True:
        odabir = input('\nUnesite po cemu pretrazujete program treninga: ')
        if odabir == '1':
            while True:
                name = input('Unesite ime ili "x" za povratak na pretragu: ')
                cursor.execute('SELECT * FROM programi_treninga WHERE naziv_programa = ?', (name,))
                data = cursor.fetchall()
                if data:
                    prikaz_programa(data, cursor)
                elif name.lower() == 'x':
                    break
                else:
                    print('Nema programa sa tom informacijom.')


        elif odabir == '2':
            while True:
                kind = input('Unesite vrstu ili "x" za povratak na pretragu: ')
                cursor.execute('SELECT * FROM programi_treninga WHERE vrsta_programa = ?', (kind,))
                data = cursor.fetchall()
                if data:
                    prikaz_programa(data, cursor)
                elif kind.lower() == 'x':
                    break
                else:
                    print('Nema programa sa tom informacijom.')

        elif odabir == '3':
            while True:
                min_time = input('Unesite min trajanje ili "x" za povratak na pretragu: ')
                cursor.execute('SELECT * FROM programi_treninga WHERE trajanje >= ?', (min_time,))
                data = cursor.fetchall()
                if data and min_time.isdigit():
                    prikaz_programa(data, cursor)
                elif min_time.lower() == 'x':
                    break
                else:
                    print('Nema programa sa tom informacijom.')


        elif odabir == '4':
            while True:
                max_time = input('Unesite max trajanje ili "x" za povratak na pretragu: ')
                cursor.execute('SELECT * FROM programi_treninga WHERE trajanje <= ?', (max_time,))
                data = cursor.fetchall()
                if data and max_time.isdigit():
                    prikaz_programa(data, cursor)
                elif max_time.lower() == 'x':
                    break
                else:
                    print('Nema programa sa tom informacijom.')

        elif odabir == '5':
            while True:
                min_time = input('Unesite min trajanje ili "x" za povratak na pretragu: ')
                max_time = input('Unesite max trajanje ili "x" za povratak na pretragu: ')
                cursor.execute('SELECT * FROM programi_treninga WHERE trajanje >= ? AND trajanje <= ?',
                               (min_time, max_time))
                data = cursor.fetchall()
                if data and min_time.isdigit() and max_time.isdigit():
                    prikaz_programa(data, cursor)
                elif min_time.lower() == 'x' or max_time.lower() == 'x':
                    break
                else:
                    print('Nema programa sa tom informacijom.')

        elif odabir == '6':
            while True:
                packet = input('nesite paket (standard ili premium) ili "x" za povratak na pretragu: ')
                cursor.execute('SELECT * FROM programi_treninga WHERE paket = ?', (packet.lower(),))
                data = cursor.fetchall()
                if data:
                    prikaz_programa(data, cursor)
                elif packet.lower() == 'x':
                    break
                else:
                    print('Nema programa sa tom informacijom.')

        elif odabir.lower() == 'x':
            return

        else:
            print('\nNEVAZECI IZBOR.\n')


def prikaz_programa(data, cursor):
    headers = [desc[0] for desc in cursor.description]
    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)

def pretragatermina(cursor):
    print('Pretraga termina treninga')
    print('Pretražujes termine treninga po programima treninga, salama, potrebnom uplaćeni paketu, datumu održavanja i vremenu početka i kraja.')
    print('1) Naziv programa\n'
          '2) Sala\n'
          '3) Paket\n'
          '4) Datum odrzavanja\n'
          '5) Vreme pocetka\n'
          '6) Vreme kraja')

    query1 = '''SELECT trening.naziv_programa, programi_treninga.vrsta_programa, trening.sifra_sale, 
                   termin.datum, trening.vreme_pocetka, trening.vreme_kraja, programi_treninga.paket 
               FROM trening 
               JOIN programi_treninga ON trening.naziv_programa = programi_treninga.naziv_programa 
               JOIN termin ON trening.sifra_treninga = termin.sifra_treninga '''

    while True:
        odabir = input('Unesite po cemu pretrazujes ili "x" za povratak na meni: ')
        if odabir == '1':
            while True:
                word = input('Unesite naziv programa ili "x" za povratak na pretragu: ')
                if word.lower() == 'x':
                    break
                else:
                    query2 = 'WHERE programi_treninga.naziv_programa = ?'
                    prikaz_pretrage_termina2(cursor, query1, query2, word)


        elif odabir == '2':
            while True:
                word = input('Unesite salu ili "x" za povratak na pretragu: ')
                if word.lower() == 'x':
                    break
                else:
                    query2 = 'WHERE trening.sifra_sale = ?'
                    prikaz_pretrage_termina2(cursor, query1, query2, word)

        elif odabir == '3':
            while True:
                word = input('Unesite paket (standard ili premium) ili "x" za povratak na pretragu: ')
                if word.lower() == 'x':
                    break
                else:
                    query2 = 'WHERE programi_treninga.paket = ?'
                    prikaz_pretrage_termina2(cursor, query1, query2, word)

        elif odabir == '4':
            while True:
                year = '2025'
                month = input('Unesite mesec "mm" ili "x" za povratak na pretragu: ')
                day = input('Unesite dan "dd" ili "x" za povratak na pretragu: ')
                word = year + '-' + month + '-' + day
                date_pattern = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'

                if month.lower() == 'x' or day.lower() == 'x':
                    break
                elif re.match(date_pattern, word):
                    query2 = 'WHERE termin.datum = ?'
                    prikaz_pretrage_termina2(cursor, query1, query2, word)
                else:
                    print('Unesite ispravan datum.')


        elif odabir == '5':
            while True:
                word = input('Unesite vreme pocetka "hh:mm" ili "x" za povratak na pretragu: ')
                if word.lower() == 'x':
                    break
                else:
                    query2 = 'WHERE trening.vreme_pocetka = ?'
                    prikaz_pretrage_termina2(cursor, query1, query2, word)

        elif odabir == '6':
            while True:
                word = input('Unesite vreme kraja "hh:mm" ili "x" za povratak na pretragu: ')
                if word.lower() == 'x':
                    break
                else:
                    query2 = 'WHERE trening.vreme_kraja = ?'
                    prikaz_pretrage_termina2(cursor, query1, query2, word)

        elif odabir.lower() == 'x':
            return

        else:
            print('NEVAZECI IZBOR\n')

def prikaz_pretrage_termina2(cursor, query1, query2, word):
    BRIGHT_GREEN_BORDER = "\033[38;5;82m"  # Brighter green for borders
    BLACK_TEXT = "\033[30m"  # Black text for table content
    DARK_YELLOW_BG = "\033[48;5;196m"  # Dark yellow background
    RESET = "\033[0m"  # Reset to default colors

    cursor.execute(query1 + query2, (word,))
    data = cursor.fetchall()
    if data:
        headers = [desc[0] for desc in cursor.description]

        table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))

        colored_table = ""
        for line in table.splitlines():
            colored_table += f"{BRIGHT_GREEN_BORDER}{DARK_YELLOW_BG}{BLACK_TEXT}{line}{RESET}\n"

        print(colored_table)
    else:
        print('Nema treninga sa tim informacijama.')


def unos_izmena_brisanje_programa(cursor):
    print('Unos, izmena i brisanje programa treninga.')
    print('1) Unos\n'
          '2) Brisanje\n'
          '3) Izmena')
    while True:
        odabir = input('Unesite vas izbor ili "x" za vracanje na meni: ')
        if odabir == '1':
            pregled_programa(cursor)
            unos_programa(cursor)
        elif odabir == '2':
            pregled_programa(cursor)
            brisanje_programa(cursor)
        elif odabir == '3':
            pregled_programa(cursor)
            izmena_programa(cursor)
        elif odabir.lower() == 'x':
            return
        else:
            print('Nevazeci izbor')


def unos_programa(cursor):
    print('Unos programa')
    print('Program sadrzi: naziv, vrstu, trajanje, instruktor, skraćeni opis, paket.')

    cursor.execute('SELECT naziv_programa FROM programi_treninga')
    nazvani = cursor.fetchall()

    while True:
        name = input('Unesi naziv: ')
        if any(name == nazvanko[0] for nazvanko in nazvani):
            print('trening sa tim imenom vec postoji.')
        elif name.strip() == '':
            print('Unesi bilo sta.')
        else:
            break

    while True:
        kind = input('Unesi vrstu: ')
        if kind.strip() == '':
            print('Unesi bilo sta.')
        else:
            break

    while True:
        duration = input('Unesi trajanje u minutima: ')
        if duration.isdigit():
            break
        else:
            print('Trajanje mora biti u minutima.')

    print('Choose name of instructor: ', end='')
    cursor.execute('SELECT ime, prezime FROM korisnici WHERE uloga = "instruktor"')
    imena = cursor.fetchall()
    while True:
        instruktor = input('\nUnesi ime instruktora: ')
        if any(instruktor == f'{ime[0]} {ime[1]}' for ime in imena):
            break
        else:
            print('Izaberi nekog od postojecih instruktora.')

    opis = input('Unesi kratak opis: ')
    while True:
        paket = input('Unesi paket (standard ili premium): ')
        if paket in ['standard', 'premium']:
            break
        else:
            print('Nema trece.')


    cursor.execute('INSERT INTO programi_treninga VALUES (?, ?, ?, ?, ?, ?)', (name, kind, duration, instruktor, opis, paket))

def brisanje_programa(cursor):
    print('DELETE PROGRAM')
    name = input('Unesi naziv programa koji hoces da obrises: ')
    cursor.execute('DELETE FROM programi_treninga WHERE naziv_programa = ?', (name,))

def izmena_programa(cursor):
    naziv_programa = input("Enter the name of the program you want to update: ")
    cursor.execute('SELECT naziv_programa FROM programi_treninga WHERE naziv_programa = ?', (naziv_programa,))
    data = cursor.fetchone()
    if data:
        izmena_programa_column(cursor, naziv_programa)
    else:
        print('Nema programa sa tim imenom')
        izmena_programa(cursor)

def izmena_programa_column(cursor, naziv_programa):
    print('Ovi je program koji hoces da menjas: ')
    cursor.execute("SELECT * FROM programi_treninga WHERE naziv_programa = ?", (naziv_programa,))
    data = cursor.fetchone()

    headers = [desc[0] for desc in cursor.description]
    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)
    print('Za svaku informaciju ili ukucaj novu ili pritisni ENTER da sadrzis staru informaciju.')
    
    cursor.execute('SELECT naziv_programa FROM programi_treninga')
    nazivi = cursor.fetchall()

    while True:
        naziv = input('Unesi novi naziv: ')
        if naziv.strip() == '':
            naziv = data[0]
            break
        elif any(naziv == naz[0] for naz in nazivi):
            print('Program sa tim imenom vec postoji.')
        else:
            break

    vrsta = input('Unesi novu vrstu: ')
    if vrsta.strip() == '':
        vrsta = data[1]

    while True:
        trajanje = input('Unesi novo trajanje: ').strip()
        if trajanje.strip() == '':
            trajanje = data[2]
            break
        elif trajanje.isdigit():
            break
        else:
            print('Trajanje mora biti u minutima.')

    cursor.execute('SELECT ime, prezime FROM korisnici WHERE uloga = "instruktor"')
    imena = cursor.fetchall()

    while True:
        instruktor = input('Unesi ime instruktora: ')
        if any(instruktor == f"{ime[0]} {ime[1]}" for ime in imena):
            break
        elif instruktor.strip() == '':
            instruktor = data[3]
            break
        else:
            print("Nema tog instruktora.")

    opis = input('Unesi kratag opis: ').strip()
    if opis == '':
        opis = data[4]

    while True:
        paket = input('Unesi novi paket (standard ili premium): ')
        if paket in ['standard', 'premium']:
            break
        elif paket.strip() == '':
            paket = data[5]
            break
        else:
            print('Nema trece bajo.')

    cursor.execute('UPDATE programi_treninga SET naziv_programa = ?,  vrsta_programa = ?, trajanje = ?, instruktor = ?, opis = ?, paket = ? WHERE naziv_programa = ?', (naziv, vrsta, trajanje, instruktor, opis, paket, naziv_programa))


def pregled_treninga(cursor):
    print('Pregled dosstupnih treninga')
    cursor.execute("SELECT * FROM trening")
    data = cursor.fetchall() 
    headers = [desc[0] for desc in cursor.description]

    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)


def unos_izmena_brisanje_treninga(cursor):
    print('Unos, izmena i brisanje treninga.')
    print('1) Unos\n'
          '2) Brisanje\n'
          '3) Izmena\n'
          'x) Za povratak na meni\n')
    odabir = input('Unesi svoj izbor: ').strip()
    if odabir == '1':
        unos_treninga(cursor)
    elif odabir == '2':
        brisanje_treninga(cursor)
    elif odabir == '3':
        pregled_treninga(cursor)
        izmena_treninga(cursor)
    elif odabir.lower() == 'x':
        return
    else:
        print('Nevazeci izbor')
        unos_izmena_brisanje_programa(cursor)

def unos_treninga(cursor):
    while True:
        print('Unos teninga')
        print('Tening sadrzi: sifra treninga, sala, vreme početka treninga, vreme kraja, dan/dani, program treninga.')

        cursor.execute('SELECT sifra_treninga FROM trening')
        sifrice = [sif[0] for sif in cursor.fetchall()]
        while True:
            sifra_treninga = input('Unesi sifru: ')
            if eval(sifra_treninga) in sifrice:
                print('Ajde molim te uzmi neku drugu.')
            elif sifra_treninga.strip() == '':
                print('Izaberi bar nesto.')
            elif sifra_treninga.isdigit():
                break
            else:
                print('Izaberi nesto drugo.')

        while True:
            sifra_sale = input('Unesi sifru sale: ')
            if sifra_sale.strip() == '':
                print('Unesi bar nesto.')
            elif sifra_sale.isdigit():
                break
            else:
                print('Unesi ispravnu sifru.')


        pattern = r'^([01]\d|2[0-3]):[0-5]\d$'
        while True:
            start_time = input('Unesi vreme pocetka "hh:mm": ')
            if start_time.strip() == '':
                print('Unesi bar nesto.')
            elif re.match(pattern, start_time):
                break
            else:
                print('Unesi u navedenom formatu.')

        while True:
            end_time = input('Unesi vreme kraja "hh:mm": ')
            if end_time.strip() == '':
                print('Unesi bar nesto.')
            elif re.match(pattern, end_time):
                break
            else:
                print('Unesi u navedenom formatu.')

        while True:
            day = input('Unesi dan ili dane, ali ako navodis vise dana molim te odvajaj dane sa uspravnom crtom "|": ')
            if day.strip() == '':
                print('Unesi bar nesto.')
            else:
                break

        cursor.execute('SELECT naziv_programa FROM programi_treninga')
        nazivi = cursor.fetchall()
        while True:
            name = input('\nUnesi naziv programa: ')
            if any(name == naziv[0] for naziv in nazivi):
                break
            elif name.strip() == '':
                print('Unesi bar nesto.')
            else:
                print('Invalidsko ime.')

        cursor.execute('INSERT INTO trening VALUES (?, ?, ?, ?, ?, ?)', (sifra_treninga, sifra_sale, start_time, end_time, day, name))
    
    

def brisanje_treninga(cursor):
    print('Pregled treninga')
    pregled_treninga(cursor)
    print('Brisanje treninga')
    name = input('Unesi sifru treninga koji hoces da obrises: ')
    cursor.execute('DELETE FROM trening WHERE sifra_treninga = ?', (name,))

def izmena_treninga(cursor):
    print('Izmena teninga')
    while True:
        sifra = input('Unesi sifru treninga koji zelis da izmenis: ')
        cursor.execute('SELECT sifra_treninga FROM trening WHERE sifra_treninga = ?', (sifra,))
        data = cursor.fetchone()
        if data:
            izmena_treninga_column(cursor, sifra)
            break
        else:
            print('Invalid training code. Try again.')

def izmena_treninga_column(cursor, sifra):
    print('Ovo je trening koji zelis da menjas: ')
    cursor.execute("SELECT * FROM trening WHERE sifra_treninga = ?", (sifra,))
    data = cursor.fetchone()

    headers = [desc[0] for desc in cursor.description]
    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)
    print('Unesi nove informacije ili pritisni ENTER da predjes na sledecu informaciju i zadrzis staru.')

    cursor.execute('SELECT sifra_treninga FROM trening')
    sifrice = cursor.fetchall()

    while True:
        sifra_treninga = input('Unesi novu sifru: ')
        if sifra_treninga == '':
            sifra_treninga = data[0]
            break
        elif any(sifra_treninga == sif[0] for sif in sifrice):
            print('Izaberi drugu sifru treninga.')
        elif sifra_treninga.isdigit() and not any(sifra_treninga == sif[0] for sif in sifrice):
            break
        else:
            print('Unesi neku drugu.')

    while True:
        sifra_sale = input('Unesi sifru sale: ')
        if sifra_sale == '':
            sifra_sale = data[1]
            break
        elif sifra_sale.isdigit():
            break
        else:
            print('Unesi nesto drugo.')

    pattern = r'^([01]\d|2[0-3]):[0-5]\d$'
    while True:
        vreme_pocetka = input('Unesi vreme pocetka ("hh:mm"): ')
        if vreme_pocetka == '':
            vreme_pocetka = data[2]
            break
        elif re.match(pattern, vreme_pocetka):
            break
        else:
            print('Unesi ispravan format.')

    while True:
        vreme_kraja = input('Unesi vreme kraja ("hh:mm"): ')
        if vreme_kraja == '':
            vreme_kraja = data[3]
            break
        elif re.match(pattern, vreme_kraja):
            break
        else:
            print('Unesi ispravan format.')

    dan = input('Unesi dan ili dane, ali ako navodis vise dana molim te odvajaj dane sa uspravnom crtom "|" i sve malim slovima: ').lower()
    if dan.strip() == '':
        dan = data[4]

    cursor.execute('SELECT naziv_programa FROM programi_treninga')
    nazivajmo = cursor.fetchall()

    while True:
        naziv = input('Unesi naziv programa treninga: ')
        if naziv == '':
            naziv = data[5]
            break
        elif any(naziv == nazivam[0] for nazivam in nazivajmo):
            break
        else:
            print('Izaberi jedan od postojecih naziva.')

    cursor.execute('UPDATE trening SET sifra_treninga = ?, sifra_sale = ?, vreme_pocetka = ?, vreme_kraja = ?, dan = ?, naziv_programa = ? WHERE sifra_treninga = ?', (sifra_treninga, sifra_sale, vreme_pocetka, vreme_kraja, dan, naziv, sifra))


