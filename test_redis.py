from redis import Redis

cache = Redis(db = 1, decode_responses = True)

# Set key, value pair without expiry
cache.set("access_key", 1)

# Set key, value pair with expiry
cache.setex("access_key_expiry", 60, 2)

# Retrieve value
print(cache.get("access_key")) # 1
print(cache.get("access_key_expiry")) # 2
print(cache.get("I dont exist")) # None

# Retrieve key, value ttl
print(cache.ttl("access_key")) # -1
print(cache.ttl("access_key_expiry")) # 60
print(cache.ttl("I dont exist")) # -2

# Set key, value expiry
cache.expire("access_key", 30)
print(cache.ttl("access_key")) # 30

# Retrieve value and set expiry
print(cache.getex("access_key_expiry", 120)) # 2
print(cache.ttl("access_key_expiry")) # 120

# Retrieve value and remove key
print(cache.getdel("access_key_expiry")) # 2
print(cache.get("access_key_expiry")) # None

# Remove key, value
cache.delete("access_key")
print(cache.get("access_key")) # None

# Set dictionary as value
cache.hset("config", mapping = {"model": "llama4"})

# Retrieve dict value
print(cache.hgetall("config")) # {"model": "llama4"}

# Retrieve ttl
print(cache.ttl("config")) # -1