from fastapi import FastAPI
from app.middleware import RateLimitMiddleware

app = FastAPI(title="Rate Limiter Demo")

app.add_middleware(RateLimitMiddleware, capacity=5, refill_rate=1.0)

@app.get("/ping")
async def ping():
    return {"message": "pong"}