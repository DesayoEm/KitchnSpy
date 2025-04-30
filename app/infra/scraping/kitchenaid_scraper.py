from datetime import timezone, datetime
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from requests.exceptions import RequestException
from app.shared.exceptions import FailedRequestError, ParsingError
from app.infra.log_service import logger


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



    def make_request(self, url: str) -> requests.Response:
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
                response = session.get(url, headers=self.headers, timeout=self.timeout)

                if response.status_code == 200:
                    return response

                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed with status {response.status_code}")

                if attempt < self.max_retries - 1:
                    sleep_time = 2 ** attempt
                    logger.info(f"Waiting {sleep_time} seconds before retrying...")
                    time.sleep(sleep_time)


            except RequestException as e:
                logger.warning(f"Request exception on attempt {attempt + 1}/{self.max_retries}: {e}")

        raise FailedRequestError(
            detail=f"All {self.max_retries} attempts failed for URL: {url}",
            attempt=self.max_retries,
            tries=self.max_retries
        )


    @staticmethod
    def extract_product_name(soup: BeautifulSoup) -> str|None:
        """Extract product."""
        product_name_tag = soup.find('h1', class_='c-dZSbvE')
        if product_name_tag and product_name_tag.text.strip():
            return product_name_tag.text.strip()

        return None


    @staticmethod
    def extract_price(soup: BeautifulSoup) -> str|None:
        """Extract price."""
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
            return True
        elif unavailable_btn or 'e-mail me when available' in page_text:
            return False

        return None


    @staticmethod
    def extract_image_url(soup: BeautifulSoup) -> str|None:
        """Extract product image URL"""
        img_container = soup.find('div', class_='c-dvzBLj')
        if img_container:
            img_tag = img_container.find('img')
            if img_tag and img_tag.get('src'):
                return img_tag['src']

        return None


    def scrape_product(self, product: dict) -> dict:
        """
        Scrape product information from the given URL.
        Args:
            product: Dictionary of the product name and  URL
        Returns:
            Dictionary containing product data or error status
        """
        name , url = product['name'], product['url']
        logger.info(f"Scraping for {name}")
        response=self.make_request(url)

        try:
            soup = BeautifulSoup(response.content, 'html.parser')

            product_name = self.extract_product_name(soup)
            price = self.extract_price(soup)
            image_url = self.extract_image_url(soup)
            availability = self.check_availability(soup)
            data = {
                'name': name,
                'product_name': product_name,
                'url': url,
                'price': price,
                'img_url': image_url,
                'is_available': availability,
                'date_checked': datetime.now(timezone.utc),
                'status': 'success'
            }
            missing_data = [field for field, value in data.items()
                            if value is None and field != 'status'
                    ]
            if missing_data:
                logger.info(f"Missing data fields: {', '.join(missing_data)}")


            return data

        except Exception as e:
            raise ParsingError(url = url, error = str(e))


    def scrape_products(self, product_list: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Scrape multiple products and return their data.
        Args:
            product_list: List of product dictionaries with 'name' and 'url' keys
        Returns:
            List of product data dictionaries
        """
        results = []
        for product in product_list:
            name, url = product['name'], product['url']
            logger.info(f"Scraping for {product['name']}")
            try:
                data = self.scrape_product(product)
                results.append(data)

            except FailedRequestError as e:
                logger.error(f"Failed to request {name}: {str(e)}")

            except ParsingError as e:
                logger.error(f"Failed to parse {name}: {str(e)}")
                continue

            except Exception as e:
                logger.error(f"Unexpected error processing {name}: {str(e)}")
                continue


        return results



