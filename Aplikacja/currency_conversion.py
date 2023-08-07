from bs4 import BeautifulSoup
from requests import get

# funcja do pobierania tabeli A kursów
def create_dict():
    url = 'https://www.nbp.pl/home.aspx?f=/kursy/kursya.html'
    page = get(url)
    bs = BeautifulSoup(page.content, 'html.parser')
    currencyDict = {}

    table = bs.find('tbody')
    values = table.find_all('tr')
    for value in values:
        value_name = value.find('td', class_='right').get_text()[2:]
        exchange_rate = round(float(value.find('td', class_='right').find_next('td').get_text().replace(',', '.')), 2)

        # wgranie do słownika
        currencyDict[value_name] = exchange_rate
        # print(value_name,exchange_rate)
    return currencyDict

# funkcja przekonwertowania kursu
def convert(currency, amount, dict):
    for value, key in dict.items():
        if value == currency:
            return amount * key