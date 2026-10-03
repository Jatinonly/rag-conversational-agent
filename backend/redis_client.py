import redis

# Create a Python Redis client object that communicates with the Redis server running on this computer at port 6379,
# and return text responses as normal Python strings.
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)
