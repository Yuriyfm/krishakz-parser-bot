from bs4 import BeautifulSoup
import requests
from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import datetime
import time
from telegramBot import bot

load_dotenv()
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
DATA = []
CHAT_ID = os.getenv("CHAT_ID")
bot_token = os.getenv("TELEGRAM_TOKEN")


def print_time():
    date_time = datetime.fromtimestamp(time.time())
    str_date_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")
    print("Бот работает", str_date_time)


print_time()


def get_html(url):
    r = requests.get(url)
    return r.text


def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        divs = soup.find('nav',
                         class_='paginator')  # находим на странице первый объект nav с именем класса paginator-public
        pages = len(divs.find_all('a', class_='paginator__btn')) # находим на странице все теги "a" с именем класса paginator-page-btn, из них выбираем элемент с индексом [-2] это будет последняя страница
        return int(pages)  # возвращаем полученное значение
    except:
        return 2


def is_new(post):
    for item in DATA:
        if item['url'] == post['url']:
            return False
    DATA.append(post)
    return True


# функция получения данных с сайта, используем библиотеку BeautifulSoup, она позволяет выполнять поиск по html тегам
def get_page_data(html):
    global DATA
    soup = BeautifulSoup(html, 'lxml')  # определяем объект soup
    divs = soup.find('section', class_='a-list')  # находим тег section с именем класса a-list
    ads = divs.find_all('div', class_='a-card__inc')  # в найденном объекте ищем все div с классом a-card__inc
    # запускаем цикл по всем найденным полям, которые нас интересуют
    # т.к. ссылка состоит 3-комнатная квартира, 79.4 м², 5/5 эт. я решил ее разделить на поля квартира, площадь, этаж
    # далее выбираем цену, адрес и описание
    #
    for ad in ads:
        try:
            div = ad.find('a', class_='a-card__title').text
            square = div.split(",")[1]
        except:
            square = ''
        try:
            price = ad.find('div', class_='a-card__price').text.strip()
        except:
            price = ''
        try:
            address = ad.find('div', class_='a-card__subtitle').text.strip()
        except:
            address = ''
        try:
            div = ad.find('div', class_='a-card__header-left')
            url = "https://krisha.kz" + div.find('a').get('href')
            # tel = ''
        except:
            url = ''
            # tel = ''

        post = {'price': price,
            'square': square,
            'address': address,
            'url': url,
              }

        if len(DATA) == 0:
            DATA.append(post)

        if is_new(post):
            print(post)
            try:
                bot.send_message(int(CHAT_ID), f'Цена: {post["price"]}\nАдрес: {post["address"]}\nПлощадь: '
                                               f'{post["square"]}\n Ссылка: {post["url"]}')
            except Exception as e:
                print(e)
            time.sleep(3)


def main():
    url = 'https://krisha.kz/arenda/kvartiry/almaty/?bounds=&das[live.furniture]=1&das[live.rooms]=1&das[live.square][from]=30&das[price][from]=100000&das[price][to]=180000&das[rent.period]=2&areas=p43.197977,76.796294,43.229366,76.775008,43.255972,76.788055,43.280558,76.798698,43.304949,76.815352,43.317920,76.884185,43.314161,76.918175,43.310901,76.952850,43.296860,76.976539,43.285575,76.981002,43.265506,76.987525,43.245431,76.988898,43.220579,76.981688,43.190944,76.906844,43.190442,76.880580,43.191195,76.865388,43.190567,76.854358,43.189939,76.840926,43.189437,76.810370,43.197977,76.796294&zoom=12&lat=43.23789&lon=76.86172'
    page_part = '&page='

    while True:
        start_time = time.time()
        if time.time() - start_time % 600:
            print_time()
        try:
            total_pages = get_total_pages(get_html(url))
            for i in range(1, total_pages):
                if i == 1:
                    url_gen = url
                else:
                    url_gen = url + page_part + str(i)
                html = get_html(url_gen)
                get_page_data(html)
            time.sleep(10)
        except Exception as e:
            print(e)
            bot.send_message(int(CHAT_ID), f'Бот упал с ошибкой:\n{e}')
            exit()
# блок main
if __name__ == '__main__':
    main()


