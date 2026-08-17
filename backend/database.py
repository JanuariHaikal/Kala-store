import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Ambil URL dari environment variable Docker (atau pakai default lokal kalau kosong)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://kala_admin:password_db_super_aman_123@db:5432/kala_ecommerce"
)

# Setup Engine Database
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency buat di-inject ke route API nanti
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()