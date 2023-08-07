from bs4 import BeautifulSoup
from requests import get
import csv
import currency_conversion as cc
import re
import pyodbc

# zmienna z odwołaniem do słownika kursów
currencyDict = cc.create_dict()

# tablica do wpisywania scrapowanych rekordów
head = []
# head.append(['Marka', 'Model', 'Rok_prod.', 'Paliwo', 'Przebieg', 'Pojemność', 'Skrzynia biegów', 'Kolor', 'Stan',
#              'Cena', 'Kraj', 'Link'])

# tworzenie połączenia do MS SQL Server
baza_danych = pyodbc.connect('Driver={SQL Server};''Server=LAPTOP-AVN5LJKQ;''Database=mgr_aplikacja;'
                             'Trusted_Connection=yes')
cursor = baza_danych.cursor()

# słownik do tłumaczenia kolorów
colors = {
    'Beige': 'Beżowy',
    'Black': 'Czarny',
    'Blue': 'Niebieski',
    'Brown': 'Brązowy',
    'Gold': 'Złoty',
    'Gray': 'Szary',
    'Green': 'Zielony',
    'Orange': 'Pomarańczowy',
    'Pink': 'Różowy',
    'Pruple': 'Fioletowy',
    'Red': 'Czerwony',
    'Silver': 'Srebrny',
    'White': 'Biały',
    'Yellow': 'Żółty'
}

counter = 0

# funkcja do tłumaczenia paliwa
def paliwo_translate(string):
    return string.replace('Gasoline', 'Benzyna').replace('Hybrid', 'Hybryda').replace('Electric',
        'Elektryczny').replace('E85 Flex Fuel', 'Etanol').replace('–', 'Inne')

# funckja do tłuamczenia skrzyni
def skrzynia_translate(string):
    return string.replace('M', 'Manualna').replace('A', 'Automatyczna')

# funkcja do przetwarzania mil na km
def przebieg_translate(przebieg):
    przebieg = int(round(float(przebieg.replace(',', '.')) * 1.61, 3) * 1000)
    return przebieg

# import wyboru auta
import gate
auto = gate.go()

def cars_com():

    # linki do poszczególnych aut
    if auto == 1:
        rl = '&page_size=20&list_price_max=&makes[]=volkswagen&maximum_distance=all&maximum_distance_expanded=1&maximum_distance_expanded_from=all&models[]=volkswagen-golf&stock_type=all&zip='
    elif auto == 2:
        rl = '&page_size=20&list_price_max=&makes[]=toyota&maximum_distance=all&models[]=toyota-rav4&stock_type=all&zip='
    elif auto == 3:
        rl = '&page_size=20&list_price_max=&makes[]=audi&maximum_distance=all&models[]=audi-a4&stock_type=all&zip='

    def parse_cars_com(page_number):

        print(f'Strona nr: {page_number}' + str(' USA'))
        URL = 'https://www.cars.com/shopping/results/?page=' + str(
            page_number) + rl
        #print(URL)
        page = get(URL)

        bs = BeautifulSoup(page.content, 'html.parser')

        for offer in bs.find_all('div', class_='vehicle-details'):

            # dane oferty
            kraj = 'USA'

            # ustalanie stanu auta
            stan = offer.find('p', class_='stock-type').get_text()
            if stan == 'New':
                stan = 'Nowe'
            else:
                stan = 'Używane'

            # wyciąganie roku prod.
            rok_produkcji = offer.find('h2', class_='title').get_text()[:4]
            # print(stan, rok_produkcji)

            # wyłapywamie spacji model, marka
            oferta = offer.find('h2', class_='title').get_text()[5:]
            point1 = oferta.find(' ')
            marka = oferta[:point1]
            point2 = oferta[point1 + 1:].find(' ') + len(marka)

            model = oferta[len(marka) + 1:point2 + 1]
            # print(marka, model)

            # wyciąganie przebiegu
            przebieg = offer.find('div', class_='mileage').get_text().strip()[:-4]
            przebieg = przebieg_translate(przebieg)

            # wyciąganie ceny
            cena = float(offer.find('span', class_='primary-price').get_text()[1:].replace(',', ''))
            cena = int(cc.convert('USD', cena, currencyDict))

            # Wejście w konkretną ofertę
            link = 'https://www.cars.com' + str(
                offer.find('a', class_='vehicle-card-link js-gallery-click-link').get('href'))

            tempPage = get(link)
            tempBs = BeautifulSoup(tempPage.content, 'html.parser')

            try:

                for dane in tempBs.find_all('section', class_='sds-page-section basics-section'):

                    # wyciąganie koloru
                    phrase = dane.find('dt', text='Exterior color').find_next('dd').get_text()[1:-1]

                    kolor = ''
                    for color, value in colors.items():
                        try:
                            zmienna = re.search(color, phrase).group()
                            kolor = value
                        except AttributeError:
                            continue

                    # wyciąganie paliwa
                    rodzaj_paliwa = paliwo_translate(dane.find('dt', text='Fuel type').find_next('dd').get_text())

                    # wyciąganie skrzyni biegów
                    skrzynia = dane.find('dt', text='Transmission').find_next('dd').get_text()
                    # usuwanie ilości biegów
                    separator1 = skrzynia.find(' ')
                    skrzynia = skrzynia_translate(skrzynia[separator1 + 1:separator1 + 2])

                    # wyciąganie pojemności
                    pojemnosc = dane.find('dt', text='Engine').find_next('dd').get_text()
                    # usuwanie rodzaju silnika
                    separator2 = pojemnosc.find('L')
                    pojemnosc = int(float(pojemnosc[:separator2]) * 1000)

                    print(marka, model, rok_produkcji, rodzaj_paliwa, przebieg, pojemnosc, skrzynia, kolor, stan, cena,
                          kraj, link)

                    # wgranie danych do tabeli
                    head.append([marka, model, rok_produkcji, rodzaj_paliwa, przebieg, pojemnosc, skrzynia,
                                 kolor, stan, cena, kraj, link])

                    # export danych na serwer
                    cursor.execute('''INSERT INTO dane (marka, model, rok_prod, paliwo, przebieg, pojemnosc,
                                             skr_bie, kolor, stan, cena, kraj, link) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                                   marka, model,
                                   rok_produkcji, rodzaj_paliwa, przebieg, pojemnosc, skrzynia, kolor, stan, cena,
                                   kraj, link)
                    global counter
                    counter = counter + 1
            except ValueError:
                'Bad data'

        baza_danych.commit()
    for i in range(1, 21):
        parse_cars_com(i)

    with open('dane.csv', 'a+', encoding='utf-8-sig', newline='') as plik:
        csv_output = csv.writer(plik, delimiter=';')
        csv_output.writerows(head)

    global counter
    print(f'counter = {counter}')

def main():
    cars_com()

    baza_danych.close()

if __name__ == "__main__":
    main()