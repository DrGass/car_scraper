from time import sleep

from bs4 import BeautifulSoup
from requests import get
import csv
import currency_conversion as cc
import pyodbc
import random

# zmienna z odwołaniem do słownika kursów
currencyDict = cc.create_dict()

# tablica do wpisywania scrapowanych rekordów
head = []
# head.append(['Marka', 'Model', 'Rok_prod.', 'Paliwo', 'Przebieg', 'Pojemność', 'Skrzynia biegów', 'Kolor', 'Stan',
#      'Cena', 'Kraj', 'Link'])

#tworzenie połączenia do MS SQL Server
baza_danych = pyodbc.connect('Driver={SQL Server};''Server=LAPTOP-AVN5LJKQ;''Database=mgr_aplikacja;'
                             'Trusted_Connection=yes')
cursor = baza_danych.cursor()

counter = 0

# funckja do usuwania niepotrzebnych znaków z ceny
def cena_trim(cena):
    return cena.replace(' ', '').replace('PLN', '')

# import wyboru auta
import gate
auto = gate.go()

# zmienna do losowania czasu przestoju
trng = random.SystemRandom()

def otomoto():

    # linki do poszczególnych aut
    if auto == 1:
        rl = 'https://www.otomoto.pl/osobowe/volkswagen/golf/?search%5Border%5D=created_at%3Adesc&search%5Bbrand_program_id%5D%5B0%5D=&search%5Bcountry%5D='
    elif auto == 2:
        rl = 'https://www.otomoto.pl/osobowe/toyota/rav4?page='
    elif auto == 3:
        rl = 'https://www.otomoto.pl/osobowe/audi/a4?page='

    def parse_otomoto(page):
        global marka, model, stan, rok, kolor, skrzynia, pojemnosc, przebieg, paliwo
        print(f'Strona nr: {page}' + str(' Polska'))
        kraj = 'Polska'
        url = rl + str(page)

        page = get(url)

        bs = BeautifulSoup(page.content, 'html.parser')
        # print(bs)
        i = 1
        # Iteracja po ofertach
        for offer in bs.find_all('h2', attrs={"data-testid": "ad-title"}):
            sleep(trng.randint(3, 5))
            # wyciagniecie linku
            links = offer.find('a').attrs
            link = ''
            for key, value in links.items():
                # print(key, link)
                if key == 'href':
                    link = value
                    #print(link)

            if link.find('otomoto.pl') == -1:
                # print('\n Another page', link)
                continue

            offer_page = get(link)
            bs = BeautifulSoup(offer_page.content, 'html.parser')

            try:
                # wyciągniecie ceny
                cena = cena_trim(bs.find('span', class_='offer-price__number').get_text().strip())
                marker = cena.find('EUR')
                test_cena = cena.strip()[marker:]

                if test_cena == 'EUR':
                    cena = int(cc.convert('EUR', float(cena.strip()[:marker]), currencyDict))
                # print(cena)

                # wejście w detale
                details = bs.find('div', class_='offer-params with-vin')

                # wyciągnięcie pojedynczych detali
                detale = details.find_all('li', class_='offer-params__item')

                # iteracja przez detale
                for detal in detale:
                    phrase = detal.find('span', class_='offer-params__label').get_text()
                    if phrase == 'Marka pojazdu':
                        marka = detal.find('a').get_text().strip()
                    if phrase == 'Model pojazdu':
                        model = detal.find('a').get_text().strip()
                    if phrase == 'Rok produkcji':
                        rok = detal.find('div').get_text().strip()
                    if phrase == 'Stan':
                        stan = detal.find('a').get_text().strip()
                    if phrase == 'Kolor':
                        kolor = detal.find('a').get_text().strip()
                    if phrase == 'Skrzynia biegów':
                        skrzynia = detal.find('a').get_text().strip()
                    if phrase == 'Pojemność skokowa':
                        pojemnosc = detal.find('div').get_text().strip()[:-4]
                    if phrase == 'Rodzaj paliwa':
                        paliwo = detal.find('a').get_text().strip()
                    if phrase == 'Przebieg':
                        przebieg = detal.find('div').get_text().strip()[:-3]
                    # if phrase == 'Kraj pochodzenia':
                    #     kraj = detal.find('div').get_text().strip()

                # print(f'\n Oferta nr: {i}\n')

                # print(detale)
                #print(marka, model, stan, rok, kolor, skrzynia, pojemnosc, przebieg, paliwo, cena, kraj, link)

                # wgranie danych do tabeli
                head.append([marka, model, rok, paliwo, przebieg, pojemnosc, skrzynia,
                             kolor, stan, cena, kraj, link])

                # export danych na serwer
                cursor.execute('''INSERT INTO dane (marka, model, rok_prod, paliwo, przebieg, pojemnosc,
                                         skr_bie, kolor, stan, cena, kraj, link) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                               marka, model,
                               rok, paliwo, przebieg, pojemnosc, skrzynia, kolor, stan, cena,
                               kraj, link)

                global counter
                counter = counter + 1
                # print(counter)

            except AttributeError as error:
                cena = 0
                try:
                    # wyciągniecie ceny
                    cena = cena_trim(bs.find('span', class_='offer-price__number').get_text().strip())
                except AttributeError:
                    print('No data')
                # wejscie w detale
                details = bs.find('div', class_='offer-params')

                try:
                    # wyciągnięcie pojedynczych detali
                    detale = details.find_all('li', class_='offer-params__item')
                except AttributeError:
                    print('No data')

                try:
                    # iteracja przez detale
                    for detal in detale:
                        phrase = detal.find('span', class_='offer-params__label').get_text()
                        if phrase == 'Marka pojazdu':
                            marka = detal.find('a').get_text().strip()
                        if phrase == 'Model pojazdu':
                            model = detal.find('a').get_text().strip()
                        if phrase == 'Rok produkcji':
                            rok = detal.find('div').get_text().strip()
                        if phrase == 'Stan':
                            stan = detal.find('a').get_text().strip()
                        if phrase == 'Kolor':
                            kolor = detal.find('a').get_text().strip()
                        if phrase == 'Skrzynia biegów':
                            skrzynia = detal.find('a').get_text().strip()
                        if phrase == 'Pojemność skokowa':
                            pojemnosc = detal.find('div').get_text().strip()[:-3]
                        if phrase == 'Rodzaj paliwa':
                            paliwo = detal.find('a').get_text().strip()
                        if phrase == 'Przebieg':
                            przebieg = detal.find('div').get_text().strip()[:-2]
                except UnboundLocalError:
                    print('unbound')

                # print(f'\n Oferta nr: {i}\n')
                # print(marka, model, stan, rok, kolor, skrzynia, pojemnosc, przebieg, paliwo, cena, kraj, link)

                # wgranie danych do tabeli
                head.append([marka, model, rok, paliwo, przebieg, pojemnosc, skrzynia,
                             kolor, stan, cena, kraj, link])

                # export danych na serwer
                cursor.execute('''INSERT INTO dane (marka, model, rok_prod, paliwo, przebieg, pojemnosc,
                                         skr_bie, kolor, stan, cena, kraj, link) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                               marka, model,
                               rok, paliwo, przebieg, pojemnosc, skrzynia, kolor, stan, cena,
                               kraj, link)

                counter = counter + 1
                # print(counter)
            except UnboundLocalError:
                print('no values/u', i, link)

            i = i + 1
            #print(details)
            # print(link, '\n')

            # break

        baza_danych.commit()

    for i in range(1, 21):
        parse_otomoto(i)
        sleep(trng.randint(3, 10))

    with open('dane.csv', 'a+', encoding='utf-8-sig', newline='') as plik:
        csv_output = csv.writer(plik, delimiter=';')
        csv_output.writerows(head)

    global counter
    print(f'counter = {counter}')

def main():
    otomoto()

    baza_danych.close()

if __name__ == "__main__":
    main()