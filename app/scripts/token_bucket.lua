-- KEYS[1] = bucket key (e.g. "bucket:ip:127.0.0.1")
-- ARGV[1] = capacity
-- ARGV[2] = refill_rate (tokens per second)
-- ARGV[3] = now (current timestamp)
-- ARGV[4] = requested tokens
 


-- defining the params
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local bucket = redis.call("HMGET", KEYS[1], "tokens", "last_refill")       --fetching the buckets 
local tokens = tonumber(bucket[1])
local last_refill = tonumber(bucket[2])

if tokens == nil then
    tokens = capacity
    last_refill = now
end

local elapsed = now - last_refill
tokens = math.min(capacity, tokens + elapsed * refill_rate)

local allowed = 0
if tokens >= requested then
    tokens = tokens - requested
    allowed = 1
end

redis.call("HSET", KEYS[1], "tokens", tokens, "last_refill", now)
redis.call("EXPIRE", KEYS[1], 3600)

return {allowed, tokens}