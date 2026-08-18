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

    return {"message": "Successfully added to cart", "cart": cart}

# Endpoint 4: List cart value (redis)
@app.get("/cart/{session_id}")
def view_cart(session_id: str):
    cart_key = f"cart:{session_id}"
    cart_data = redis_db.get(cart_key)
    
    if cart_data:
        return json.loads(cart_data)
    return {}

# Endpoint 5: Checkout logic
@app.post("/checkout/{session_id}", response_model=schemas.OrderResponse)
def checkout(session_id: str, db: Session = Depends(get_db)):
    cart_key = f"cart:{session_id}"
    cart_data = redis_db.get(cart_key)
    
    if not cart_data:
        raise HTTPException(status_code=400, detail="Cart is empty; cannot proceed to checkout.")
        
    cart = json.loads(cart_data)
    total_price = 0
    order_items_data = []

    # 1. Read prize value & validate data from database
    for product_id_str, quantity in cart.items():
        product_id = int(product_id_str)
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product ID {product_id} not found")
            
        if product.stock < quantity:
            raise HTTPException(status_code=400, detail=f"Stok {product.name} insufficient")

        # float converter from decimal
        price = float(product.price)
        total_price += price * quantity
        
        order_items_data.append({
            "product_id": product.id,
            "quantity": quantity,
            "price": price
        })

        product.stock -= quantity

    # 2. Create order
    db_order = models.Order(session_id=session_id, total_price=total_price)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # 3. Write product to order
    for item_data in order_items_data:
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            price=item_data["price"]
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)

    # empty cart
    redis_db.delete(cart_key)

    return db_order