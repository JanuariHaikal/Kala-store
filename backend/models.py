from sqlalchemy import Column, Integer, String, Text, Numeric
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False) # Format desimal buat harga
    stock = Column(Integer, default=0)