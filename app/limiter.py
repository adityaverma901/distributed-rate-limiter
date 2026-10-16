import threading
import time


class TokenBucket:
    def __init__ (self, capacity:int , refill_rate:float):       #creation of object in class tokenbucket
          """
        capacity: max tokens bucket can hold
        refill_rate: tokens added per second
        """
          self.capacity=capacity
          self.refill_rate=refill_rate
          self.bucket={}         
          """self.buckets = {
            "user_101": {"tokens": 5},
            "user_102": {"tokens": 8}
        }"""
          self.lock=threading.lock()

    def allow_request(self, key: str, requested: int = 1) -> tuple[bool, float]:
        with self.lock: #is block ke andar jo bhi ho raha hai, wo atomic hai (koi aur thread interrupt nahi kar sakta).
            now = time.time()
            bucket = self.buckets.get(key)

            if bucket is None:
                bucket = {"tokens": self.capacity, "last_refill": now}
                self.buckets[key] = bucket

            # refill based on elapsed time
            elapsed = now - bucket["last_refill"]
            bucket["tokens"] = min(self.capacity, bucket["tokens"] + elapsed * self.refill_rate)
            bucket["last_refill"] = now

            if bucket["tokens"] >= requested:
                bucket["tokens"] -= requested
                return True, bucket["tokens"]
            return False, bucket["tokens"]
        

