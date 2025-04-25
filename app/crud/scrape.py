
from app.core.database.mongo_gateway import MongoGateway
from app.core.services.scraper import Scraper



class ScraperCrud:
    def __init__(self):
        self.db = MongoGateway()
        self.scraper=Scraper(timeout=30, max_retries=3)


    def scrape_product(self, url):
        scraped = self.scraper.scrape_product(url)
        return self.db.insert_product(scraped)


    def scrape_all_products(self, products):
        result = self.scraper.scrape_all_products(products)
        for scraped_product in result:
           self.db.insert_product(scraped_product)

        return result


    def update_product_info(self, url):
        existing = self.db.find_product(url)
        updated_data = self.scrape_product(url)

        required_fields = ["name", "url", "price", "availability", "img_url"]
        if any(updated_data.get(field) is None for field in required_fields):
            return self.db.update_product({"url": url}, updated_data)

        else:
            return self.db.replace_product({"url": url}, updated_data)


