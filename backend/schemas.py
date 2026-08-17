from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0

# Create & add new product
class ProductCreate(ProductBase):
    pass

# add id from database to product api
class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

#cart system with redis
class CartItem(BaseModel):
    product_id: int
    quantity: int