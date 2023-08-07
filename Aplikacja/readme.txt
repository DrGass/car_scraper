===========
SPIS TREŚCI
===========

1. Informacje o aplikacji
2. Opis modułów
2.1. Scrapery
2.2. Wykresy
2.3. User Interface
2.4. Launcher
3. Obsługa aplikacji

=========================
1. INFORMACJE O APLIKACJI
=========================

Aplikacja ta stanowi część pracy magisterskiej.

Aplikacja pobiera informacje z ofert zamieszczonych na motoryzacyjnych stronach internetowych, a następnie zapisuje je w pliku .CSV oraz na serwerze MS SQL w celu dalszej analizy. Istnieje takze możliwość wygenerowania następujących wykresów zaraz po zakończeniu pobierania danych:
1. cena per kolor
2. cena per kraj
3. cena per rodzaj paliwa
4. cena per rok produkcji

===============
2. OPIS MODUŁÓW
===============

-------------
2.1. Scrapery
-------------

Aplikacja składa się z sześciu głównych scraperów pobierających dane z serwisów internetowych oraz jednego dodatkowego. 

Dodatkowy scraper zajmuje się pobieraniem informacji z tabeli A - średnich kursów walut obcych z oficjalnej strony NBP, a także konwersją pobranych cen aut w walutach obcych na PLN.

Kody głównych scraperów znajdują się w plikach:
1. ameryka.py
2. hiszpania.py
3. polska.py
4. niemcy.py
5. uk.py
6. rosja.py

Kod scrapera walutowego znajduje się w pliku currency_conversion.py

------------
2.2. Wykresy
------------

Aplikacja posiada wbudowane 4 wykresy wspomniane w sekcji "1. Informacje o aplikacji". 

Kod poszczególnych wykresów znajduje się w następujących plikach:
1. kolor_cena.py
2. kraj_cena.py
3. paliwo_cena.py
4. rocznik_cena.py

-------------------
2.3. User Interface
-------------------

Kod zawierający interfejs użytkownika oraz wywołujący scrapery i ewentualnie wykresy znajduje się w pliku gate.py

------------
2.4 Launcher
------------

Moduł ten wywołuje gate.py i stanowi pewnego rodzaju zabezpieczenie przed ingerencją użytkownika. Proszę traktować plik wykonawczy.py, jako ikonę na pulpicie oraz co istotne rozpoczynać działanie aplikacji z tego pliku.

====================
3. OBSŁUGA APLIAKCJI
====================

1. Jak zostało wspomniane w sekcji 2.4, proszę uruchamiać działanie aplikacji poprzez wywołanie kodu znajdującego się w pliku wykonawczy.py

2. Po uruchomieniu aplikacji w terminalu pokaże się opcja wyboru auta na temat, którego scrapery będą pobierać informacje. Aplikacja wyświetla licznik ile ofert aut dla danego kraju zostało pobranych oraz informacje o zakończeniu pobierania

3. Po zakończonym pobieraniu informacji aplikacja przedstawia możliwość generowania wykresów. Opcja "Nie" kończy działanie aplikacji. Odpowiedź użytkownika "Tak" powoduje przejście do możliwości wyboru wykresów, który ma być wygenerowany.

4. Aplikacja zapisuje dane na serwerze, gdzie użytkownik może dokonać bardziej zaawansowanych zapytań w celu dalszej analizy. Pobrane dane są także zapisywane w pliku dane.csv, który jest możliwy do otwarcia w programie MS Excel. Dodatkowo, moduł generujący wykresy tworzy pliki z danymi, które posłużyły do stworzenia danego wykresu w celu umożliwienia wygenerowania własnych wykresów przez użytkownika.

Wszystkie pliki generowane przez aplikację zapisywane są w folderze głównym aplikacji pod następującymi nazwami:
1. Pobrane dane => dane.csv
2. Wykres cena per kolor => c_kolor_[nazwa marki/modelu].csv
3. Wykres cena per kraj => c_kraj_[nazwa marki/modelu].csv
4. Wykres cena per rodzaj paliwa => c_paliwo_[nazwa marki/modelu].csv
5. Wykres cena per rok produkcji => c_rocznik_[nazwa marki/modelu].csv
