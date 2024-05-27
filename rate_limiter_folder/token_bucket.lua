-- indexing start from 1
-- KEYS = [client_id]
-- ARGV = [current_time, refill_rate, limit]
local tokens = tonumber(redis.call("hget", KEYS[1], "tokens"))
local last_refill_time = tonumber(redis.call("hget", KEYS[1], "timestamp"))
local current_time = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

if not tokens then -- new client
    tokens = limit
    last_refill_time = current_time
    redis.call("hset", KEYS[1], "tokens", tokens)
    redis.call("hset", KEYS[1], "timestamp", last_refill_time)
else -- refill tokens for a client based on the time passed since the last refill 
    local elapsed_time = current_time - last_refill_time
    local new_tokens = math.floor(elapsed_time / refill_rate)
    if new_tokens > 0 then
        tokens = math.min(tokens + new_tokens, limit) -- make sure tokens doesn't exceed bucket limit
        last_refill_time = current_time
        redis.call("hset", KEYS[1], "tokens", tokens)
        redis.call("hset", KEYS[1], "timestamp", last_refill_time)
    end
end

-- consume a token for the request
if tokens > 0 then
    redis.call("hset", KEYS[1], "tokens", tokens - 1)
    return tokens - 1
else
    return -1
end