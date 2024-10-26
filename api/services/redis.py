import redis.asyncio as redis


class RedisService:
    
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self._connection = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)
    
    async def set(self, key, value):
        await self._connection.set(key, value)
    
    async def get(self, key) -> str:
        return await self._connection.get(key)
    
    async def flush(self):
        await self._connection.flushdb()
