import redis.asyncio as redis

# redis_client = redis.from_url("redis://localhost:6379/0", decode_responses=True)


class RedisClient:
    def __init__(self, url: str = "redis://localhost:6380"):
        self.client = redis.from_url(url, decode_responses=True)

    async def ping(self):
        return await self.client.ping()