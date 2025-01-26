from tabulate import tabulate
import re
import sys


def pregled_programa(cursor):
    print('PROGRAM OVERVIEW')
    cursor.execute("SELECT * FROM programi_treninga")
    data = cursor.fetchall()

    headers = [desc[0] for desc in cursor.description]
    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)

def pretraga_programa(cursor):
    print('SEARCH OF TRAINING PROGRAMS')
    print('You can search programs by name, kind, duration(min. time, max. time, time limit), needed packet\n')
    print('To search programs by name enter 1\n'
          'To search programs by kind press 2\n'
          'To search programs by min. time press 3\n'
          'To search programs by max. time press 4\n'
          'To search programs by time limit press 5\n'
          'To search programs by package press 6\n'
          'To return to your menu enter "x".\n'
          '')
    while True:
        odabir = input('You are searching program by (or enter "x" to get back to your menu): ')
        if odabir == '1':
            while True:
                name = input('Enter name of program(or "x" to get back): ')
                cursor.execute('SELECT * FROM programi_treninga WHERE naziv_programa = ?', (name,))
                data = cursor.fetchall()
                if data:
                    prikaz_programa(data, cursor)
                elif name == 'x':
                    break
                else:
                    print('No program with that name.')


        elif odabir == '2':
            while True:
                kind = input('Enter kind of program(or "x" to get back): ')
                cursor.execute('SELECT * FROM programi_treninga WHERE vrsta_programa = ?', (kind,))
                data = cursor.fetchall()
                if data:
                    prikaz_programa(data, cursor)
                elif kind.lower() == 'x':
                    break
                else:
                    print('No program with that kind')

        elif odabir == '3':
            while True:
                min_time = input('Enter min. time of duration(or "x" to get back): ')
                cursor.execute('SELECT * FROM programi_treninga WHERE trajanje >= ?', (min_time,))
                data = cursor.fetchall()
                if data and min_time.isdigit():
                    prikaz_programa(data, cursor)
                elif min_time == 'x':
                    break
                else:
                    print('No program with that duration.')


        elif odabir == '4':
            while True:
                max_time = input('Enter max. time of duration(or "x" to get back): ')
                cursor.execute('SELECT * FROM programi_treninga WHERE trajanje <= ?', (max_time,))
                data = cursor.fetchall()
                if data and max_time.isdigit():
                    prikaz_programa(data, cursor)
                elif max_time.lower() == 'x':
                    break
                else:
                    print('No program with that duration.')

        elif odabir == '5':
            while True:
                min_time = input('Enter min. time of duration(or "x" to get back): ')
                max_time = input('Enter max. time of duration(or "x" to get back): ')
                cursor.execute('SELECT * FROM programi_treninga WHERE trajanje >= ? AND trajanje <= ?',
                               (min_time, max_time))
                data = cursor.fetchall()
                if data and min_time.isdigit() and max_time.isdigit():
                    prikaz_programa(data, cursor)
                elif min_time.lower() == 'x' or max_time.lower() == 'x':
                    break
                else:
                    print('No program with that duration.')

        elif odabir == '6':
            while True:
                packet = input('Enter package type(standard or premium)(or "x" to get back): ')
                cursor.execute('SELECT * FROM programi_treninga WHERE paket = ?', (packet.lower(),))
                data = cursor.fetchall()
                if data:
                    prikaz_programa(data, cursor)
                elif packet.lower() == 'x':
                    break
                else:
                    print('No program with that package.')

        elif odabir.lower() == 'x':
            return

        else:
            print('You entered invalid choice.')


def prikaz_programa(data, cursor):
    headers = [desc[0] for desc in cursor.description]
    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)

