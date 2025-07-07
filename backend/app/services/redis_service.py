"""
Redis Service
Handles Redis connections and operations for caching and session management
"""

import json
from typing import Any, Optional
import redis.asyncio as redis
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class RedisService:
    """Redis service for caching and session management"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not connected")
            
            # Serialize value to JSON if it's not a string
            if not isinstance(value, str):
                value = json.dumps(value)
            
            result = await self.redis_client.set(key, value, ex=expire)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to set Redis key {key}: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not connected")
            
            value = await self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to deserialize JSON, fallback to string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            logger.error(f"Failed to get Redis key {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not connected")
            
            result = await self.redis_client.delete(key)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to delete Redis key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not connected")
            
            result = await self.redis_client.exists(key)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to check Redis key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a key's value in Redis"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not connected")
            
            result = await self.redis_client.incrby(key, amount)
            return result
            
        except Exception as e:
            logger.error(f"Failed to increment Redis key {key}: {e}")
            return None
    
    async def set_session(self, session_id: str, data: dict, expire: int = 3600) -> bool:
        """Set session data"""
        return await self.set(f"session:{session_id}", data, expire)
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        return await self.get(f"session:{session_id}")
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session data"""
        return await self.delete(f"session:{session_id}")


# Global Redis service instance
redis_service = RedisService()
