from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db

# Perintah ajaib buat bikin tabel otomatis di PostgreSQL saat API nyala
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kala Store API", version="0.1.0")

@app.get("/")
def read_root():
    return {"brand": "Kala", "status": "online"}

# Endpoint 1: Tambah Produk Baru
@app.post("/products/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Endpoint 2: Lihat Semua Produk
@app.get("/products/", response_model=list[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products