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

def w_rocznik_cena():
    # połączenie z serwerem i bazą
    baza_danych = pyodbc.connect('Driver={SQL Server};''Server=LAPTOP-AVN5LJKQ;''Database=mgr_aplikacja;'
                                 'Trusted_Connection=yes')

    cursor = baza_danych.cursor()

    zapytanie = f'select rok_prod, AVG(cena) from dane where marka like {marka} and model like {model} group by rok_prod order by rok_prod'

    # wykonanie zapytania
    cursor.execute(zapytanie)

    # port => zaciąganie danych z bazy danych
    wynik_dane = cursor.fetchall()

    # port => zapis .csv
    with open(f'c_rocznik_{m}.csv', 'w', newline='') as plik:
        for wiersz in wynik_dane:
            csv.writer(plik, delimiter=';').writerow(wiersz)

    # zakończenie połączenia z serwerem
    baza_danych.close()

    # odczyt danych z pliku
    dane = np.genfromtxt(f'c_rocznik_{m}.csv', delimiter=';', dtype=None)

    x = dane[:, 0]
    y = dane[:, 1]

    # sub-wykres do nakładania opisów
    ax = plt.subplot()

    # tytuł wykresu
    ax.set_title('Średnia cena aut w zależności od roku produkcji (w PLN)')

    # etykiety danych
    for i in range(len(x)):
        ax.text(x[i], y[i]//1.1, y[i], size=7, ha = 'center', rotation = 90)

    # przekazanie danych do wykresu
    plt.bar(x, y, tick_label = x)

    # opisy i ich placement na osi x
    plt.setp(ax.get_xticklabels(), rotation=60, ha='center', size = 8)

    # rysowanie wykresu
    plt.show()

def main():
    w_rocznik_cena()

if __name__ == "__main__":
    main()