def pretragatermina(cursor):
    print('SEARCH TRAINING SCHEDULES')
    print('You can search training dates by: name of the program, training hall, package, date, start time or end time.')
    print('To search by name of the program enter 1.\n'
          'To search by training hall enter 2.\n'
          'To search by package enter 3.\n'
          'To search by date enter 4.\n'
          'To search by start time enter 5.\n'
          'To search by end time enter 6.')

    query1 = '''SELECT trening.naziv_programa, programi_treninga.vrsta_programa, trening.sifra_sale, 
                   termin.datum, trening.vreme_pocetka, trening.vreme_kraja, programi_treninga.paket 
               FROM trening 
               JOIN programi_treninga ON trening.naziv_programa = programi_treninga.naziv_programa 
               JOIN termin ON trening.sifra_treninga = termin.sifra_treninga '''

    while True:
        odabir = input('Your are searching training by(or enter "x" to return): ')
        if odabir == '1':
            while True:
                print('\nYOU ARE CHOOSING BY NAME OF THE PROGRAM')
                word = input('Enter name of the program(or enter "x" to return): ')
                if word.lower() == 'x':
                    break
                else:
                    query2 = 'WHERE programi_treninga.naziv_programa = ?'
                    prikaz_pretrage_termina2(cursor, query1, query2, word)


        elif odabir == '2':
            while True:
                print('\nYOU ARE CHOOSING BY TRAINING HALL')
                word = input('Enter hall code(or enter "x" to return): ')
                if word.lower() == 'x':
                    break
                else:
                    query2 = 'WHERE trening.sifra_sale = ?'
                    prikaz_pretrage_termina2(cursor, query1, query2, word)

        elif odabir == '3':
            while True:
                print('YOU ARE CHOOSING BY PACKAGE')
                word = input('Enter package (standard or premium)(or enter "x" to return): ')
                if word == 'x':
                    break
                else:
                    query2 = 'WHERE programi_treninga.paket = ?'
                    prikaz_pretrage_termina2(cursor, query1, query2, word)

        elif odabir == '4':
            while True:
                print('YOU ARE CHOOSING BY DATE')
                year = '2025'
                month = input('Enter month ("mm")(or enter "x" to return): ')
                day = input('Enter day ("dd")(or enter "x" to return): ')
                word = year + '-' + month + '-' + day
                date_pattern = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'

                if month.lower() == 'x' or day.lower() == 'x':
                    break
                elif re.match(date_pattern, word):
                    query2 = 'WHERE termin.datum = ?'
                    prikaz_pretrage_termina2(cursor, query1, query2, word)
                else:
                    print('Enter valid date.')


        elif odabir == '5':
            while True:
                print('YOU ARE CHOOSING BY START TIME')
                word = input('Enter start time (hh:mm)(or enter "x" to return): ')

                if word.lower() == 'x':
                    break
                else:
                    query2 = 'WHERE trening.vreme_pocetka = ?'
                    prikaz_pretrage_termina2(cursor, query1, query2, word)

        elif odabir == '6':
            while True:
                print('YOU ARE CHOOSING BY END TIME')
                word = input('Enter end time (hh:mm)(or enter "x" to return): ')

                if word.lower() == 'x':
                    break
                else:
                    query2 = 'WHERE trening.vreme_kraja = ?'
                    prikaz_pretrage_termina2(cursor, query1, query2, word)

        elif odabir.lower() == 'x':
            return

        else:
            print('INVALID CHOICE\n')

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
        print('There is no training with that information.')


def unos_izmena_brisanje_programa(cursor):
    print('ADDING NEW, CHANGING OLD AND DELETING TRAINING PROGRAMS')
    print('To add new program enter 1.\n'
          'To delete program enter 2.\n'
          'To change old program enter 3.')
    while True:
        odabir = input('Your choice is(or enter "x" to return to menu): ')
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
            print('INVALID CHOICE')


def unos_programa(cursor):
    print('YOU ARE ADDING NEW PROGRAM')
    print('Each program has: name, kind, duration, instructor, description, needed package.')

    cursor.execute('SELECT naziv_programa FROM programi_treninga')
    nazvani = cursor.fetchall()

    while True:
        name = input('Enter name: ')
        if any(name == nazvanko[0] for nazvanko in nazvani):
            print('Training with that name aleady exists.')
        elif name.strip() == '':
            print('Enter something.')
        else:
            break

    while True:
        kind = input('Enter kind: ')
        if kind.strip() == '':
            print('Enter something')
        else:
            break

    while True:
        duration = input('Enter duration in minutes: ')
        if duration.isdigit():
            break
        else:
            print('Duration must be in minutes.')

    print('Choose name of instructor: ', end='')
    cursor.execute('SELECT ime, prezime FROM korisnici WHERE uloga = "instruktor"')
    imena = cursor.fetchall()
    for ime in imena:
        print(ime[0] + ' ' + ime[1], end=', ')
    while True:
        instruktor = input('\nEnter name of instructor: ')
        if any(instruktor == f'{ime[0]} {ime[1]}' for ime in imena):
            break
        else:
            print('Choose one of already existing instructors.')

    opis = input('Enter short description: ')
    while True:
        paket = input('Enter needed package (standard or premium): ')
        if paket in ['standard', 'premium']:
            break
        else:
            print('Choose standard or premium, there is no third.')


    cursor.execute('INSERT INTO programi_treninga VALUES (?, ?, ?, ?, ?, ?)', (name, kind, duration, instruktor, opis, paket))

