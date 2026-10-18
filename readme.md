# Distributed Rate Limiter

A production-style API rate limiter built with FastAPI and Redis, supporting Token Bucket and Sliding Window algorithms with atomic, race-condition-safe request handling.

## Why this project?

Every public API needs protection from being overwhelmed — by abusive clients, buggy retry loops, or just too much legitimate traffic at once. This project implements rate limiting the way it's done in production systems: with shared, centralized state (Redis) and atomic operations (Lua scripts) so it works correctly even across multiple server instances.

## Features

- [x] Token bucket algorithm (allows controlled bursts)
- [ ] Sliding window algorithm (strict, precise limiting)
- [x] Per-IP and per-user identity-based limiting
- [x] Redis-backed shared state (works across multiple instances)
- [ ] Atomic Lua script operations (prevents race conditions)
- [ ] `Retry-After` and `X-RateLimit-*` response headers
- [ ] Dockerized (API + Redis via docker-compose)

## Tech stack

- **FastAPI** — web framework, middleware-based request interception
- **Redis** — centralized state store for rate-limit counters
- **Docker Compose** — containerized Redis for local development

## Architecture

```
Client
  |
  v
RateLimitMiddleware  -->  extracts identity (user ID or IP)
  |
  v
TokenBucket.allow_request()
  |
  |--> Redis: HGETALL bucket:<identity>   (read current tokens + last_refill)
  |--> calculate refill based on elapsed time
  |--> decide allow / deny
  `--> Redis: HSET bucket:<identity>      (write updated state)
  |
  v
allowed? --> No  --> 429 Too Many Requests
  |
  Yes
  v
Route handler (e.g. /ping) --> response + X-RateLimit-Remaining header
```

Every incoming request passes through `RateLimitMiddleware` before reaching any route. The middleware checks the client's identity (user ID or IP) against their token bucket stored in Redis, and either allows the request through or returns `429 Too Many Requests`.

## Why Redis?

An in-memory store (plain Python dict) only works for a single server process. In real deployments with multiple instances behind a load balancer, each instance would have its own disconnected view of a client's usage — a client could exceed the limit by N times across N instances. Redis acts as a single shared source of truth that every instance reads and writes to, so the limit is enforced correctly no matter how many instances are running. It also survives process restarts, where in-memory state would simply reset.

**Note:** the current Redis read (`HGETALL`) and write (`HSET`) are two separate commands, not one atomic operation. Under concurrent requests, this can allow more requests through than the configured limit (a classic check-then-act race condition). Phase 3 fixes this by moving the read-check-write logic into a single atomic Redis Lua script.

## Setup

### Prerequisites
- Python 3.10+
- Docker + Docker Compose

### Run Redis
```bash
docker-compose up -d
```

> If port 6379 is already in use on your machine (e.g. another local Redis install), change the host port mapping in docker-compose.yml (e.g. "6380:6379") and update the Redis URL in main.py accordingly.

### Install dependencies
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Run the API
```bash
uvicorn app.main:app --reload
```

API available at http://127.0.0.1:8000

## Testing

```bash
# Manual burst test (PowerShell)
1..8 | ForEach-Object { curl.exe -s -o NUL -w "%{http_code}`n" http://127.0.0.1:8000/ping }
```

Expect the first N requests (per configured capacity) to return 200, followed by 429 once the bucket is exhausted. Waiting a few seconds between batches should allow some requests through again as the bucket refills.

### Inspecting Redis state directly

```bash
docker exec -it redis-dev redis-cli
> KEYS *
> HGETALL bucket:ip:127.0.0.1
```

## Project structure

```
distributed-rate-limiter/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI app entrypoint
│   ├── middleware.py      # RateLimitMiddleware
│   ├── limiter.py         # TokenBucket (Redis-backed)
│   └── redis_client.py    # Redis connection wrapper
├── docker-compose.yml      # Redis service
├── requirements.txt
└── README.md
```

## Roadmap

- [x] Phase 1: In-memory token bucket (proof of concept)
- [x] Phase 2: Redis-backed state
- [ ] Phase 3: Atomic Lua scripts (race-condition safe) + sliding window
- [ ] Phase 4: Response headers, config via env vars
- [ ] Phase 5: Dockerize full app, CI, benchmarks