from datetime import datetime, timezone
from app.core.database.database import MongoGateway
from app.core.exceptions import PriceLoggingError, NotFoundError
from app.crud.scrape import ScraperCrud


class HistoryCrud:
    def __init__(self):
        self.db = MongoGateway()
        self.scraper = ScraperCrud()


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


    def log_prices(self, products: list):
        for product in products:
            self.log_price(product['url'])



