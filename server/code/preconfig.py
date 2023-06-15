import redis
import json

class PreConfig:
    REDIS_HOST = 'redis'
    REDIS_PORT = 6379
    HEARTBEAT_TIMEOUT = 5

    def __init__(self):
        # Connect to Redis
        self.rc = redis.Redis(host=self.REDIS_HOST, port=self.REDIS_PORT)

        # Extract text values from Redis and convert to JSON objects
        config_value = self.rc.get('config')
        inventory_value = self.rc.get('inventory')
        deployment_value = self.rc.get('deployment')
        self.config = json.loads(config_value)
        self.inventory = json.loads(inventory_value)
        self.deployment = json.loads(deployment_value)