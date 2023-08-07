from time import sleep

from bs4 import BeautifulSoup
from requests import get
import csv
import currency_conversion as cc
import pyodbc

# zmienna z odwołaniem do słownika kursów
currencyDict = cc.create_dict()

# tablica do wpisywania scrapowanych rekordów
head = []
# head.append(
#     ['Marka', 'Model', 'Rok_prod.', 'Paliwo', 'Przebieg', 'Pojemność', 'Skrzynia biegów', 'Kolor', 'Stan',
#      'Cena', 'Kraj', 'Link'])

#tworzenie połączenia do MS SQL Server
baza_danych = pyodbc.connect('Driver={SQL Server};''Server=LAPTOP-AVN5LJKQ;''Database=mgr_aplikacja;'
                             'Trusted_Connection=yes')
cursor = baza_danych.cursor()

# funkcja do tłumaczenia paliwa
def paliwo_translate(string):
    fuel = {
        'Benzin': 'Benzyna',
        'Diesel': 'Diesel',
        'Hybrid': 'Hybryda',
        'Elektro': 'Elektryczny',
        'Elektro/Benzin': 'Hybryda',
        'Elektro/Diesel': 'Hybryda',
        'Autogas(LPG)': 'Benzyna+LPG',
        'Sonstige': 'Inne'
    }

    for key, value in fuel.items():
        if string == key:
            # print(string, key, value)
            return string.replace(key, value)
    return ''

# funckja do tłuamczenia skrzyni
def skrzynia_translate(string):
    return string.replace('Schaltgetriebe', 'Manualna').replace('Automatik', 'Automatyczna').replace('Halbautomatik',
        'Automatyczna')

# funckja do usuwania niepotrzebnych znaków z ceny
def cena_translate(string):
    return string.replace(',-', '').replace('MwSt. ausweisb', '').replace('\n', '')

# funkcja do usuwania nowej linii
def newLine_translate(string):
    return string.replace('\n', ' ')

# funkcja do tłumaczenia kolorów
def kolor_translate(string):
    colors = {
        'Beige': 'Beżowy',
        'Braun': 'Brązowy',
        'Gelb': 'Żółty',
        'Grün': 'Zielony',
        'Schwarz': 'Czarny',
        'Violett': 'Fioletowy',
        'Orange': 'Pomarańczowy',
        'Blau': 'Niebieski',
        'Bronze': 'Brązowy',
        'Grau': 'Szary',
        'Rot': 'Czerwony',
        'Silber': 'Srebrny',
        'Weiß': 'Biały',
        'Gold': 'Złoty'
    }
    # print(string)
    for key, value in colors.items():
        if string == key:
            # print(string, key, value)
            return string.replace(key, value)


counter = 0

# zmienna do próbowania wejścia na stronę do skutku
check = False

# import wyboru auta
import gate
auto = gate.go()

