from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0

# Dipakai saat nambah produk baru
class ProductCreate(ProductBase):
    pass

# Dipakai saat API ngirim data produk (ada tambahan ID dari database)
class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True