def brisanje_programa(cursor):
    print('DELETE PROGRAM')
    name = input('Enter name of the program you want to delete: ')
    cursor.execute('DELETE FROM programi_treninga WHERE naziv_programa = ?', (name,))

def izmena_programa(cursor):
    naziv_programa = input("Enter the name of the program you want to update: ")
    cursor.execute('SELECT COUNT(naziv_programa) FROM programi_treninga WHERE naziv_programa = ?', (naziv_programa,))
    data = cursor.fetchone()
    if data[0] > 0:
        izmena_programa_column(cursor, naziv_programa)
    else:
        print('INVALID NAME PROGRAM')
        izmena_programa(cursor)

def izmena_programa_column(cursor, naziv_programa):
    print('This is program you want to change: ')
    cursor.execute("SELECT * FROM programi_treninga WHERE naziv_programa = ?", (naziv_programa,))
    data = cursor.fetchall()

    headers = [desc[0] for desc in cursor.description]
    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)
    print('For each information type new or if you want to keep old one press ENTER')
    data = data[0]

    cursor.execute('SELECT naziv_programa FROM programi_treninga')
    nazivi = cursor.fetchall()

    while True:
        naziv = input('Enter new program name: ')
        if naziv.strip() == '':
            naziv = data[0]
            break
        elif any(naziv == naz[0] for naz in nazivi):
            print('Program with that name already exists.')
        else:
            break

    vrsta = input('Enter new training kind: ')
    if vrsta.strip() == '':
        vrsta = data[1]

    while True:
        trajanje = input('Enter new duration: ')
        if trajanje.strip() == '':
            trajanje = data[2]
            break
        elif trajanje.isdigit():
            break
        else:
            print('Duration should be in minutes.')

    print('Choose name of instructor: ', end='')
    cursor.execute('SELECT ime, prezime FROM korisnici WHERE uloga = "instruktor"')
    imena = cursor.fetchall()
    for ime in imena:
        print(ime[0] + ' ' + ime[1], end=', ')

    while True:
        instruktor = input('Enter name of instructor: ')
        if any(instruktor == f"{ime[0]} {ime[1]}" for ime in imena):
            break
        elif instruktor.strip() == '':
            instruktor = data[3]
            break
        else:
            print("Invalid instructor name. Please try again.")

    opis = input('Enter short description: ')
    if opis.strip() == '':
        opis = data[4]

    while True:
        paket = input('Enter new package(standard or premium): ')
        if paket in ['standard', 'premium']:
            break
        elif paket.strip() == '':
            paket = data[5]
            break
        else:
            print('Invalid choice. Try again.')

    cursor.execute('UPDATE programi_treninga SET naziv_programa = ?,  vrsta_programa = ?, trajanje = ?, instruktor = ?, opis = ?, paket = ? WHERE naziv_programa = ?', (naziv, vrsta, trajanje, instruktor, opis, paket, naziv_programa))


def pregled_treninga(cursor):
    print('Trening OVERVIEW')
    cursor.execute("SELECT * FROM trening")
    data = cursor.fetchall() 
    headers = [desc[0] for desc in cursor.description]

    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)


def unos_izmena_brisanje_treninga(cursor):
    print('ADDING NEW, CHANGING OLD AND DELETING TRAINING')
    print('To add new training enter 1.\n'
          'To delete training enter 2.\n'
          'To change old training enter 3.\n'
          'To return to menu enter "x".\n')
    odabir = input('Your choice is: ')
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
        print('INVALID CHOICE')
        unos_izmena_brisanje_programa(cursor)

