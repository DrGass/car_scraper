from time import sleep

from bs4 import BeautifulSoup
from requests import get
import csv
import pyodbc
import random

# tablica do wpisywania scrapowanych rekordów
head = []
# head.append(['Marka', 'Model', 'Rok_prod.', 'Paliwo', 'Przebieg', 'Pojemność', 'Skrzynia biegów', 'Kolor', 'Stan',
#              'Cena', 'Kraj', 'Link'])

#tworzenie połączenia do MS SQL Server
baza_danych = pyodbc.connect('Driver={SQL Server};''Server=LAPTOP-AVN5LJKQ;''Database=mgr_aplikacja;'
                             'Trusted_Connection=yes')
cursor = baza_danych.cursor()

# funkcja do tłumaczenia paliwa
def paliwo_translate(string):
    fuel = {
        'Бензин': 'Benzyna',
        'Дизель': 'Diesel',
        'Гибрид': 'Hybryda',
        'Электро': 'Elektryczny',
        'Газ': 'Benzyna+LPG'
    }
    for key, value in fuel.items():
        if string == key:
            # print(string, key, value)
            return string.replace(key, value)
    return ''

# funckja do tłuamczenia skrzyni
def skrzynia_translate(string):
    gearbox = {
        'механическая': 'Manualna',
        'автоматическая': 'Automatyczna',
        'роботизированная': 'Automatyczna',
        'вариатор': 'Automatyczna',
        'Автоматическая': 'Automatyczna',
        'робот': 'Automatyczna',
        'механика': 'Manualna',
        'автомат': 'Automatyczna'
    }
    for key, value in gearbox.items():
        if string == key:
            # print(string, key, value)
            return string.replace(key, value)
    return ''

# funkcja do tłumaczenia kolorów
def kolor_translate(string):
    colors = {
        'серый': 'Szary',
        'синий': 'Niebieski',
        'голубой': 'Niebieski',
        'серебристый': 'Srebrny',
        'белый': 'Biały',
        'фиолетовый': 'Fioletowy',
        'пурпурный': 'Fioletowy',
        'красный': 'Czerwony',
        'зелёный': 'Zielony',
        'чёрный': 'Czarny',
        'золотой': 'Złoty',
        'золотистый': 'Złoty',
        'жёлтый': 'Żółty',
        'коричневый': 'Brązowy',
        'бежевый': 'Beżowy',
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

def auto_ru():

    # linki do poszczególnych aut
    if auto == 1:
        rl = 'https://auto.ru/cars/volkswagen/golf/all/?page='
    elif auto == 2:
        rl = 'https://auto.ru/cars/toyota/rav_4/all/?page='
    elif auto == 3:
        rl = 'https://auto.ru/cars/audi/a4/all/?page='

    def parse_auto_ru(page_number):
        print(f'Strona nr: {page_number}' + str(' Rosja'))
        URL = rl + str(page_number)

       # print(URL)

        page = get(URL)
        bs = BeautifulSoup(page.content, 'html.parser')

        try:
            for offer in bs.find_all('div', class_='ListingItem__description'):
                print(bs)
                # dane oferty
                kraj = 'Rosja'

                sleep(trng.randint(5, 30))

                # wylapywanmie spacji model, marka
                oferta = offer.find('a', class_='Link ListingItemTitle__link').get_text()
                point1 = oferta.find(' ')
                car_name = oferta[:point1]
                point2 = oferta[point1 + 1:].find(' ') + len(car_name)
                # print(point1, point2)

                # wycinanie danych z banera
                marka = offer.find('a', class_='Link ListingItemTitle__link').get_text()[:point1]
                model = offer.find('a', class_='Link ListingItemTitle__link').get_text()[len(marka)+1:point2 + 1]

                # wyciąganie przebiegu
                przebieg = offer.find('div', class_="ListingItem__kmAge").get_text()

                if przebieg == 'Новый':
                    stan = 'Nowe'
                    przebieg = '0'
                else:
                    stan = 'Używane'
                    przebieg = przebieg.replace(u'\xa0', u' ')[:-3]
                sleep(trng.randint(0, 5))
                #print(przebieg)

                # wyciaganie roku produkcji
                rok_produkcji = offer.find('div', class_='ListingItem__year').get_text()

                # wyciannnie rodzaju paliwa z baneru
                paliwo_oferta = offer.find('div', class_='ListingItemTechSummaryDesktop ListingItem__techSummary').find(
                    'div', class_='ListingItemTechSummaryDesktop__cell').get_text()
                separator1 = paliwo_oferta.rfind('/')
                rodzaj_paliwa = paliwo_translate(offer.find(
                    'div', class_='ListingItemTechSummaryDesktop__cell').get_text().strip()[separator1 + 2:])
                # print(stan, rodzaj_paliwa, rok_produkcji)
                sleep(trng.randint(0, 5))

                # wyciąganie pojemnosci
                pojemnosc = offer.find('div', class_='ListingItemTechSummaryDesktop ListingItem__techSummary').find(
                    'div', class_='ListingItemTechSummaryDesktop__cell').get_text().strip()[:3]
                if rodzaj_paliwa == 'Elektryczny':
                    pojemnosc = ''
                else:
                    pojemnosc = int(float(pojemnosc) * 1000)

                #wyciąganie ceny
                cena = offer.find('div', class_='ListingItemPrice__content').get_text().strip()[:-2]
                cena = cena.replace(u'\xa0', u'')

                # czyszczenie ceny
                if cena[:3] == 'от ':
                    cena = cena[3:]
                else:
                    cena = cena

                cena = int(float(cena) * 0.033)

                sleep(trng.randint(0, 5))

                # wyciaganie skrzyni
                skrzynia = offer.find('div', class_='ListingItemTechSummaryDesktop__cell').find_next('div').get_text()
                skrzynia = skrzynia_translate(skrzynia)
                if rodzaj_paliwa == 'Elektryczny':
                    skrzynia = 'Automatyczna'
                else:
                    skrzynia = skrzynia

                # wyciaganie koloru
                kolor = offer.find('div', class_='ListingItemTechSummaryDesktop__cell').find_next('div').find_next(
                    'div').find_next('div').find_next('div').find_next('div').get_text()
                kolor = kolor_translate(kolor)
                #print(skrzynia, kolor)
                # Wejście w konkretną ofertę
                link = offer.find('a', class_='Link ListingItemTitle__link').get('href')

                # print(marka, model, rok_produkcji, rodzaj_paliwa, przebieg, pojemnosc, skrzynia, kolor, stan, cena,
                #       kraj, link)

                # wgranie danych do tabeli
                head.append([marka, model, rok_produkcji, rodzaj_paliwa, przebieg, pojemnosc, skrzynia,
                    kolor, stan, cena, kraj, link])

                # export danych na serwer
                cursor.execute('''INSERT INTO dane (marka, model, rok_prod, paliwo, przebieg, pojemnosc,
                    skr_bie, kolor, stan, cena, kraj, link) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', marka, model,
                    rok_produkcji, rodzaj_paliwa, przebieg, pojemnosc, skrzynia, kolor, stan, cena, kraj, link)

                global counter
                counter = counter + 1

        except AttributeError:
            print('No data')

        baza_danych.commit()

    for i in range(1, 21):
        parse_auto_ru(i)

    with open('dane.csv', 'a+', encoding='utf-8-sig', newline='') as plik:
        csv_output = csv.writer(plik, delimiter=';')
        csv_output.writerows(head)

    global counter
    print(f'counter = {counter}')

def main():
    auto_ru()

    baza_danych.close()

if __name__ == "__main__":
    main()