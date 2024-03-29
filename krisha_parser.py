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
URL = os.getenv("URL")


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
                         class_='paginator') 
        pages = len(divs.find_all('a', class_='paginator__btn')) 
        return int(pages) 
    except:
        return 2


def is_new(post):
    for item in DATA:
        if item['url'] == post['url']:
            return False
    DATA.append(post)
    return True


# функция-парсер html
def get_page_data(html):
    global DATA
    soup = BeautifulSoup(html, 'lxml')  
    divs = soup.find('section', class_='a-list')
    ads = divs.find_all('div', class_='a-card__inc')

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
    url = URL
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


