import requests
from bs4 import BeautifulSoup
import re
import json

from ..data.products import *

products = [
    {'name': 'Mini Chopper', 'url': chopper_url},
    {'name': 'Evergreen Artisan', 'url': evergreen_url},
    {'name': 'Classic White', 'url': classic_url},
    {'name': 'Glass Mixing bowl', 'url': bowl_url}
]

class Scraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }

    def scrape_url(self, url: str):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            product_name_tag = soup.find('h1', class_='c-dZSbvE')
            price_tag = soup.find('div', class_='c-bULnVn c-bULnVn-icWEoxs-css')
            img_container = soup.find('div', class_='c-dvzBLj')
            img_tag = img_container.find('img') if img_container else None

            data = {
                'name': product_name_tag.text.strip() if product_name_tag else None,
                'price': price_tag.text.strip() if price_tag else None,
                'img_url': img_tag['src'] if img_tag else None
            }

            if not data['price']:
                print("Price tag not found.")
            if not data['name']:
                print("Product name not found.")
            if not data['img_url']:
                print("Product image not found.")

            return data
        else:
            print("Failed to retrieve page:", response.status_code)
            return None


scraps = Scraper()
datas = [item for item in scraps.scrape_url(chopper_url).items()]
for item in datas:
    print(item)