def unos_treninga(cursor):
    print('ADDING NEW TRAINING')
    print('Training contains: training code, hall code, start time, end time, day, program name.')

    cursor.execute('SELECT sifra_treninga FROM trening')
    sifrice = [sif[0] for sif in cursor.fetchall()]
    print(sifrice)
    while True:
        sifra_treninga = input('Enter training code: ')
        if eval(sifra_treninga) in sifrice:
            print('Take another one, this one is already taken.')
        elif sifra_treninga.strip() == '':
            print('Choose something.')
        elif sifra_treninga.isdigit():
            break
        else:
            print('Try something else.')

    while True:
        sifra_sale = input('Enter hall code: ')
        if sifra_sale.strip() == '':
            print('Choose something.')
        elif sifra_sale.isdigit():
            break
        else:
            print('Try something else.')


    pattern = r'^([01]\d|2[0-3]):[0-5]\d$'
    while True:
        start_time = input('Enter start time("hh:mm"): ')
        if start_time.strip() == '':
            print('Choose something.')
        elif re.match(pattern, start_time):
            break
        else:
            print('Invalid time format. Try again.')

    while True:
        end_time = input('Enter end time("hh:mm"): ')
        if end_time.strip() == '':
            print('Choose something.')
        elif re.match(pattern, end_time):
            break
        else:
            print('Invalid time format. Try again.')

    while True:
        day = input('Enter day: ')
        if day.strip() == '':
            print('Choose something')
        else:
            break

    cursor.execute('SELECT naziv_programa FROM programi_treninga')
    nazivi = cursor.fetchall()
    print('\nAvailable progrm names: ', end = '')
    for naziv in nazivi:
        print(naziv[0], end=', ')
    while True:
        name = input('\nEnter program name: ')
        if any(name == naziv[0] for naziv in nazivi):
            break
        elif name.strip() == '':
            print('Choose something.')
        else:
            print('Invalid name')

    cursor.execute('INSERT INTO trening VALUES (?, ?, ?, ?, ?, ?)', (sifra_treninga, sifra_sale, start_time, end_time, day, name))

def brisanje_treninga(cursor):
    print('TRAINING OVERVIEW')
    pregled_treninga(cursor)
    print('DELETE TRAINING')
    name = input('Enter training code from training you want to delete: ')
    cursor.execute('DELETE FROM trening WHERE sifra_treninga = ?', (name,))

def izmena_treninga(cursor):
    print('TRAINING CHANGE')
    while True:
        sifra = input('Enter training code: ')
        cursor.execute('SELECT COUNT(sifra_treninga) FROM trening WHERE sifra_treninga = ?', (sifra,))
        data = cursor.fetchone()
        if data[0] > 0:
            izmena_treninga_column(cursor, sifra)
            break
        else:
            print('Invalid training code. Try again.')

def izmena_treninga_column(cursor, sifra):
    print('This is training you want to change: ')
    cursor.execute("SELECT * FROM trening WHERE sifra_treninga = ?", (sifra,))
    data = cursor.fetchall()

    headers = [desc[0] for desc in cursor.description]
    table = tabulate(data, headers, tablefmt="fancy_grid", colalign=['center'] * len(headers))
    print(table)

    data = data[0]
    print('Enter new information or if you want to keep old one press ENTER')

    cursor.execute('SELECT sifra_treninga FROM trening')
    sifrice = cursor.fetchall()

    while True:
        sifra_treninga = input('Enter new training code: ')
        if sifra_treninga == '':
            sifra_treninga = data[0]
            break
        elif any(sifra_treninga == sif[0] for sif in sifrice):
            print('Training code already exists, enter new one.')
        elif sifra_treninga.isdigit() and not any(sifra_treninga == sif[0] for sif in sifrice):
            break
        else:
            print('Try something else.')

    while True:
        sifra_sale = input('Enter hall code: ')
        if sifra_sale == '':
            sifra_sale = data[1]
            break
        elif sifra_sale.isdigit():
            break
        else:
            print('Try something else.')

    pattern = r'^([01]\d|2[0-3]):[0-5]\d$'
    while True:
        vreme_pocetka = input('Enter start time("hh:mm"): ')
        if vreme_pocetka == '':
            vreme_pocetka = data[2]
            break
        elif re.match(pattern, vreme_pocetka):
            break
        else:
            print('Invalid time format. Try again.')

    while True:
        vreme_kraja = input('Enter end time("hh:mm"): ')
        if vreme_kraja == '':
            vreme_kraja = data[3]
            break
        elif re.match(pattern, vreme_kraja):
            break
        else:
            print('Invalid time format. Try again.')

    dan = input('Enter day: ')
    if dan.strip() == '':
        dan = data[4]

    cursor.execute('SELECT naziv_programa FROM programi_treninga')
    nazivajmo = cursor.fetchall()

    while True:
        naziv = input('Enter name of the program: ')
        if naziv == '':
            naziv = data[5]
            break
        elif any(naziv == nazivam[0] for nazivam in nazivajmo):
            break
        else:
            print('Choose ono of already existing names. Try again.')

    cursor.execute('UPDATE trening SET sifra_treninga = ?, sifra_sale = ?, vreme_pocetka = ?, vreme_kraja = ?, dan = ?, naziv_programa = ? WHERE sifra_treninga = ?', (sifra_treninga, sifra_sale, vreme_pocetka, vreme_kraja, dan, naziv, sifra))


