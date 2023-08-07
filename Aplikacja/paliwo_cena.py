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

def w_paliwo_cena():
    # połączenie z serwerem i bazą
    baza_danych = pyodbc.connect('Driver={SQL Server};''Server=LAPTOP-AVN5LJKQ;''Database=mgr_aplikacja;'
                                 'Trusted_Connection=yes')

    cursor = baza_danych.cursor()

    zapytanie = f"select paliwo, AVG(cena) from dane where marka like {marka} and model like {model} group by paliwo"

    # wykonanie zapytania
    cursor.execute(zapytanie)

    # port => zaciąganie danych z bazy danych
    wynik_dane = cursor.fetchall()

    # port => zapis .csv
    with open(f'c_paliwo_{m}.csv', 'w', newline='') as plik:
        for wiersz in wynik_dane:
            csv.writer(plik, delimiter=';').writerow(wiersz)

    # zakończenie połączenia z serwerem
    baza_danych.close()

    # odczyt danych z pliku
    dane = np.genfromtxt(f'c_paliwo_{m}.csv', delimiter=';', dtype='<U19')

    # zliczanie r_paliw na potrzeby osi x
    paliwo = []
    for p in range(1, len(dane)+1):
        paliwo.append(p)

    x = paliwo
    y = dane[:, 1].astype(int)

    # sub-wykres do nakładania opisów
    ax = plt.subplot()

    # tytuł wykresu
    ax.set_title('Średnia cena aut w zależności od rodzaju paliwa (w PLN)')

    # etykiety danych
    for i in range(len(x)):
        ax.text(x[i], y[i]//10, y[i], size=8, ha = 'center', rotation = 90)

    # przekazanie danych do wykresu
    plt.bar(x, y, tick_label=dane[:, 1])

    # opisy na osi x - nazwy paliw
    ax.set_xticklabels(dane[:, 0])

    # opisy i ich placement na osi x
    plt.setp(ax.get_xticklabels(), rotation=20, ha='center', size=8)

    # rysowanie wykresu
    plt.show()

def main():
    w_paliwo_cena()

if __name__ == "__main__":
    main()