from fastapi import FastAPI, Depends
from bs4 import BeautifulSoup
from tenacity import retry, wait_fixed, stop_after_attempt
import requests
import os
import uuid

from .schemas import Product, ScraperSettings
from .utils import JSONStorage, PriceCache, validate_api_key
from .external_services import ConsoleNotification

app = FastAPI()

class WebScraper:
    def __init__(
        self,
        settings: ScraperSettings,
        storage: JSONStorage,
        notifier: ConsoleNotification,
        cache: PriceCache,
        base_url: str = "https://dentalstall.com/shop/page/",
    ):
        self.settings = settings
        self.storage = storage
        self.notifier = notifier
        self.cache = cache
        self.base_url = base_url
        self.image_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
    
    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3))
    def _scrape_page(self, page: int) -> bytes:
        url = f"{self.base_url}{page}"
        proxies = {"http": self.settings.proxy, "https": self.settings.proxy} if self.settings.proxy else None
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()
        return response.content
    
    def _parse_page(self, html: bytes) -> list[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        for product_div in soup.find_all('div', class_='product-inner'):
            name = product_div.find('h2', class_='woo-loop-product__title').text.strip()
            price_str = product_div.find('span', class_='woocommerce-Price-amount').text.strip()
            price = float(price_str.replace('₹', ''))
            image = product_div.find('img')['data-lazy-src']
            products.append(Product(name=name, price=price, image=image))
        return products
    
    def _download_image(self, url: str) -> str:
        response = requests.get(url)
        if response.status_code == 200:
            image_name = os.path.basename(url)
            if not image_name or image_name == '/':
                image_name = f"image_{uuid.uuid4()}.jpg"
            else:
                name, ext = os.path.splitext(image_name)
                image_name = f"{name}_{uuid.uuid4()}{ext}"
            image_path = os.path.join(self.image_dir, image_name)
            with open(image_path, 'wb') as f:
                f.write(response.content)
            return image_path
        else:
            raise Exception(f"Failed to download image from {url}")

    def scrape(self) -> None:
        products_to_update = []
        for page in range(1, self.settings.page_limit + 1):
            try:
                html = self._scrape_page(page)
                scraped_products = self._parse_page(html)
                for product in scraped_products:
                    cached_price = self.cache.get(product.name)
                    if cached_price is None or cached_price.decode() != product.price:
                        image_path = self._download_image(product.image)
                        product.image = image_path
                        products_to_update.append(product)
                        self.cache.set(product.name, product.price)
            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                continue

        if products_to_update:
            updated_count = self.storage.bulk_update(products_to_update)
            self.notifier.notify(f"Successfully updated {updated_count} products.")
        else:
            self.notifier.notify("No new products or updates found.")

@app.post("/scrape", dependencies=[Depends(validate_api_key)])
def run_scraper(settings: ScraperSettings):
    storage = JSONStorage()
    notifier = ConsoleNotification()
    cache = PriceCache()
    scraper = WebScraper(settings, storage, notifier, cache)
    scraper.scrape()
    return {"status": "Scraping completed successfully"}