from datetime import datetime, timezone
from app.core.database.database import MongoGateway
from app.core.exceptions import PriceLoggingError, NotFoundError
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

    def log_price(self, url: str):
        existing = self.db.find_product(url)
        new = self.scraper.scrape_product(url)

        if not new:
            raise NotFoundError(url=url)

        try:
            previous_price = float(existing["price"].replace("£", "").replace(",", ""))
            current_price = float(new["price"].replace("£", "").replace(",", ""))
            price_diff = current_price - previous_price
            change_dir = "+" if price_diff > 0 else "-"

            data = {
                "product_id": str(existing["_id"]),
                "previous_price": existing["price"],
                "current_price": new["price"],
                "price_diff": price_diff,
                "change_dir": change_dir,
                "date_checked": datetime.now(timezone.utc)
            }

            self.db.log_price(data)

        except Exception as e:
            raise PriceLoggingError(product_id=str(existing["_id"]), error=str(e))



