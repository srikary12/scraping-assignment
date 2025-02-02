
import redis

class PriceCache:
    def __init__(self):
        self.redis = redis.Redis()
    
    def get(self, product_name: str) -> str | None:
        return self.redis.get(product_name)
    
    def set(self, product_name: str, price: float) -> None:
        self.redis.set(product_name, price)

