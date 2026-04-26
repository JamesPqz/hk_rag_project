import hashlib
from typing import Optional, Tuple, List

from backend.cache.redis_client import redis_client
from backend.utils.logger_handler import logger

CACHE_TTL = 7200

class QueryCache:
    @staticmethod
    def _get_key(question: str) -> str:
        return f"qa:{hashlib.md5(question.encode()).hexdigest()}"

    @staticmethod
    def get(question: str) -> Optional[Tuple[str, List[str]]]:
        key = QueryCache._get_key(question)
        data = redis_client.get(key)
        if data:
            logger.info(f"cache hit:{question[:30]}...")
            return data.get('answer'), data.get('sources',[])
        return None

    @staticmethod
    def set(question:str , answer:str, sources: List[str]):
        key = QueryCache._get_key(question)
        redis_client.set(key, {
            "answer": answer,
            "sources":sources
        }, ttl=CACHE_TTL)

    @staticmethod
    def invalidate_by_pattern(pattern: str):
        """批量删除缓存"""
        redis_client.delete_pattern(pattern)
        logger.info(f"Cache invalidated by pattern: {pattern}")
