from bs4 import BeautifulSoup
import requests
from pathlib import Path
from dotenv import load_dotenv
import os
import time
from telegramBot import bot

load_dotenv()
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
DATA = []
CHAT_ID = os.getenv("CHAT_ID")
bot_token = os.getenv("TELEGRAM_TOKEN")

# функция для получения html
def get_html(url):
    r = requests.get(url)
    return r.text


# функция подсчета количества страниц
# используем библиотеку BeautifulSoup для поиска html тегов на странице
#
def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')  # определяем объект soup
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
            bot.send_message(int(CHAT_ID), f'Цена: {post["price"]}\nАдрес: {post["address"]}\nПлощадь: '
                                           f'{post["square"]}\n Ссылка: {post["url"]}')
            time.sleep(5)

# основная функция
# базовый url для Астаны имеет вид https://krisha.kz/prodazha/kvartiry/astana/
# к нему добавляется запрос query_part и еще дальше идет блок со страницами page_part
#
def main():
    url = 'https://krisha.kz/arenda/kvartiry/almaty/?das[live.furniture]=1&das[live.rooms]=1&das[live.square][from]=30&das[price][from]=100000&das[price][to]=180000&das[rent.period]=2&areas=p43.196219,76.783591,43.240662,76.784278,43.255219,76.794578,43.273033,76.816894,43.279304,76.837493,43.285825,76.885215,43.293851,76.926414,43.296860,76.951133,43.296860,76.976539,43.285575,76.981002,43.262746,76.981002,43.240411,76.980315,43.234387,76.974822,43.215055,76.891051,43.198982,76.855002,43.198480,76.782218,43.196219,76.783591&zoom=12&lat=43.23978&lon=76.87442'
    page_part = '&page='

    while True:
        try:
            total_pages = get_total_pages(get_html(url))
            #
            for i in range(1, total_pages):
                if i == 1:
                    url_gen = url
                else:
                    url_gen = url + page_part + str(i)
                html = get_html(url_gen)
                get_page_data(html)
            time.sleep(120)
        except Exception as e:
            print(e)
            exit()
# блок main
if __name__ == '__main__':
    main()


