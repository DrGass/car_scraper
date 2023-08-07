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
        'Gasolina': 'Benzyna',
        'Diésel': 'Diesel',
        'Eléctrico': 'Elektryczny',
        'Híbrido': 'Hybryda',
        'Electro/Gasolina': 'Hybryda',
        'Electro/Diésel': 'Hybryda',
        'Gas licuado (GLP)': 'Benzyna+LPG',
        'Otros': 'Inne'
    }

    for key, value in fuel.items():
        if string == key:
            # print(string, key, value)
            return string.replace(key, value)
    return ''


# funckja do tłuamczenia skrzyni
def skrzynia_translate(string):
    return string.replace('Manual', 'Manualna').replace('Automático', 'Automatyczna').replace('Semiautomático',
        'Automatyczna').replace('- (Cambio)', '')

# funckja do usuwania niepotrzebnych znaków z ceny
def cena_translate(string):
    return string.replace(',-', '').replace('IVA deducib', '').replace('\n', '')

# funkcja do usuwania nowej linii
def newLine_translate(string):
    return string.replace('\n', ' ')

# funkcja do tłumaczenia kolorów
def kolor_translate(string):
    colors = {
        'Beige': 'Beżowy',
        'Marrón': 'Brązowy',
        'Amarillo': 'Żółty',
        'Verde': 'Zielony',
        'Negro': 'Czarny',
        'Burdeos': 'Fioletowy',
        'Naranja': 'Pomarańczowy',
        'Azul': 'Niebieski',
        'Bronce': 'Brązowy',
        'Gris': 'Szary',
        'Rojo': 'Czerwony',
        'Plateado': 'Srebrny',
        'Blanco': 'Biały',
        'Oro': 'Złoty'
    }
    # print(string)
    for key, value in colors.items():
        if string == key:
            # print(string, key, value)
            return string.replace(key, value)
    return ''


counter = 0

# zmienna do próbowania wejścia na stronę do skutku
check = False

# import wyboru auta
import gate
auto = gate.go()

def autoscout24_es():

    # linki do poszczególnych aut
    if auto == 1:
        rl1 = 'https://www.autoscout24.es/lst/volkswagen/golf-(todo)?sort=standard&desc=0&ustate=N%2CU&size=20&page='
        rl2 = '&cy=E&atype=C&recommended_sorting_based_id=c6d9e11b-262f-44cd-b9a5-29b22f430af8&'
    elif auto == 2:
        rl1 = 'https://www.autoscout24.es/lst/toyota/rav-4?sort=standard&desc=0&ustate=N%2CU&size=20&page='
        rl2 = '&cy=E&atype=C&'
    elif auto == 3:
        rl1 = 'https://www.autoscout24.es/lst/audi/a4?sort=standard&desc=0&ustate=N%2CU&size=20&page='
        rl2 = '&cy=E&atype=C&'

    def parse_autoscout24_es(page_number):

        print(f'Strona nr: {page_number}'+ str(' Hiszpania'))
        URL =  rl1 + str(page_number) + rl2

        page = get(URL)
        bs = BeautifulSoup(page.content, 'html.parser')
        check = True
        #print(URL)

        for offer in bs.find_all('div', class_='cl-list-element cl-list-element-gap'):
            kraj = 'Hiszpania'
            # Punkty do ucięcia linka
            lpoint = int(str(offer.find('a')).find('/'))
            rpoint = int(str(offer.find('a')).find('>'))
            link = 'https://www.autoscout24.es' + str(offer.find('a'))[lpoint:rpoint - 1]
            #print(link)

            # Dane z bannera
            banner_data = offer.find('div', class_='cldt-summary-vehicle-data')

            # Wyciąganie danych z bannera
            try:
                nazwa = offer.find('h2', class_='cldt-summary-makemodel sc-font-bold sc-ellipsis').get_text()
                lpoint = nazwa.find(' ')

                # przypisanie marki
                marka = nazwa[:lpoint]
                nazwa = nazwa[lpoint + 1:]
                if nazwa.find(' ') == -1:
                    model = nazwa[:lpoint + 1]
                else:
                    # przypisanie modelu
                    rpoint = nazwa.find(' ')
                    model = nazwa[:rpoint]
                # wypisanie
                # print(lpoint, rpoint, nazwa)
                try:
                    # wyciąganie ceny
                    cena = float(cena_translate(
                        offer.find('span', class_='cldt-price sc-font-xl sc-font-bold').get_text().strip()[2:-2]))

                    cena = int(cc.convert('EUR', cena, currencyDict)*1000)

                    # wyciąganie przebiegu
                    przebieg = banner_data.find('li', attrs={'data-type': 'mileage'}).get_text().strip()[:-3]
                    przebieg = int(round(float(przebieg), 3)*1000)

                    rok = banner_data.find('li', attrs={'data-type': 'first-registration'}).get_text().strip()[3:]
                except ValueError:
                    print("No data")

                # wyciąganie paliwa
                paliwo = paliwo_translate(banner_data.find('li', class_='summary_item_no_bottom_line').get_text().strip())

                # wyciąganie skrzyni
                skrzynia = skrzynia_translate(
                    banner_data.find('li', attrs={'data-type': 'transmission-type'}).get_text().strip())
                if przebieg == '1' or przebieg == '-':
                    stan = 'Nowe'
                    rok = '2021'
                    przebieg = '0'
                else:
                    stan = 'Używane'

                # print(f'{kraj}, {marka}, {model}, {link} \n {przebieg} {cena} {paliwo} {skrzynia} {stan}, {rok}')
                # Wejście w konkretną ofertę
                tempPage = get(link)
                tempBs = BeautifulSoup(tempPage.content, 'html.parser')

                # Wydzielenie wszystkich danych z tabelki

                for dane in tempBs.find_all('div', class_='cldt-categorized-data cldt-data-section sc-pull-left'):
                    # Zamiana na tekst i usuniecie wszystkich znakow nowej linii
                    opis = newLine_translate(dane.get_text())
                    pojemnosc_pos = opis.find('Cilindrada')
                    pos1 = pojemnosc_pos + len('Cilindrada')
                    opis = opis[pos1 + 2:]
                    pos2 = opis.find(' ')

                    if (pojemnosc_pos != -1):
                        pojemnosc = opis[:pos2]
                        # print(opis[pos1+2:pos1+7])
                        pojemnosc = int(round(float(pojemnosc), 3)*1000)

                    else:
                        pojemnosc = ''


                dane = tempBs.find('div', class_='cldt-categorized-data cldt-data-section sc-pull-right')
                # print(dane)
                opis = newLine_translate(dane.get_text())
                pos1 = opis.find('Color')
                pos1 = pos1 + len('Color')
                opis = opis[pos1 + 2:]
                pos2 = opis.find(' ')
                kolor = opis[:pos2]
                kolor = kolor_translate(kolor)
                # print(kolor, opis[:pos2])

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

        baza_danych.commit()
    for i in range(1, 21):
        parse_autoscout24_es(i)
        sleep(3)

    with open('dane.csv', 'a+', encoding='utf-8-sig', newline='') as plik:
        csv_output = csv.writer(plik, delimiter=';')
        csv_output.writerows(head)

    global counter
    print(f'counter = {counter}')

    # parse_autoscout24_es(1)

    return check

def main():
    autoscout24_es()

    baza_danych.close()

if __name__ == "__main__":
    main()