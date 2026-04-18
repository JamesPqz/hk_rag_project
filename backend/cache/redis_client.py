import hashlib
import json
from typing import Optional, Any
import redis

from backend.utils.config_handler import redis_config as cfg

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host= cfg['redis_host'],
            port= cfg['redis_port'],
            decode_responses= True
        )

    def get(self, key:str) -> Optional[Any]:
        data = self.client.get(key)
        return json.loads(data) if data else None

    def set(self, key:str, value: Any, ttl:int = 7200):
        self.client.setex(key, ttl, json.dumps(value))

    def delete_pattern(self, pattern: str):
        for key in self.client.scan_iter(pattern):
            self.client.delete(key)

    def cache_qa(self, question:str, answer: str):
        key = f"qa:{hashlib.md5(question.encode()).hexdigest()}"
        self.set(key, answer, ttl=7200)

    def get_cache_qa(self, question:str) -> Optional[dict]:
        key = f"qa:{hashlib.md5(question.encode()).hexdigest()}"
        return self.get(key)

    def cache_session(self, session_id: int, history:list, ttl:int = 3600):
        self.client.setex(f"session:{session_id}", ttl, json.dumps(history))

    def get_session(self, session_id: int) -> Optional[list]:
        data = self.client.get(f"session:{session_id}")
        return json.loads(data) if data else []

redis_client = RedisClient()
