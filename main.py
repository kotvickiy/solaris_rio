import os
import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent as UA
from send_telegram import send_telegram


def save(data):
    with open('solaris_rio.csv', 'w'):
        for i in data:
            with open('solaris_rio.csv', 'a', encoding='utf-8', newline='') as file:
                order = ['name', 'price', 'year', 'link']
                writer = csv.DictWriter(file, fieldnames=order)
                writer.writerow(i)


def lst_old():
    with open('solaris_rio.csv', encoding='utf-8') as file:
        order = ['name', 'price', 'year', 'link']
        reader = csv.DictReader(file, fieldnames=order)
        return [i for i in reader]


def get_html():
    htmls = []
    urls = [r'https://auto.ru/ekaterinburg/cars/all/?year_from=2012&year_to=2017&catalog_filter=mark%3DHYUNDAI%2Cmodel%3DSOLARIS%2Cgeneration%3D6847474&catalog_filter=mark%3DHYUNDAI%2Cmodel%3DSOLARIS%2Cgeneration%3D20162370&seller_group=PRIVATE&transmission=ROBOT&transmission=AUTOMATIC&transmission=VARIATOR&transmission=AUTO&sort=cr_date-desc&displacement_from=1500',
            r'https://auto.ru/ekaterinburg/cars/kia/rio/all/?year_from=2012&year_to=2017&displacement_from=1500&seller_group=PRIVATE&transmission=ROBOT&transmission=AUTOMATIC&transmission=VARIATOR&transmission=AUTO&sort=cr_date-desc',
            r'https://www.avito.ru/sverdlovskaya_oblast/avtomobili/hyundai/solaris/sedan-ASgBAQICAkTgtg2imzHitg3kmzEBQOa2DRTKtyg?cd=1&f=ASgBAQECA0TyCrCKAeC2DaKbMeK2DeSbMQJA5rYNFMq3KPC2DTTwtyjytyjutygCRfgCGHsiZnJvbSI6NjA0NSwidG8iOjE5Nzc1fbwVGHsiZnJvbSI6MTU3ODUsInRvIjpudWxsfQ&s=104&user=1',
            r'https://www.avito.ru/sverdlovskaya_oblast/avtomobili/kia/rio/sedan-ASgBAQICAkTgtg3KmCjitg3KrigBQOa2DRTKtyg?cd=1&f=ASgBAQECA0TyCrCKAeC2DcqYKOK2DcquKAJA5rYNFMq3KPC2DTTwtyjytyjutygCRfgCGHsiZnJvbSI6NjA0NSwidG8iOjE5Nzc1fbwVGHsiZnJvbSI6MTU3ODUsInRvIjpudWxsfQ&s=104&user=1']
    for url in urls:
        headers = {'user-agent': UA().chrome}
        response = requests.get(url, headers=headers)
        htmls.append(response.content.decode('utf-8'))
    return htmls


def get_data(htmls):
    all_lst = []
    for html in htmls:
        soup = BS(html, 'lxml')
        if soup.find('div', class_='ListingCars_outputType_list'):
            cards = soup.find('div', class_='ListingCars_outputType_list').find_all('div', class_='ListingItem')
            for card in cards:
                name = card.find('h3', class_='ListingItem__title').text
                price = card.find('div', class_='ListingItemPrice__content').text.replace('₽', '').replace(' ', '').strip()
                year = card.find('div', class_='ListingItem__year').text.strip()
                link = card.find('h3', class_='ListingItem__title').a['href']
                data = {'name': name,
                        'price': price,
                        'year': year,
                        'link': link}
                all_lst.append(data)
        elif soup.find('div', class_='index-content-_KxNP'):
            cards = soup.find('div', class_='index-content-_KxNP').find_all('div', {'data-marker': 'item'})
            page_title_count = soup.find('span', class_='page-title-count-oYIga').text.strip()
            for card in cards[:int(page_title_count)]:
                name = card.h3.text.split(',')[0].strip()
                price = card.find('span', class_='price-text-E1Y7h text-text-LurtD text-size-s-BxGpL').text.replace('₽', '').replace(' ', '').strip()
                year = card.h3.text.split(',')[1].strip()
                link = 'https://www.avito.ru' + card.find('div', class_='iva-item-titleStep-_CxvN').a['href']
                data = {'name': name,
                        'price': price,
                        'year': year,
                        'link': link}
                all_lst.append(data)
    return all_lst


def verify_news():
    ref_lst = lst_old()
    new_lst = get_data(get_html())


    freshs_lst = []
    for new in new_lst:
        if new not in ref_lst:
            freshs_lst.append(new)
    if freshs_lst:
        save(new_lst)
        for i in freshs_lst:
            send_telegram(f"{i['name']} {i['price']} {i['link']}")


def run():    
    try:
        if os.path.exists('solaris_rio.csv'):
            verify_news()
        else:
            save(get_data(get_html()))
    except Exception as ex:
        now = datetime.now()
        print(str(now.strftime('%d-%m-%Y %H:%M:%S ')) + str(ex))


def main():
    run()


if __name__ == '__main__':
    main()
