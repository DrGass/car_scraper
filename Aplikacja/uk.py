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
# head.append(
#     ['Marka', 'Model', 'Rok_prod.', 'Paliwo', 'Przebieg', 'Pojemność', 'Skrzynia biegów', 'Kolor', 'Stan',
#      'Cena', 'Kraj', 'Link'])

#tworzenie połączenia do MS SQL Server
baza_danych = pyodbc.connect('Driver={SQL Server};''Server=LAPTOP-AVN5LJKQ;''Database=mgr_aplikacja;'
                             'Trusted_Connection=yes')
cursor = baza_danych.cursor()

# funkcja do tłumaczenia paliwa
def paliwo_translate(string):
    if string.find('Hybrid') != -1:
        return 'Hybryda'
    return string.replace('Petrol', 'Benzyna')

# funckja do tłuamczenia skrzyni
def skrzynia_translate(string):
    return string.replace('Manual', 'Manualna').replace('Automatic', 'Automatyczna').replace('Electric',
                                                                                             'Elektryczna')

# funkcja do przetwarzania mil na km
def przebieg_translate(przebieg):
    przebieg = int(round(float(przebieg.replace(',', '.'))*1.61, 3)*1000)
    return przebieg

# funkcja do tłumaczenia kolorów
def kolor_translate(string):
    colors = {
        'Grey': 'Szary',
        'Blue': 'Niebieski',
        'Silver': 'Srebrny',
        'White': 'Biały',
        'Violett': 'Fioletowy',
        'Red': 'Czerwony',
        'Green': 'Zielony',
        'Orange': 'Pomarańczowy',
        'Brown': 'Brązowy',
        'Black': 'Czarny',
        'Bronze': 'Brązowy',
        'Beige' : 'Beżowy',
        'Gold' : 'Złoty',
        'Yellow' : 'Żółty'
    }

    for key, value in colors.items():
        if string == key:
            # print(string, key, value)
            return string.replace(key, value)
    return ''

counter = 0

# import wyboru auta
import gate
auto = gate.go()

# zmienna do losowania czasu przestoju
trng = random.SystemRandom()

def parkers_uk():

    # linki do poszczególnych aut
    if auto == 1:
        rl = 'https://www.parkers.co.uk/volkswagen/golf/search-results/?page='
    elif auto == 2:
        rl = 'https://www.parkers.co.uk/toyota/rav4/search-results/?page='
    elif auto == 3:
        rl = 'https://www.parkers.co.uk/audi/a4/search-results/?page='

    def parse_parkers_uk(page_number):
        print(f'Strona nr: {page_number}' + str(' UK'))
        URL = rl + str(page_number)

        page = get(URL)
        bs = BeautifulSoup(page.content, 'html.parser')

        sleep(3)

        try:
            for offer in bs.find_all(lambda tag: tag.name == 'li' and tag.get('class') == ['result-item']):
                # print(offer.prettify())
                kraj = 'UK'
                stan = 'Używane'

                # wyciagniecie nazwy
                nazwa = offer.find('a', class_='panel__primary-link').get_text().strip()
                separator = nazwa.find(' ')
                marka = nazwa[:separator]

                # wyciagniecie modelu
                model = nazwa[separator + 1:]
                separator = model.find(' ')
                model = model[:separator]

                # wyciagniecie detali
                detale = offer.find_all('li', class_='for-sale-result-item__specs__bullet')

                # wyciagniecie rocznika
                rocznik = detale[0].get_text()[:4]

                # wyciagniecie przebiegu
                separator = detale[1].get_text().find(' ')
                przebieg = przebieg_translate(detale[1].get_text()[:separator])
                #print(przebieg)

                # wyciagniecie skrzyni
                skrzynia = skrzynia_translate(detale[2].get_text())

                # wyciagniecie rodzaju paliwa
                paliwo = paliwo_translate(detale[3].get_text())

                # wyciagniecie ceny
                cena = offer.find('div', class_='for-sale-result-item__price__value').get_text().strip()[1:]
                cena = float(cena.replace(',', '.'))
                if cena < 10:
                    cena = cena*1000
                cena = int(cc.convert('GBP', cena, currencyDict))

                # wyciagniecie pojemnosci
                pojemnosc = offer.find('h3', class_='for-sale-result-item__sub-heading').get_text()
                marker = pojemnosc.find('.')
                pojemnosc = int(float(pojemnosc[marker-1:marker+1])*1000)

                # wyciagniecie linku
                link = str(offer.find('a', class_='for-sale-result-item__image'))
                separator = link.find('href') + len('href') + 2
                link = link[separator:]
                separator = link.find('"')
                link = 'https://www.parkers.co.uk' + link[:separator]

                # sprawdzenie czy to redirect na inna strone, jezeli tak, pomija rekord
                if (link.find('redirect') != -1):
                    continue

                # wejscie w ofertę
                try:
                    temppage = get(link)
                    tempbs = BeautifulSoup(temppage.content, 'html.parser')
                except ConnectionError:
                    print('The connection has been broken')

                # wyciagniecie koloru
                details = tempbs.find_all('li', class_='cfs-used-details-page__summary__item bullet-item')
                kolor = kolor_translate(details[1].get_text())

                # print(marka, model, rocznik, paliwo, przebieg, pojemnosc, skrzynia, kolor, stan, cena,
                #       kraj, link)
                # break

                # wgranie danych do tabeli
                head.append([marka, model, rocznik, paliwo, przebieg, pojemnosc, skrzynia,
                             kolor, stan, cena, kraj, link])

                # export danych na serwer
                cursor.execute('''INSERT INTO dane (marka, model, rok_prod, paliwo, przebieg, pojemnosc,
                                                         skr_bie, kolor, stan, cena, kraj, link) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                               marka, model,
                               rocznik, paliwo, przebieg, pojemnosc, skrzynia, kolor, stan, cena,
                               kraj, link)

                global counter
                counter = counter + 1

        except AttributeError:
            pass
        except ValueError:
            print('No data')


        baza_danych.commit()

    for i in range(1, 21):
        parse_parkers_uk(i)
        sleep(trng.randint(3, 10))

    with open('dane.csv', 'a+', encoding='utf-8-sig', newline='') as plik:
        csv_output = csv.writer(plik, delimiter=';')
        csv_output.writerows(head)

    global counter
    print(f'counter = {counter}')


def main():
    parkers_uk()

    baza_danych.close()

if __name__ == "__main__":
    main()