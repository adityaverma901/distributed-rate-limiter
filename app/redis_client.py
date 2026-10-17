import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost:6379/0", decode_responses=True)


class RedisClient:
    def __init__(self,url:str=redis_client):
        self.client=url

    async def ping(self):
        return await self.client.ping()