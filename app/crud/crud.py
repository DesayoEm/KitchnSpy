from pprint import pprint

from app.core.data.products import PRODUCTS
from app.database.conn import Database
from app.core.services.scraper import Scraper

class ScraperCrud:
    def __init__(self):
        self.db = Database()
        self.scraper=Scraper(timeout=30, max_retries=3)

    def scrape_all_products(self, products):
        result = self.scraper.scrape_all_products(products)
        for scraped_product in result:
            product_id = self.db.insert_or_update_product(scraped_product)
            if product_id:
                self.db.log_price(product_id, scraped_product)
        return pprint(result)
            # current_price = ?
            # previous_price = ?
            #
            #
            # change_dir = ("+" if self.parser.previous_price > self.parser.current_price
            #             # else "-")

ac = ScraperCrud()
print(ac.scrape_all_products(PRODUCTS))