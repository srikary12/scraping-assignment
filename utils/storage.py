from abc import ABC, abstractmethod
from models import product
import json

class Storage(ABC):
    @abstractmethod
    def bulk_update(self, products:list[product.Product]) -> int:
        pass

class JSONStorage(Storage):
    def __init__(self, filename: str = "db.json"):
        self.filename = filename

    def _load_products(self) -> dict[str, product.Product]:
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return {p['name']: product.Product(**p) for p in data}
        except FileNotFoundError:
            return {}
    
    def bulk_update(self, products):
        existing_products = self._load_products()
        updated_count = 0

        for product in products:
            if product.name in existing_products:
                if existing_products[product.name].price != product.price:
                    existing_products[product.name] = product
                    updated_count += 1
            else:
                existing_products[product.name] = product
                updated_count += 1
        
        with open(self.filename, 'w') as f:
            json.dump([p.dict() for p in existing_products,values()], f, indent=4)
        return updated_count