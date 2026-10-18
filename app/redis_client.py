import redis.asyncio as redis

# redis_client = redis.from_url("redis://localhost:6379/0", decode_responses=True)


class RedisClient:
    def __init__(self, url: str = "redis://localhost:6380"):
        self.client = redis.from_url(url, decode_responses=True)
        self.token_bucket_script = None
    async def ping(self):
        return await self.client.ping()

    async def load_scripts(self):
        print("Loading Lua script...")
        with open("app/scripts/token_bucket.lua", "r") as f:
            lua_code = f.read()
        self.token_bucket_script = self.client.register_script(lua_code)
        print("Lua script loaded successfully!")