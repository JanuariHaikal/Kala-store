from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
import json
from redis_client import redis_db

# Automate table creator in PostgreSQL
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kala Store API", version="0.1.0")

@app.get("/")
def read_root():
    return {"brand": "Kala", "status": "online"}

# Endpoint 1: Add new product
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

# Endpoint 2: List all product
@app.get("/products/", response_model=list[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

# Endpoint 3: Cart system (redis)
@app.post("/cart/{session_id}")
def add_to_cart(session_id: str, item: schemas.CartItem):
    cart_key = f"cart:{session_id}"

    # keep data from past condition
    cart_data = redis_db.get(cart_key)
    cart = json.loads(cart_data) if cart_data else {}

    product_id_str = str(item.product_id)

    # Add quantity product if exsisting, if not add new
    if product_id_str in cart:
        cart[product_id_str] += item.quantity
    else:
        cart[product_id_str] = item.quantity

    # Save to redis and set exit time 24h (86400 second)
    redis_db.set(cart_key, json.dumps(cart), ex=86400)

    return {"message": "Berhasil ditambahkan ke keranjang", "cart": cart}

# Endpoint 4: List cart value (redis)
@app.get("/cart/{session_id}")
def view_cart(session_id: str):
    cart_key = f"cart:{session_id}"
    cart_data = redis_db.get(cart_key)
    
    if cart_data:
        return json.loads(cart_data)
    return {}