from pydantic import BaseModel, HttpUrl

class Product(BaseModel):
    name: str
    price: float
    image: HttpUrl