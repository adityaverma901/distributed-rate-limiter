from app.redis_client import RedisClient
from fastapi import FastAPI
from app.middleware import RateLimitMiddleware

app = FastAPI(title="Rate Limiter Demo")

redis_client = RedisClient(url="redis://localhost:6380")

app.add_middleware(RateLimitMiddleware, redis_client=redis_client, capacity=5, refill_rate=1.0)

@app.get("/ping")
async def ping():
    return {"message": "pong"}