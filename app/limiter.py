import threading
import time

from app.redis_client import RedisClient


# class TokenBucket:
#     def __init__ (self, capacity:int , refill_rate:float):       #creation of object in class tokenbucket
#           """
#         capacity: max tokens bucket can hold
#         refill_rate: tokens added per second
#         """
#           self.capacity=capacity
#           self.refill_rate=refill_rate
#           self.buckets={}          # this used to store the data of each user in RAM 
#           """self.buckets = {
#             "user_101": {"tokens": 5},
#             "user_102": {"tokens": 8}
#         }"""
#           self.lock=threading.Lock()

class TokenBucket:
    def __init__(self, redis_client:RedisClient,refill_rate:int, capacity:int):
        self.redis_client = redis_client      # <- ab ye Redis se connection hai, dictionary nahi
        self.capacity=capacity
        self.refill_rate=refill_rate
        """
        self.buckets = {} poora hata diya. Ab koi Python dictionary state store nahi kar rahi. Iski jagah self.redis hai — jo ek network connection object hai jo tumhare Python process se bahar, Redis server (jo Docker container mein alag se chal raha hai, port 6379 pe) se baat karta hai.
        """


    # def allow_request(self, key: str, requested: int = 1) -> tuple[bool, float]:
    #     with self.lock: #is block ke andar jo bhi ho raha hai, wo atomic hai (koi aur thread interrupt nahi kar sakta).
    #         now = time.time()
    #         bucket = self.buckets.get(key)

    #         if bucket is None:
    #             bucket = {"tokens": self.capacity, "last_refill": now}
    #             self.buckets[key] = bucket

    #         # refill based on elapsed time
    #         elapsed = now - bucket["last_refill"]
    #         bucket["tokens"] = min(self.capacity, bucket["tokens"] + elapsed * self.refill_rate)
    #         bucket["last_refill"] = now

    #         if bucket["tokens"] >= requested:
    #             bucket["tokens"] -= requested
    #             return True, bucket["tokens"]
    #         return False, bucket["tokens"]
        
    """this code below was without lua script, now we are using lua script to avoid race condition and make it atomic. so this code is commented out.
    """
    # async def allow_request(self, key:str, requested:int=1)->tuple[bool ,float]:
    #     now = time.time()
    #     bucket_key=f"bucket:{key}"
    #     data= await self.redis.hgetall(bucket_key)


    #     if not data:
    #         # bucket does not exist, create it
    #         tokens=self.capacity
    #         last_refill=now
    #     else:
    #         tokens=float(data["tokens"])
    #         last_refill=float(data["last_refill"])

    #     elapsed= now - last_refill      # kitna time beeta purani req me 
    #     tokens= min(self.capacity, tokens+elapsed*self.refill_rate)     # find the token- minimum(capacity, ya new token generated) me se - 

    #     allowed=False
    #     if (tokens>= requested):
    #         tokens -= requested
    #         allowed= True

    #     await self.redis.hset(bucket_key, mapping={"tokens":tokens,"last_refill":now})
    #     await self.redis.expire(bucket_key,3600)

    #     return allowed, tokens

    



    async def allow_request(self, key: str, requested: int = 1) -> tuple[bool, float]:
        now = time.time()
        bucket_key = f"bucket:{key}"

        result = await self.redis_client.token_bucket_script(
            keys=[bucket_key],
            args=[self.capacity, self.refill_rate, now, requested]
        )

        allowed = bool(result[0])
        tokens = float(result[1])

        return allowed, tokens