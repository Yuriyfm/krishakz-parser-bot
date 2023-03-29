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
    url = 'https://krisha.kz/arenda/kvartiry/almaty/?das[_sys.hasphoto]=1&das[floor_not_first]=1&das[live.furniture]=1&das[live.rooms]=1&das[live.square][from]=33&das[price][from]=140000&das[price][to]=200000&das[who]=1&areas=p43.279932,76.964170,43.280560,76.963483,43.276546,76.923657,43.270024,76.910955,43.254467,76.906491,43.237652,76.825810,43.233887,76.819974,43.222338,76.818944,43.203505,76.833020,43.201244,76.855680,43.219576,76.885549,43.234891,76.962453,43.242170,76.974469,43.255220,76.979276,43.280560,76.963826,43.279932,76.964170&zoom=13&lat=43.22758&lon=76.87427'
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


