from app.redis_client import RedisClient
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from app.limiter import TokenBucket

# class RateLimitMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app, capacity: int = 10, refill_rate: float = 2.0):
#         super().__init__(app)
#         self.bucket = TokenBucket(capacity=capacity, refill_rate=refill_rate)

#     async def dispatch(self, request, call_next):
#         identity = self._get_identity(request)
#         allowed, remaining = self.bucket.allow_request(identity)

#         if not allowed:
#             return JSONResponse(
#                 status_code=429,
#                 content={"error": "Too Many Requests"},
#                 headers={"Retry-After": "1"}
#             )

#         response = await call_next(request)
#         response.headers["X-RateLimit-Remaining"] = str(int(remaining))
#         return response

#     def _get_identity(self, request):
#         user_id = request.headers.get("X-User-ID")
#         if user_id:
#             return f"user:{user_id}"
#         return f"ip:{request.client.host}"

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client: RedisClient, capacity: int = 10, refill_rate: float = 2.0):
        super().__init__(app)
        self.bucket = TokenBucket(redis_client, capacity=capacity, refill_rate=refill_rate)

    async def dispatch(self, request, call_next):
        identity = self._get_identity(request)
        allowed, remaining = await self.bucket.allow_request(identity)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"error": "Too Many Requests"},
                headers={"Retry-After": "1"}
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(int(remaining))
        return response

    def _get_identity(self, request):
        user_id = request.headers.get("X-User-ID")
        if user_id:
            return f"user:{user_id}"
        return f"ip:{request.client.host}"
