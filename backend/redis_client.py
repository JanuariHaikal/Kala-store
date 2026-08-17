import redis
import os

# Ambil URL Redis dari environment Docker
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Setup koneksi Redis
redis_db = redis.from_url(REDIS_URL, decode_responses=True)