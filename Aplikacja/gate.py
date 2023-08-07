import csv
import sys

# wybór samochodu do scrapowania i ewentualnego generowania wykresu
print('Proszę wybrać samochód:\n1.Volkswagen Golf\n2.Toyota RAV4\n3.Audi A4')

while True:
    try:
        a = int(input('Proszę wprowadzić nr samochodu: '))
        if a == 1 or a == 2 or a == 3:
            break
    except ValueError:
        continue

# funkcja do przekazywania wartości wyboru do poszczególnych modułów
def go():
    x = a
    return x

# tworzenie tablicy
head=[]

# atrybuty tabeli do dane.csv
head.append(['Marka', 'Model', 'Rok_prod.', 'Paliwo', 'Przebieg', 'Pojemność', 'Skrzynia biegów', 'Kolor', 'Stan',
             'Cena', 'Kraj', 'Link'])

# wpisanie atrybutów do pliku
with open('dane.csv', 'a+', encoding='utf-8-sig', newline='') as plik:
    csv_output = csv.writer(plik, delimiter=';')
    csv_output.writerows(head)

# start scraperów
from ameryka import cars_com
cars_com()
from hiszpania import autoscout24_es
autoscout24_es()
from polska import otomoto
otomoto()
from niemcy import autoscout24_de
autoscout24_de()
from uk import parkers_uk
parkers_uk()
from rosja import auto_ru
auto_ru()

# inf o pobraniu danych i czy generować wykres
print('---------------------\nDane zostały pobrane.\n---------------------\nCzy wygenerować wykres?')

while True:
    try:
        decyzja = int(input('1.Tak 2.Nie: '))
        if decyzja == 1:
            break
        elif decyzja == 2:
            sys.exit()
    except ValueError:
        continue

# opcje generowania wykresów
print('Proszę wybrać wykres:\n1.Średnia cena aut per kolor\n2.Średnia cena aut per kraj\n3.Średnia cena aut per paliwo'
      '\n4.Średnia cena aut per rocznik\n5.Wygeneruj wszystkie wykresy\n6.Zakończ bez generowania wykresu')

# import modułów wykresów
from kolor_cena import w_kolor_cena
from kraj_cena import w_kraj_cena
from paliwo_cena import w_paliwo_cena
from rocznik_cena import w_rocznik_cena

# funkcja do wybóru opcji generowania
def wykres():
    while True:
        try:
            w = int(input('Proszę wprowadzić nr opcji generowania: '))
            if w == 1:
                w_kolor_cena()
                rwykres()
            elif w == 2:
                w_kraj_cena()
                rwykres()
            elif w == 3:
                w_paliwo_cena()
                rwykres()
            elif w == 4:
                w_rocznik_cena()
                rwykres()
            elif w == 5:
                w_kolor_cena()
                w_kraj_cena()
                w_rocznik_cena()
                w_paliwo_cena()
                break
            elif w == 6:
                sys.exit()
        except ValueError:
            continue

# funkcja powrotu do wyboru opcji generowania
def rwykres():
    while True:
        try:
            print('Czy wygenerować inny wykres?')
            rw = int(input('1.Tak 2.Nie: '))
            if rw == 1:
                wykres()
            elif rw == 2:
                sys.exit()
        except ValueError:
            continue

# start generowania wykresów
wykres()