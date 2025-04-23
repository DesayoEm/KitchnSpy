from datetime import datetime
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
from requests.exceptions import RequestException
from app.data.products import PRODUCTS
from app.data.validation import ProductData
from app.database.conn import Database
from app.infrastructure.log_service import logger
import pprint


class Scraper:
    """Scraper for extracting product information"""
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive'
        }
        self.timeout = timeout
        self.max_retries = max_retries


    def make_request(self, url: str) -> requests.Response|None:
        """
        Make HTTP request with retries.
        Args:
            url: The URL to request
        Returns:
            Response object or None if all attempts fail
        """
        for attempt in range(self.max_retries):
            try:
                session = requests.Session()
                response = session.get(url, headers=self.headers, timeout = self.timeout)
                if response.status_code == 200:
                    return response
                logger.warning(f"Request failed with status code{response.status_code}"
                               f"attempt {attempt + 1}/{self.max_retries}")

            except RequestException as e:
                logger.warning(f"Request error: {str(e)} (attempt {attempt + 1}/{self.max_retries})")

            return None


    @staticmethod
    def extract_product_name(soup: BeautifulSoup) -> str|None:
        """Extract product name using multiple possible selectors."""
        product_name_tag = soup.find('h1', class_='c-dZSbvE')
        if product_name_tag and product_name_tag.text.strip():
            return product_name_tag.text.strip()

        return None


    @staticmethod
    def extract_price(soup: BeautifulSoup) -> str|None:
        """Extract price using multiple possible selectors."""
        price_tag = soup.find('div', class_='c-bULnVn c-bULnVn-icWEoxs-css')
        if price_tag and price_tag.text.strip():
            return price_tag.text.strip()
        return None


    @staticmethod
    def check_availability(soup: BeautifulSoup) -> int|None:
        """Check product availability based on button text."""
        unavailable_btn = soup.find(
            'button',
            class_='c-CKPQg c-CKPQg-hnGDME-size-lg c-CKPQg-ijEYedS-css',
            string=lambda text: text and "E-mail me when available" in text
            )

        available_btn = soup.find(
            'button',
            class_='c-CKPQg c-CKPQg-hnGDME-size-lg c-CKPQg-fTYkTT-leftIcon-true c-CKPQg-iUsihs-css',
            string=lambda text: text and "Add to cart" in text
            )
        page_text = soup.get_text().lower()

        if available_btn or 'add to cart' in page_text:
            return 1
        elif unavailable_btn or 'e-mail me when available' in page_text:
            return 0

        return None


    @staticmethod
    def extract_image_url(soup: BeautifulSoup) -> str|None:
        """Extract product image URL using multiple possible approaches."""
        img_container = soup.find('div', class_='c-dvzBLj')
        if img_container:
            img_tag = img_container.find('img')
            if img_tag and img_tag.get('src'):
                return img_tag['src']

        return None


    def scrape_product(self, url: str) -> ProductData|Dict[str, Any]:
        """
        Scrape product information from the given URL.
        Args:
            url: The product page URL
        Returns:
            Dictionary containing product data or error status
        """
        logger.info(f"scraping URL: {url}")
        response=self.make_request(url)

        if not response:
            logger.error(f"Failed to retrieve page after {self.max_retries} attempts")
            return {'status': 'error', 'message': 'Failed to retrieve page'}
        try:
            soup = BeautifulSoup(response.content, 'html.parser')

            product_name = self.extract_product_name(soup)
            price = self.extract_price(soup)
            image_url = self.extract_image_url(soup)
            availability = self.check_availability(soup)
            data = {
                'name': product_name,
                'product': product_name,
                'url': url,
                'price': price,
                'img_url': image_url,
                'availability': availability,
                'date_checked': datetime.now().isoformat(),
                'status': 'success'
            }
            missing_data = [field for field, value in data.items()
                            if value is None and field != 'status'
                    ]
            if missing_data:
                logger.info(f"Missing data fields: {', '.join(missing_data)}")

            validated = ProductData(**data)
            return validated

        except Exception as e:
            logger.error(f"Error parsing page: {str(e)}")
            return {
                'product': product_name or 'Unknown',
                'url':url,
                'status': 'error',
                'message': f"Error parsing page: {str(e)}"
            }


    def scrape_all_products(self, product_list: list[Dict[str, str]]) -> list[Dict[str, Any]]:
        """
        Scrape multiple products and return their data.
        Args:
            product_list: List of product dictionaries with 'name' and 'url' keys
        Returns:
            List of product data dictionaries
        """
        res = []
        for product in product_list:
            logger.info(f"Processing {product['name']}")
            try:
                data = self.scrape_product(product['url'])
                res.append(data)

            except Exception as e:
                logger.error(f"Failed to scrape {product['name']}: {str(e)}")
                res.append({
                    'product': product['name'],
                    'status': 'error',
                    'message': str(e)
                })
        return res