def autoscout24_de():

    # linki do poszczególnych aut
    if auto == 1:
        rl1 = 'https://www.autoscout24.de/lst/volkswagen/golf-(alle)?sort=standard&desc=0&ustate=N%2CU&atype=C&cy=D&ocs_listing=include&page='
        rl2 = '&search_id=d0qlxkee2k'
    elif auto == 2:
        rl1 = 'https://www.autoscout24.de/lst/toyota/rav-4?sort=standard&desc=0&ustate=N%2CU&atype=C&cy=D&ocs_listing=include&page='
        rl2 = '&search_id=1tdndclb7z3'
    elif auto == 3:
        rl1 = 'https://www.autoscout24.de/lst/audi/a4?sort=standard&desc=0&ustate=N%2CU&atype=C&cy=D&ocs_listing=include&page='
        rl2 = '&search_id=2cuset97nyj'

    def parse_autoscout24_de(page_number):

        print(f'Strona nr: {page_number}'+str(' Niemcy'))
        URL =  rl1 + str(page_number) + rl2

        page = get(URL)
        bs = BeautifulSoup(page.content, 'html.parser')
        check = True

        # print(bs.prettify())

        for offer in bs.find_all('article', attrs={"data-testid": "list-item"}):

            #print(offer)
            kraj = 'Niemcy'
            # Punkty do ucięcia linka
            lpoint = int(str(offer.find('a')).find('/'))
            rpoint = int(str(offer.find('a')).find('>'))
            link = 'https://www.autoscout24.de' + str(offer.find('a').get('href'))# [lpoint:rpoint-2]
            # Dane z bannera
            banner_data = offer.find('div', class_='css-hffhkd emtvtq415')
            # print(banner_data)
            # Wyciąganie danych z bannera
            nazwa = offer.find('h2').get_text()
            lpoint = nazwa.find(' ')
            # przypisanie marki
            marka = nazwa[:lpoint]
            nazwa = nazwa[lpoint+1:]
            if nazwa.find(' ') == -1:
                model = nazwa[:lpoint+1]
            else:
                #przypisanie modelu
                rpoint = nazwa.find(' ')
                model = nazwa[:rpoint]
            # print(lpoint, rpoint, nazwa)
            try:
                # wyciąganie ceny
                cena = float(cena_translate(
                    offer.find('span', class_='css-113e8xo').get_text().strip()[2:-2].replace('.', '').replace(',', '')))

                # print(cena)
                cena = int(round(cc.convert('EUR', cena, currencyDict), 0))

                #wyciąganie r_prod, przebiegu, r_paliwa, skrzyni
                details = banner_data.find('div', class_='css-1xom8dl e1hcrnma0')

                przebieg = details.find('span', {'type': 'mileage'}).get_text().strip()[:-3].replace('.', '')

                rok = details.find('span', {'type': 'registration-date'}).get_text().strip()[3:]

                if rok == 'Erstanmeldung)':
                    rok = '2022'

                if przebieg == '1' or przebieg == '-':
                    stan = 'Nowe'
                    rok = '2022'
                    przebieg = '0'
                else:
                    stan = 'Używane'

                paliwo = paliwo_translate(details.find('span', {'type': 'fuel-category'}).get_text())

                skrzynia = skrzynia_translate(details.find('span', {'type': 'transmission-type'}).get_text())

            except AttributeError:
                    print('No data')
            #print(marka, model, cena, przebieg, rok, paliwo, skrzynia, stan, link)
            # Wejście w konkretną ofertę
            tempPage = get(link)
            tempBs = BeautifulSoup(tempPage.content, 'html.parser')

            # Wydzielenie wszystkich danych z tabelki
            try:
                for dane in tempBs.find_all('div', class_='css-1pioiqw eo8sp100'):
                    # Zamiana na tekst i usuniecie wszystkich znakow nowej linii
                    opis = newLine_translate(dane.get_text())
                    #print(opis)
                    pojemnosc_pos = opis.find('Hubraum')
                    pos1 = pojemnosc_pos + len('Hubraum')
                    opis = opis[pos1:]
                    pos2 = opis.find(' ')

                    if (pojemnosc_pos != -1):
                        pojemnosc = opis[:pos2]
                        pojemnosc = pojemnosc.replace('.', '')
                        # print(opis[pos1+2:pos1+7])
                    else:
                        pojemnosc = ''

                    pojemnosc = int(pojemnosc)

                # dane = tempBs.find('div', class_='css-1pioiqw eo8sp100')
                    # print(dane)
                    opis = newLine_translate(dane.get_text())
                    pos1 = opis.find('Außenfarbe')
                    pos1 = pos1 + len('Außenfarbe')
                    opis = opis[pos1:]
                    pos2 = opis.find('Farbe ')
                    kolor = opis[:pos2]
                    kolor = kolor_translate(kolor)
                    # print(pojemnosc, kolor)

                # print(marka, model, rok, paliwo, przebieg, pojemnosc, skrzynia, kolor, stan, cena,
                #       kraj, link)

                # wgranie danych do tabeli
                head.append([marka, model, rok, paliwo, przebieg, pojemnosc, skrzynia, kolor, stan, cena, kraj, link])

                # export danych na serwer
                cursor.execute('''INSERT INTO dane (marka, model, rok_prod, paliwo, przebieg, pojemnosc,
                                                                                 skr_bie, kolor, stan, cena, kraj, link) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                               marka, model,
                               rok, paliwo, przebieg, pojemnosc, skrzynia, kolor, stan, cena,
                               kraj, link)
                global counter
                counter = counter + 1
                # print(counter)
            except AttributeError:
                print("No data")
            except UnboundLocalError:
                print("unbound")
            except ValueError:
                print("No data")


            # print(opis)
        baza_danych.commit()

    for i in range(1, 21):
        parse_autoscout24_de(i)
        sleep(3)

    with open('dane.csv', 'a+', encoding='utf-8-sig', newline='') as plik:
        csv_output = csv.writer(plik, delimiter=';')
        csv_output.writerows(head)

    global counter
    print(f'counter = {counter}')

    # parse_autoscout24_de(1)

    return check

def main():
    autoscout24_de()

    baza_danych.close()

if __name__ == "__main__":
    main()