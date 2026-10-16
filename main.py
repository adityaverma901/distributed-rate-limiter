from fastapi import FastAPI
from app.redis_client import redis_client

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "hello"}


@app.get("/test-redis")
async def test_redis():
    await redis_client.set("foo", "bar")
    val = await redis_client.get("foo")
    return {"value": val}