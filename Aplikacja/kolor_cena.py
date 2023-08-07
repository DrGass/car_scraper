import csv
import pyodbc
import numpy as np
import matplotlib.pyplot as plt

# wybór auta do zapytania by wygenerować wykres
import gate
auto = gate.go()

if auto == 1:
    marka = "'%Volkswagen%'"
    model = "'%Golf%'"
elif auto == 2:
    marka = "'%Toyota%'"
    model = "'%RAV%'"
elif auto == 3:
    marka = "'%Audi%'"
    model = "'%A4%'"

# modyfikowanie zmiennej model do nazwy pliku
m = model.replace("'", '').replace('%', '')

def w_kolor_cena():

    # połączenie z serwerem i bazą
    baza_danych = pyodbc.connect('Driver={SQL Server};''Server=LAPTOP-AVN5LJKQ;''Database=mgr_aplikacja;'
                                 'Trusted_Connection=yes')

    cursor = baza_danych.cursor()

    zapytanie = f"select kolor, AVG(cena) from dane where kolor not like '' and marka like {marka} and model like {model} group by kolor"

    # wykonanie zapytania
    cursor.execute(zapytanie)

    # port => zaciąganie danych z bazy danych
    wynik_dane = cursor.fetchall()

    # port => zapis .csv
    with open(f'c_kolor_{m}.csv', 'w', newline='') as plik:
        for wiersz in wynik_dane:
            csv.writer(plik, delimiter=';').writerow(wiersz)

    # zakończenie połączenia z serwerem
    baza_danych.close()

    # odczyt danych z pliku
    dane = np.genfromtxt(f'c_kolor_{m}.csv', delimiter=';', dtype='<U19')

    # zliczanie kolorów na potrzeby osi x
    kolory = []
    for k in range(1, len(dane)+1):
        kolory.append(k)

    x = kolory
    y = dane[:, 1].astype(int)

    # sub-wykres do nakładania opisów
    ax = plt.subplot()

    # tytuł wykresu
    ax.set_title('Średnia cena aut w zależności od koloru (w PLN)')

    # etykiety danych
    for i in range(len(x)):
        ax.text(x[i], y[i]//10, y[i], size=8, ha='center', rotation=90)

    # przekazanie danych do wykresu
    plt.bar(x, y, tick_label=dane[:, 1])

    # opisy na osi x - nazwy kolorów
    ax.set_xticklabels(dane[:, 0])

    # opisy i ich placement na osi x
    plt.setp(ax.get_xticklabels(), rotation=30, ha='center', size=8)

    # rysowanie wykresu
    plt.show()

def main():
    w_kolor_cena()

if __name__ == "__main__":
    main()